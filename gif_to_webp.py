#!/usr/bin/env python3
"""
GIF to WebP Converter with Animation Support
Converts GIF images (static and animated) to WebP format
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Tuple
from PIL import Image


def find_gif_files(input_dir: Path, recursive: bool = False) -> List[Path]:
    """Find all GIF files in the directory."""
    gif_files = []

    if recursive:
        gif_files = list(input_dir.rglob("*.gif")) + list(input_dir.rglob("*.GIF"))
    else:
        gif_files = list(input_dir.glob("*.gif")) + list(input_dir.glob("*.GIF"))

    return sorted(set(gif_files))


def is_animated_gif(img: Image.Image) -> bool:
    """Check if the GIF is animated (has multiple frames)."""
    try:
        img.seek(1)
        return True
    except EOFError:
        return False
    finally:
        img.seek(0)


def convert_gif_to_webp(
    input_path: Path,
    output_dir: Path,
    quality: int = 80,
    lossless: bool = False,
    method: int = 4,
    preserve_animation: bool = True,
) -> Tuple[Path, bool]:
    """
    Convert a GIF file to WebP format.

    Args:
        input_path: Path to input GIF file
        output_dir: Directory to save WebP file
        quality: Quality for lossy compression (0-100)
        lossless: Use lossless compression
        method: Compression method (0-6, higher is slower but smaller)
        preserve_animation: Keep animation if present

    Returns:
        Tuple of (output_path, is_animated)
    """
    # Generate output path
    output_path = output_dir / f"{input_path.stem}.webp"

    # Open the GIF
    with Image.open(input_path) as img:
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
            # Convert static GIF to static WebP
            # Convert to RGBA to preserve transparency
            img_rgba = img.convert("RGBA")
            img_rgba.save(
                output_path,
                format="WebP",
                quality=quality,
                lossless=lossless,
                method=method,
            )

        return output_path, is_animated


def main():
    parser = argparse.ArgumentParser(
        description="Convert GIF images to WebP format (preserves animation)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i ./images                          # Convert all GIFs
  %(prog)s -i ./images -q 90                    # High quality
  %(prog)s -i ./images -l                       # Lossless
  %(prog)s -i ./images -o ./webp                # Custom output
  %(prog)s -i ./images -r                       # Recursive
  %(prog)s -i ./images -q 85 -m 6               # High compression
  %(prog)s -i ./images --no-animation           # Static only
        """,
    )

    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        required=True,
        help="Input directory containing GIF files",
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
        help="Delete original GIF files after successful conversion",
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

    # Find all GIF files
    gif_files = find_gif_files(args.input, args.recursive)

    if not gif_files:
        print("No GIF files found in the specified directory.")
        return

    print(f"Found {len(gif_files)} GIF file(s) to convert")
    print(
        f"Settings: quality={args.quality}, lossless={args.lossless}, "
        f"method={args.method}, preserve_animation={not args.no_animation}"
    )
    print()

    success_count = 0
    error_count = 0
    animated_count = 0
    static_count = 0

    for gif_path in gif_files:
        try:
            output_path, is_animated = convert_gif_to_webp(
                gif_path,
                output_dir,
                quality=args.quality,
                lossless=args.lossless,
                method=args.method,
                preserve_animation=not args.no_animation,
            )

            anim_status = "animated" if is_animated else "static"
            print(f"✓ Converted ({anim_status}): {gif_path.name} -> {output_path.name}")

            success_count += 1
            if is_animated:
                animated_count += 1
            else:
                static_count += 1

            # Get file sizes for comparison
            original_size = gif_path.stat().st_size
            new_size = output_path.stat().st_size
            reduction = (1 - new_size / original_size) * 100
            print(
                f"  Size: {original_size:,} bytes -> {new_size:,} bytes "
                f"({reduction:+.1f}% change)"
            )

            if args.delete_original:
                try:
                    gif_path.unlink()
                    print("  Deleted original file")
                except Exception as e:
                    print(f"  Warning: Failed to delete original file: {e}")

        except Exception as e:
            print(f"✗ Failed to convert {gif_path.name}: {e}")
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
