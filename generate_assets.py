import os
from PIL import Image, ImageDraw, ImageFont

def generate_avatar():
    os.makedirs("assets", exist_ok=True)

    # 1. Create a beautiful cyberpunk/retro badge
    img = Image.new("RGB", (512, 512), color=(15, 10, 25))
    draw = ImageDraw.Draw(img)

    # Outer neon glowing circles
    draw.ellipse([20, 20, 492, 492], outline=(0, 255, 200), width=6)
    draw.ellipse([30, 30, 482, 482], outline=(255, 0, 128), width=3)
    draw.ellipse([40, 40, 472, 472], outline=(0, 100, 255), width=2)

    # Draw grid/tech lines in background
    for i in range(80, 440, 40):
        draw.line([i, 80, i, 432], fill=(30, 20, 50), width=1)
        draw.line([80, i, 432, i], fill=(30, 20, 50), width=1)

    # Glowing hexagon
    draw.polygon([(256, 90), (400, 173), (400, 339), (256, 422), (112, 339), (112, 173)], outline=(0, 255, 200), width=4)

    # Terminal prompt look
    draw.text((256, 190), "[- SYSTEM STATUS -]", fill=(0, 255, 200), anchor="mm")
    draw.text((256, 256), "[ DECOMMISSIONED ]", fill=(255, 0, 128), anchor="mm")
    draw.text((256, 320), "NODE: 0x7F-LEGACY", fill=(255, 255, 255), anchor="mm")

    # Draw little decorative brackets
    draw.text((256, 390), "<< OFFLINE >>", fill=(0, 255, 200), anchor="mm")

    # 2. Add EXIF data containing the Stage 3 key
    exif_dict = img.getexif()
    # 270 corresponds to ImageDescription EXIF tag
    exif_dict[270] = "portal_key: legacy_handshake_99"

    # Save as JPEG with EXIF dictionary
    img.save("assets/avatar_source.jpg", "JPEG", exif=exif_dict)
    print("Successfully generated assets/avatar_source.jpg with EXIF portal key.")

if __name__ == "__main__":
    generate_avatar()
