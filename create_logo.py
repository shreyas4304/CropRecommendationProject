from PIL import Image, ImageDraw, ImageFont
import os

def create_logo():
    # Create a new image with a white background
    width = 200
    height = 200
    image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)

    # Draw a green circle
    circle_color = (40, 167, 69)  # Bootstrap success color
    draw.ellipse((20, 20, 180, 180), fill=circle_color)

    # Draw a leaf shape
    leaf_color = (255, 255, 255)
    leaf_points = [
        (100, 40),  # Top
        (160, 100),  # Right
        (100, 160),  # Bottom
        (40, 100),   # Left
    ]
    draw.polygon(leaf_points, fill=leaf_color)

    # Draw a smaller circle in the center
    draw.ellipse((80, 80, 120, 120), fill=circle_color)

    # Add text
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()

    text = "SF"
    text_color = (255, 255, 255)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2
    draw.text((text_x, text_y), text, font=font, fill=text_color)

    # Create static directory if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')

    # Save the image
    image.save('static/logo.png', 'PNG')

if __name__ == '__main__':
    create_logo() 