#!/usr/bin/env python3
"""
Image to WebP Converter with Animation Support
Converts GIF (with animation), JPG, and PNG images to WebP format
"""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple
from PIL import Image


def find_image_files(
    input_dir: Path, file_type: str = "all", recursive: bool = False
) -> List[Path]:
    """Find all image files of specified type in the directory."""
    image_files = []

    # Define extensions for each type
    extensions = {
        "gif": ["*.gif", "*.GIF"],
        "jpg": ["*.jpg", "*.JPG", "*.jpeg", "*.JPEG"],
        "png": ["*.png", "*.PNG"],
        "all": [
            "*.gif",
            "*.GIF",
            "*.jpg",
            "*.JPG",
            "*.jpeg",
            "*.JPEG",
            "*.png",
            "*.PNG",
        ],
    }

    # Get the extensions to search for
    search_extensions = extensions.get(file_type, extensions["all"])

    # Search for files
    if recursive:
        for ext in search_extensions:
            image_files.extend(input_dir.rglob(ext))
    else:
        for ext in search_extensions:
            image_files.extend(input_dir.glob(ext))

    return sorted(set(image_files))


def is_animated_gif(img: Image.Image) -> bool:
    """Check if the GIF is animated (has multiple frames)."""
    try:
        img.seek(1)
        return True
    except EOFError:
        return False
    finally:
        img.seek(0)


def convert_image_to_webp(
    input_path: Path,
    output_dir: Path,
    quality: int = 80,
    lossless: bool = False,
    method: int = 4,
    preserve_animation: bool = True,
) -> Tuple[Path, bool]:
    """
    Convert an image file to WebP format.

    Args:
        input_path: Path to input image file
        output_dir: Directory to save WebP file
        quality: Quality for lossy compression (0-100)
        lossless: Use lossless compression
        method: Compression method (0-6, higher is slower but smaller)
        preserve_animation: Keep animation if present (GIF only)

    Returns:
        Tuple of (output_path, is_animated)
    """
    # Generate output path
    output_path = output_dir / f"{input_path.stem}.webp"

    # Open the image
    with Image.open(input_path) as img:
        # Check if it's a GIF and if it's animated
        is_gif = input_path.suffix.lower() == ".gif"
        is_animated = False

        if is_gif:
            is_animated = is_animated_gif(img)

        if is_animated and preserve_animation:
            # Convert animated GIF to animated WebP
            frames = []
            durations = []

            try:
                while True:
                    # Convert frame to RGBA to preserve transparency
                    frame = img.convert("RGBA")
                    frames.append(frame.copy())

                    # Get frame duration (in milliseconds)
                    duration = img.info.get("duration", 100)
                    durations.append(duration)

                    img.seek(img.tell() + 1)
            except EOFError:
                pass  # End of frames

            # Save as animated WebP
            frames[0].save(
                output_path,
                format="WebP",
                save_all=True,
                append_images=frames[1:],
                duration=durations,
                loop=img.info.get("loop", 0),
                quality=quality,
                lossless=lossless,
                method=method,
            )
        else:
            # Convert static image to static WebP
            # Convert to RGBA to preserve transparency (for PNG/GIF)
            # For JPG, convert to RGB (no transparency)
            if img.mode in ("RGBA", "LA") or (
                img.mode == "P" and "transparency" in img.info
            ):
                img_converted = img.convert("RGBA")
            else:
                img_converted = img.convert("RGB")

            img_converted.save(
                output_path,
                format="WebP",
                quality=quality,
                lossless=lossless,
                method=method,
            )

        return output_path, is_animated


def main():
    parser = argparse.ArgumentParser(
        description="Convert images (GIF/JPG/PNG) to WebP format (preserves GIF animation)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i ./images -t gif                   # Convert only GIFs
  %(prog)s -i ./images -t jpg                   # Convert only JPGs
  %(prog)s -i ./images -t png                   # Convert only PNGs
  %(prog)s -i ./images -t all                   # Convert all formats
  %(prog)s -i ./images -t gif -q 90             # High quality GIFs
  %(prog)s -i ./images -t jpg -l                # Lossless JPGs
  %(prog)s -i ./images -t all -o ./webp         # All formats, custom output
  %(prog)s -i ./images -t png -r                # Recursive PNGs
  %(prog)s -i ./images -t gif -q 75 -m 6        # High compression GIFs
  %(prog)s -i ./images -t gif --no-animation    # Static GIFs only
        """,
    )

    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        required=True,
        help="Input directory containing image files",
    )

    parser.add_argument(
        "-t",
        "--type",
        type=str,
        default="all",
        choices=["gif", "jpg", "png", "all"],
        help="Image type to convert (default: all)",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output directory for WebP files (default: same as input)",
    )

    parser.add_argument(
        "-q",
        "--quality",
        type=int,
        default=80,
        help="Quality for lossy compression (0-100, default: 80)",
    )

    parser.add_argument(
        "-l", "--lossless", action="store_true", help="Use lossless compression"
    )

    parser.add_argument(
        "-m",
        "--method",
        type=int,
        default=4,
        choices=range(0, 7),
        help="Compression method (0-6, higher=slower but smaller, default: 4)",
    )

    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Process subdirectories recursively",
    )

    parser.add_argument(
        "-d",
        "--delete-original",
        action="store_true",
        help="Delete original image files after successful conversion",
    )

    parser.add_argument(
        "--no-animation",
        action="store_true",
        help="Convert animated GIFs to static WebP (first frame only)",
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.input.exists():
        print(f"Error: Input directory does not exist: {args.input}")
        sys.exit(1)

    if not args.input.is_dir():
        print(f"Error: Input path is not a directory: {args.input}")
        sys.exit(1)

    if args.quality < 0 or args.quality > 100:
        print("Error: Quality must be between 0 and 100")
        sys.exit(1)

    # Set output directory
    output_dir = args.output if args.output else args.input
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all image files of specified type
    image_files = find_image_files(args.input, args.type, args.recursive)

    if not image_files:
        print(f"No {args.type.upper()} files found in the specified directory.")
        return

    print(f"Found {len(image_files)} {args.type.upper()} file(s) to convert")
    print(
        f"Settings: quality={args.quality}, lossless={args.lossless}, "
        f"method={args.method}, preserve_animation={not args.no_animation}"
    )
    if args.type in ["gif", "all"]:
        print("Note: GIF animations will be preserved unless --no-animation is used")
    print()

    success_count = 0
    error_count = 0
    animated_count = 0
    static_count = 0

    for image_path in image_files:
        try:
            output_path, is_animated = convert_image_to_webp(
                image_path,
                output_dir,
                quality=args.quality,
                lossless=args.lossless,
                method=args.method,
                preserve_animation=not args.no_animation,
            )

            # Determine file type for display
            file_type = image_path.suffix.lower().lstrip(".")
            if file_type == "jpeg":
                file_type = "jpg"

            anim_status = f"animated {file_type}" if is_animated else file_type
            print(
                f"✓ Converted ({anim_status}): {image_path.name} -> {output_path.name}"
            )

            success_count += 1
            if is_animated:
                animated_count += 1
            else:
                static_count += 1

            # Get file sizes for comparison
            original_size = image_path.stat().st_size
            new_size = output_path.stat().st_size
            reduction = (1 - new_size / original_size) * 100
            print(
                f"  Size: {original_size:,} bytes -> {new_size:,} bytes "
                f"({reduction:+.1f}% change)"
            )

            if args.delete_original:
                try:
                    image_path.unlink()
                    print("  Deleted original file")
                except Exception as e:
                    print(f"  Warning: Failed to delete original file: {e}")

        except Exception as e:
            print(f"✗ Failed to convert {image_path.name}: {e}")
            error_count += 1

    print()
    print("=" * 60)
    print("Conversion complete!")
    print(
        f"Success: {success_count} (Animated: {animated_count}, Static: {static_count})"
    )
    print(f"Errors: {error_count}")
    print("=" * 60)


if __name__ == "__main__":
    main()
