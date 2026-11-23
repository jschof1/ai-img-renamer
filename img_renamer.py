#!/usr/bin/env python3
"""
AI Image Renamer CLI
Analyzes images using Google Gemini and renames them based on content.
"""

import argparse
import base64
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types


def load_api_key() -> str:
    """Load GEMINI_API_KEY from .env file or environment variable."""
    # Load from current working directory
    cwd = os.getcwd()
    env_path = os.path.join(cwd, ".env")
    
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        load_dotenv()  # Fallback to default behavior
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found.")
        print("\nPlease set your API key using one of these methods:")
        print("  1. Create a .env file in the current directory with:")
        print("     GEMINI_API_KEY=your_api_key_here")
        print("  2. Set it as an environment variable:")
        print("     export GEMINI_API_KEY=your_api_key_here")
        print("\nGet your API key from: https://aistudio.google.com/app/apikey")
        sys.exit(1)
    
    return api_key


def get_image_files(folder_path: Path) -> list[Path]:
    """Scan directory for supported image files."""
    supported_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    image_files = []
    
    for ext in supported_extensions:
        image_files.extend(folder_path.glob(f"*{ext}"))
        image_files.extend(folder_path.glob(f"*{ext.upper()}"))
    
    # Remove duplicates and sort
    image_files = sorted(set(image_files))
    
    return image_files


def encode_image_to_base64(image_path: Path) -> str:
    """Read image file and convert to base64 string."""
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded


def analyze_image_with_gemini(
    image_path: Path,
    api_key: str
) -> Optional[str]:
    """Analyze image using Google Gemini and return suggested filename."""
    try:
        # Create client with the new SDK
        client = genai.Client(api_key=api_key)

        # Read and encode image
        base64_image = encode_image_to_base64(image_path)

        # Create prompt
        prompt = """Analyze this image and suggest a very short, descriptive filename.
Requirements:
- 3-6 words
- All lowercase
- Words separated by hyphens
- NO file extension
- Be descriptive but concise

Example output: 'vintage-red-sports-car-garage'"""

        # Determine mime type
        mime_type = f"image/{image_path.suffix.lstrip('.').replace('jpg', 'jpeg')}"

        # Generate content using new SDK format
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=[
                types.Part(text=prompt),
                types.Part(
                    inline_data=types.Blob(
                        mime_type=mime_type,
                        data=base64_image
                    )
                )
            ]
        )

        # Extract and clean the suggested filename
        suggestion = response.text.strip().lower()

        # Remove any file extension if the AI included one
        suggestion = suggestion.split(".")[0]

        # Remove any non-alphanumeric characters except hyphens
        import re
        suggestion = re.sub(r'[^a-z0-9-]', '-', suggestion)

        # Remove consecutive hyphens
        suggestion = re.sub(r'-+', '-', suggestion)

        # Remove leading/trailing hyphens
        suggestion = suggestion.strip('-')

        return suggestion

    except Exception as e:
        print(f"   ⚠️  Error analyzing {image_path.name}: {e}")
        return None


def generate_new_filename(
    original_path: Path,
    ai_suggestion: str,
    prefix: Optional[str],
    include_date: bool
) -> str:
    """Construct new filename based on parameters."""
    parts = []
    
    if prefix:
        parts.append(prefix)
    
    if include_date:
        today = datetime.now().strftime("%Y-%m-%d")
        parts.append(today)
    
    parts.append(ai_suggestion)
    
    # Join parts with hyphens
    base_name = "-".join(parts)
    
    # Get original extension (lowercase)
    extension = original_path.suffix.lower()
    
    return f"{base_name}{extension}"


def handle_duplicate_filename(
    folder_path: Path,
    proposed_name: str,
    original_extension: str
) -> str:
    """Check for duplicates and append index if necessary."""
    proposed_path = folder_path / proposed_name
    
    if not proposed_path.exists():
        return proposed_name
    
    # Extract base name without extension
    base_name = proposed_name[: -len(original_extension)]
    
    # Find next available index
    index = 1
    while True:
        indexed_name = f"{base_name}-{index:02d}{original_extension}"
        if not (folder_path / indexed_name).exists():
            return indexed_name
        index += 1


def rename_image(
    image_path: Path,
    new_name: str,
    dry_run: bool
) -> bool:
    """Rename the image file."""
    new_path = image_path.parent / new_name
    
    if dry_run:
        print(f"   → Would rename to: {new_name}")
        return True
    
    try:
        image_path.rename(new_path)
        print(f"   ✓ Renamed to: {new_name}")
        return True
    except Exception as e:
        print(f"   ✗ Failed to rename: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="AI-powered image renamer using Google Gemini",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ~/Pictures/vacation
  %(prog)s ./photos --prefix vacation --date --dry-run
  %(prog)s ./images --force --prefix gallery
        """
    )
    
    parser.add_argument(
        "folder",
        nargs="?",
        default=".",
        help="Target folder path (default: current directory)"
    )
    
    parser.add_argument(
        "--prefix",
        type=str,
        default=None,
        help="Optional string to prepend to the filename"
    )
    
    parser.add_argument(
        "--date",
        action="store_true",
        help="Prepend today's date (YYYY-MM-DD) to the filename"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show proposed renames without executing (default: true)"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Actually execute the rename (overrides --dry-run)"
    )
    
    args = parser.parse_args()
    
    # Determine if we should actually rename
    should_rename = args.force and not args.dry_run
    if args.force:
        should_rename = True
        args.dry_run = False
    
    # Resolve folder path
    folder_path = Path(args.folder).resolve()
    
    if not folder_path.exists():
        print(f"❌ Error: Folder not found: {folder_path}")
        sys.exit(1)
    
    if not folder_path.is_dir():
        print(f"❌ Error: Path is not a directory: {folder_path}")
        sys.exit(1)
    
    # Load API key
    print("🔑 Loading API key...")
    api_key = load_api_key()
    
    # Get image files
    print(f"📁 Scanning {folder_path} for images...")
    image_files = get_image_files(folder_path)
    
    if not image_files:
        print("⚠️  No supported image files found (.jpg, .jpeg, .png, .webp)")
        sys.exit(0)
    
    print(f"🖼️  Found {len(image_files)} image(s)\n")
    
    # Process each image
    mode = "DRY RUN (no changes will be made)" if args.dry_run else "LIVE MODE"
    print(f"⚙️  Operating in {mode}\n")
    
    success_count = 0
    
    for i, image_path in enumerate(image_files, 1):
        print(f"[{i}/{len(image_files)}] Analyzing: {image_path.name}")
        
        # Analyze image with Gemini
        suggestion = analyze_image_with_gemini(image_path, api_key)
        
        if not suggestion:
            print("   ✗ Skipped (analysis failed)\n")
            continue
        
        # Generate new filename
        new_name = generate_new_filename(
            image_path,
            suggestion,
            args.prefix,
            args.date
        )
        
        # Handle duplicates
        final_name = handle_duplicate_filename(
            folder_path,
            new_name,
            image_path.suffix.lower()
        )
        
        # Rename (or simulate)
        if rename_image(image_path, final_name, args.dry_run):
            success_count += 1
        
        print()
        
        # Rate limiting: 500ms delay between API calls
        if i < len(image_files):
            time.sleep(0.5)
    
    # Summary
    print(f"\n✅ {'Analysis' if args.dry_run else 'Renaming'} complete!")
    print(f"   Total images: {len(image_files)}")
    print(f"   Successful: {success_count}")
    
    if args.dry_run:
        print(f"\n💡 To actually rename files, run with --force flag")


if __name__ == "__main__":
    main()
