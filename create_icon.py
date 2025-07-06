# create_icon.py
# Simple script to create a basic icon for the application

from PIL import Image, ImageDraw, ImageFont
import os

def create_app_icon():
    """Create a simple application icon"""
    # Icon sizes for Windows
    sizes = [16, 32, 48, 64, 128, 256]
    
    # Create the base image (256x256)
    size = 256
    img = Image.new('RGB', (size, size), '#2E86AB')  # Blue background
    draw = ImageDraw.Draw(img)
    
    # Draw envelope shape for email application
    margin = size // 8
    envelope_box = [margin, margin + 20, size - margin, size - margin - 20]
    
    # Envelope body
    draw.rectangle(envelope_box, fill='#F24236', outline='#A23B72', width=3)
    
    # Envelope flap
    center_x = size // 2
    flap_top = margin + 20
    flap_points = [
        (margin, flap_top),
        (center_x, margin + 60),
        (size - margin, flap_top),
        (margin, flap_top)
    ]
    draw.polygon(flap_points, fill='#F6AE2D', outline='#A23B72', width=3)
    
    # Add "M" for MessageHub
    try:
        # Try to use a system font
        font_size = size // 4
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Draw "M" in the center
    text = "M"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2 + 10
    
    draw.text((text_x, text_y), text, fill='white', font=font)
    
    # Save as ICO file with multiple sizes
    icon_images = []
    for icon_size in sizes:
        resized = img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
        icon_images.append(resized)
    
    # Save the icon
    icon_images[0].save(
        'icon.ico',
        format='ICO',
        sizes=[(s, s) for s in sizes],
        append_images=icon_images[1:]
    )
    
    # Also save a PNG version for other uses
    img.save('icon.png', 'PNG')
    
    print("Icon created successfully!")
    print("- icon.ico (for Windows executable)")
    print("- icon.png (for other uses)")

if __name__ == "__main__":
    try:
        create_app_icon()
    except ImportError:
        print("Error: PIL (Pillow) is required to create icons")
        print("Install it with: pip install Pillow")
    except Exception as e:
        print(f"Error creating icon: {e}")
        print("You can skip this step and use a custom icon file instead")
