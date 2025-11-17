# Image to WebP Converter - Complete Usage Guide 🖼️

## 🎉 Updated! Now Supports GIF, JPG, and PNG

This script converts **GIF** (with animation!), **JPG/JPEG**, and **PNG** images to WebP format.

## 📦 Quick Setup

```bash
# Activate your environment
uv venv --python 3.12
source .venv/bin/activate

# Install dependency
uv pip install Pillow

# You're ready to go!
```

## 🚀 Basic Usage

### Convert Specific Image Types

```bash
# Convert only GIFs (preserves animation!)
python image_to_webp.py -i ./images -t gif -q 75

# Convert only JPGs
python image_to_webp.py -i ./images -t jpg -q 75

# Convert only PNGs
python image_to_webp.py -i ./images -t png -q 75

# Convert ALL image types (GIF + JPG + PNG)
python image_to_webp.py -i ./images -t all -q 75
```

### If `-t` is not specified, it defaults to `all`

```bash
# This converts all GIF, JPG, and PNG files
python image_to_webp.py -i ./images -q 75
```

## 📋 All Parameters

```
Required:
  -i, --input PATH          Input directory with images

Optional:
  -t, --type TYPE           Image type: gif, jpg, png, all (default: all)
  -o, --output PATH         Output directory (default: same as input)
  -q, --quality 0-100       Quality (default: 80)
  -l, --lossless           Lossless compression
  -m, --method 0-6         Compression method (default: 4)
  -r, --recursive          Process subdirectories
  -d, --delete-original    Delete originals after conversion
  --no-animation           Convert animated GIFs to static
```

## 🎯 Common Use Cases

### 1. Convert All Images with Good Compression

```bash
python image_to_webp.py -i ./images -t all -q 75 -m 6
```

### 2. Convert Only Photos (JPG)

```bash
python image_to_webp.py -i ./photos -t jpg -q 80
```

### 3. Convert Only Icons/Graphics (PNG)

```bash
python image_to_webp.py -i ./icons -t png -q 85
```

### 4. Convert Only Animated GIFs

```bash
python image_to_webp.py -i ./gifs -t gif -q 70 -m 6
```

### 5. Batch Convert Everything

```bash
# Process all subdirectories, all image types
python image_to_webp.py -i ./website_assets -t all -q 75 -r
```

### 6. High Quality Conversion

```bash
python image_to_webp.py -i ./images -t all -q 90 -m 5
```

### 7. Maximum Compression (Smaller Files)

```bash
python image_to_webp.py -i ./images -t all -q 60 -m 6
```

## 📊 Quality Recommendations by Image Type

### For JPG Photos

```bash
# Good balance (recommended)
python image_to_webp.py -i ./photos -t jpg -q 80

# Maximum compression
python image_to_webp.py -i ./photos -t jpg -q 70 -m 6

# High quality
python image_to_webp.py -i ./photos -t jpg -q 90
```

### For PNG Graphics/Icons

```bash
# Good balance
python image_to_webp.py -i ./icons -t png -q 85

# Lossless (if transparency is critical)
python image_to_webp.py -i ./icons -t png --lossless

# Compressed
python image_to_webp.py -i ./icons -t png -q 75
```

### For GIF Animations

```bash
# Balanced (recommended for your 10MB GIF issue)
python image_to_webp.py -i ./gifs -t gif -q 75 -m 6

# More compression (smaller files)
python image_to_webp.py -i ./gifs -t gif -q 65 -m 6

# Higher quality
python image_to_webp.py -i ./gifs -t gif -q 85 -m 5
```

## 🎬 Expected Output

```bash
$ python image_to_webp.py -i ./mixed_images -t all -q 75

Found 8 ALL file(s) to convert
Settings: quality=75, lossless=False, method=4, preserve_animation=True
Note: GIF animations will be preserved unless --no-animation is used

✓ Converted (animated gif): cat_dance.gif -> cat_dance.webp
  Size: 10,456,789 bytes -> 2,678,901 bytes (-74.4% change)
✓ Converted (jpg): photo.jpg -> photo.webp
  Size: 2,345,678 bytes -> 456,789 bytes (-80.5% change)
✓ Converted (png): icon.png -> icon.webp
  Size: 123,456 bytes -> 34,567 bytes (-72.0% change)
✓ Converted (gif): logo.gif -> logo.webp
  Size: 45,234 bytes -> 12,456 bytes (-72.5% change)

============================================================
Conversion complete!
Success: 4 (Animated: 1, Static: 3)
Errors: 0
============================================================
```

## 🔍 Understanding File Size Results

### Good Results (File Size Reduced)

- Animated GIF: 60-80% reduction typical
- JPG photos: 70-85% reduction typical
- PNG graphics: 50-75% reduction typical

### Bad Results (File Size Increased)

- Using `--lossless` flag ❌
- Quality too high (95-100) ❌
- Original already well-compressed ⚠️

## 📁 Organize by Type

### Convert Different Types to Different Folders

```bash
# GIFs to one folder
python image_to_webp.py -i ./images -t gif -o ./webp/gifs -q 75

# JPGs to another
python image_to_webp.py -i ./images -t jpg -o ./webp/photos -q 80

# PNGs to another
python image_to_webp.py -i ./images -t png -o ./webp/graphics -q 85
```

## 🆘 Common Issues

### "No GIF/JPG/PNG files found"

- Check the directory path
- Verify file extensions (.gif, .jpg, .jpeg, .png)
- Try `-r` for subdirectories

### File size increased instead of decreased

- Remove `--lossless` flag
- Lower quality: `-q 70` or `-q 65`
- Increase method: `-m 6`

### Quality is too low

- Increase quality: `-q 85` or `-q 90`
- Use method 5 instead of 6: `-m 5`
- For perfect quality: `--lossless` (larger files)

## 🎯 Quick Reference Table

| Image Type              | Recommended Quality | Method | Expected Reduction |
| ----------------------- | ------------------- | ------ | ------------------ |
| GIF (animated)          | 70-80               | 6      | 60-80%             |
| JPG (photos)            | 75-85               | 4-6    | 70-85%             |
| PNG (graphics)          | 80-90               | 4-5    | 50-75%             |
| PNG (with transparency) | 85 or lossless      | 4      | 50-70%             |

## 🚀 Complete Workflow Example

```bash
# 1. Test on a few files first
python image_to_webp.py -i ./test_folder -t all -q 75 -m 6

# 2. Check the results (file sizes and quality)

# 3. If good, process all files
python image_to_webp.py -i ./all_images -t all -q 75 -m 6 -r

# 4. Verify everything looks good

# 5. Optionally delete originals (be careful!)
python image_to_webp.py -i ./all_images -t all -q 75 -m 6 -r -d
```
