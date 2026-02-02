import os
import sys
import io

# Try to import cairosvg, handle missing system dependencies gracefully
try:
    import cairosvg
    from PIL import Image
except ImportError as e:
    print(f"Error: Missing Python dependency. {e}")
    print("Please run: pip install cairosvg Pillow")
    sys.exit(1)
except OSError as e:
    # This block catches the DLL load error on Windows
    print("Error: System graphics library (Cairo) not found.")
    print("-" * 50)
    if os.name == 'nt':  # Windows
        print("ON WINDOWS:")
        print("1. You need the GTK+ Runtime.")
        print("2. Download latest release from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases")
        print("3. Install it and ensure 'Add to PATH' is checked.")
        print("4. Restart your terminal.")
    else:  # Linux/Mac
        print("ON LINUX (GitHub Actions):")
        print("Run: sudo apt-get install libcairo2")
    print("-" * 50)
    print(f"Original Error: {e}")
    sys.exit(1)

def convert_svgs():
    # Define paths relative to this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    input_dir = os.path.normpath(os.path.join(project_root, 'factory'))
    output_dir = os.path.normpath(os.path.join(input_dir, 'png'))

    # Ensure input directory exists
    if not os.path.exists(input_dir):
        print(f"Error: Input directory {input_dir} does not exist.")
        return

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    print(f"Input:  {input_dir}")
    print(f"Output: {output_dir}")

    # Process files
    count = 0
    files = [f for f in os.listdir(input_dir) if f.lower().endswith('.svg')]
    
    if not files:
        print("No SVG files found.")
        return

    for filename in files:
        input_path = os.path.join(input_dir, filename)
        output_filename = os.path.splitext(filename)[0] + '.png'
        output_path = os.path.join(output_dir, output_filename)
        
        print(f"Processing: {filename}...", end=" ", flush=True)

        try:
            # 1. Convert SVG to 160x160 PNG bytes using CairoSVG
            # This preserves aspect ratio if we don't force both dimensions, 
            # but here we set output_width/height which might scale/crop.
            # Ideally for icons we want 'fit to box'. 
            # CairoSVG's output_width/height scales the SVG to fit that box.
            png_data = cairosvg.svg2png(url=input_path, output_width=160, output_height=160)
            
            if not png_data:
                print("[Failed] Empty output")
                continue

            # 2. Load into PIL
            foreground = Image.open(io.BytesIO(png_data))
            
            # 3. Create 204x204 Transparent Background
            background = Image.new('RGBA', (204, 204), (0, 0, 0, 0))
            
            # 4. Center the 160x160 image
            # (204 - 160) // 2 = 22 pixel padding
            bg_w, bg_h = background.size
            fg_w, fg_h = foreground.size
            offset = ((bg_w - fg_w) // 2, (bg_h - fg_h) // 2)
            
            # 5. Composite
            background.paste(foreground, offset, foreground if foreground.mode == 'RGBA' else None)
            
            # 6. Save
            background.save(output_path)
            print("[OK]")
            count += 1

        except Exception as e:
            print(f"\nError processing {filename}: {e}")
            # If it's the DLL error again inside the loop (unlikely if import passed)
            if "cairo" in str(e).lower():
                print("Hint: Check GTK+ Runtime installation.")
                break

    print(f"\nDone. Processed {count} files.")

if __name__ == "__main__":
    convert_svgs()
