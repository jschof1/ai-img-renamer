# AI Image Renamer

AI-powered CLI tool that analyzes images using Google Gemini and renames them based on content.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

- 🤖 **AI-Powered**: Uses Google Gemini 2.5 Flash to analyze image content
- 🖼️ **Smart Renaming**: Generates descriptive filenames (3-6 words, lowercase, hyphen-separated)
- 📅 **Date Support**: Optionally prepend today's date to filenames
- 🏷️ **Custom Prefixes**: Add your own prefixes to organize files
- 🔒 **Safe by Default**: Dry-run mode shows changes before applying them
- 🚀 **Easy Install**: One command installation with pipx

## Quick Start

### Install

```bash
# Install with pipx (recommended - no environment issues)
pipx install git+https://github.com/jacksloan/ai-img-renamer.git

# Or install with pip
pip install git+https://github.com/jacksloan/ai-img-renamer.git
```

### Setup

1. Get a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

2. Set your API key:

   ```bash
   # Option A: Create .env file in the folder you'll be working in
   echo "GEMINI_API_KEY=your_key_here" > .env

   # Option B: Export as environment variable (add to ~/.zshrc or ~/.bash_profile)
   export GEMINI_API_KEY=your_key_here
   ```

### Usage

```bash
# Preview changes (dry run - default, no files changed)
ai-rename ~/Pictures/vacation

# Actually rename files
ai-rename ~/Pictures/vacation --force

# Add prefix and date
ai-rename ~/Pictures --prefix vacation --date --force

# See all options
ai-rename --help
```

### Examples

**Before:**

```
IMG_2024_001.jpg
DSC02394.png
IMG_9891.jpeg
```

**After running `ai-rename ~/Pictures --prefix vacation --date --force`:**

```
vacation-2024-02-09-sunset-over-ocean.jpg
vacation-2024-02-09-mountain-landscape.png
vacation-2024-02-09-family-dinner-table.jpeg
```

## Installation Options

### Option 1: pipx (Recommended)

```bash
# Install pipx if you don't have it
brew install pipx  # macOS
pipx ensurepath

# Install the tool
pipx install git+https://github.com/jacksloan/ai-img-renamer.git

# Upgrade when new versions are available
pipx upgrade ai-img-renamer
```

### Option 2: pip

```bash
pip install --user git+https://github.com/jacksloan/ai-img-renamer.git
```

### Option 3: Clone and Install Locally

```bash
git clone https://github.com/jacksloan/ai-img-renamer.git
cd ai-img-renamer
pipx install .  # or: pip install -e .
```

### Option 4: Run Without Installing

```bash
git clone https://github.com/jacksloan/ai-img-renamer.git
cd ai-img-renamer
python img_renamer.py ~/Pictures
```

## Command Reference

```
ai-rename [FOLDER] [OPTIONS]

Arguments:
  folder              Target folder path (default: current directory)

Options:
  --prefix <text>     String to prepend to filename
  --date              Prepend today's date (YYYY-MM-DD)
  --dry-run           Show proposed renames without executing (default: true)
  --force             Actually execute the rename
  -h, --help          Show help message
```

## How It Works

1. **Scan**: Finds all images (.jpg, .jpeg, .png, .webp) in the target folder
2. **Analyze**: Sends each image to Google Gemini with the prompt:
   > "Analyze this image and suggest a very short, descriptive filename. Requirements: 3-6 words, lowercase, words separated by hyphens, exclude file extensions."
3. **Rename**: Constructs new filename: `[prefix]-[date]-[ai-suggestion].[ext]`
4. **Handle Duplicates**: Automatically appends -01, -02, etc. if filename exists
5. **Rate Limit**: 500ms delay between API calls to avoid rate limits

## Requirements

- Python 3.8+
- Google Gemini API key (free tier available)
- Supported image formats: .jpg, .jpeg, .png, .webp

## Uninstall

```bash
pipx uninstall ai-img-renamer
```

## License

MIT License - see [LICENSE](LICENSE) file

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.
