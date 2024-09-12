from rembg import remove
from PIL import Image, ImageDraw
import numpy as np
import io
import os

class WatermarkProcessor:
    def __init__(self, watermark_image_path):
        self.watermark_image_path = watermark_image_path
        self.watermark = Image.open(watermark_image_path).convert("RGBA")

    def remove_background(self, image_path):
        with open(image_path, 'rb') as i:
            input_image = i.read()
        output_image = remove(input_image)
        image = Image.open(io.BytesIO(output_image)).convert("RGBA")
        return image

    def add_white_background(self, image):
        white_bg = Image.new('RGBA', image.size, (255, 255, 255, 255))
        white_bg.paste(image, (0, 0), image)
        return white_bg

    def remove_specific_colors(self, image, colors_to_remove):
        # Convert the image to a NumPy array
        data = np.array(image)
        
        # Create a mask for the colors to be removed
        mask = np.zeros(data.shape[:2], dtype=bool)
        for color in colors_to_remove:
            mask |= np.all(data[:, :, :3] == color, axis=-1)
        
        # Apply the mask to make the specific colors transparent
        data[mask] = [255, 255, 255, 0]  # Make the masked area transparent
        
        # Convert the NumPy array back to an image
        return Image.fromarray(data, 'RGBA')

    def add_watermark_front(self, image):
        # Resize watermark to match the size of the image
        watermark = self.watermark.resize(image.size, Image.LANCZOS)

        # Create a new image with white background
        combined = Image.new('RGBA', image.size, (255, 255, 255, 255))

        # Paste the original image on the white background
        combined.paste(image, (0, 0), image)

        # Paste the watermark on top of the original image
        combined.paste(watermark, (0, 0), watermark)

        return combined.convert('RGB')

    def add_watermark_behind(self, image):
        # Resize watermark to match the size of the image
        watermark = self.watermark.resize(image.size, Image.LANCZOS)

        # Create a new image with white background
        combined = Image.new('RGBA', image.size, (255, 255, 255, 255))

        # Paste the watermark on the white background
        combined.paste(watermark, (0, 0), watermark)

        # Paste the original image on top of the watermark
        combined.paste(image, (0, 0), image)

        return combined.convert('RGB')

# Directory with images
input_dir = 'Whiskey'  # Update to the correct path if needed
output_dir_behind = 'output/'  # Update to the correct path if needed
output_dir_front = 'output2/'  # Update to the correct path if needed
watermark_image = 'watermark.png'  # Path to your watermark image

# Create output directories if they don't exist
if not os.path.exists(output_dir_behind):
    os.makedirs(output_dir_behind)

if not os.path.exists(output_dir_front):
    os.makedirs(output_dir_front)

# Create an instance of WatermarkProcessor
processor = WatermarkProcessor(watermark_image)

# Colors to remove (specified in RGB)
colors_to_remove = [(243, 244, 238), (236, 235, 235)]

# Process each image
for filename in os.listdir(input_dir):
    if filename.endswith(('.png', '.jpg', '.jpeg')):
        input_path = os.path.join(input_dir, filename)
        
        # Remove background
        foreground = processor.remove_background(input_path)
        
        # Remove specific colors
        cleaned_image = processor.remove_specific_colors(foreground, colors_to_remove)
        
        # Add white background
        img_with_bg = processor.add_white_background(cleaned_image)
        
        # Add watermark behind the image
        img_with_watermark_behind = processor.add_watermark_behind(img_with_bg)
        
        # Save output with watermark behind
        output_path_behind = os.path.join(output_dir_behind, filename)
        img_with_watermark_behind.save(output_path_behind)
        print(f"Saved with watermark behind: {output_path_behind}")
        
        # Add watermark in front of the image
        img_with_watermark_front = processor.add_watermark_front(img_with_bg)
        
        # Save output with watermark in front
        output_path_front = os.path.join(output_dir_front, filename)
        img_with_watermark_front.save(output_path_front)
        print(f"Saved with watermark in front: {output_path_front}")

print("Processing complete.")
