from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import os
from django.conf import settings

WATERMARK_PATH = os.path.join(settings.STATIC_ROOT, 'images', 'RO-JA.png')

def add_watermark(image_file):
    # Open the main image
    image = Image.open(image_file)
    
    # Convert main image to RGB if it's not
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    try:
        # Open and prepare watermark
        watermark = Image.open(WATERMARK_PATH)
        # Convert watermark to RGBA if it's not
        if watermark.mode != 'RGBA':
            watermark = watermark.convert('RGBA')
        
        # Calculate watermark size while maintaining aspect ratio
        watermark_ratio = watermark.width / watermark.height
        desired_width = int(image.width * 0.4)  # 20% of main image width
        new_height = int(desired_width / watermark_ratio)
        
        # Resize watermark maintaining aspect ratio
        watermark = watermark.resize((desired_width, new_height), Image.LANCZOS)
        
        # Create a new blank image with the same size as the original
        watermarked = Image.new('RGB', image.size, (0, 0, 0))
        
        # Paste the original image
        watermarked.paste(image, (0, 0))
        
        # Calculate position (bottom-right corner)
        position = (
            image.width - watermark.width - 10,
            image.height - watermark.height - 10
        )
        
        # Paste the watermark
        watermarked.paste(watermark, position, watermark)
        
    except Exception as e:
        print(f"Error applying watermark: {str(e)}")
        # If watermark fails, return original image
        watermarked = image
    
    # Save to BytesIO
    output = BytesIO()
    watermarked.save(output, format='JPEG', quality=95)
    output.seek(0)
    
    # Return as InMemoryUploadedFile
    return InMemoryUploadedFile(
        output,
        'ImageField',
        f"{os.path.splitext(image_file.name)[0]}_watermarked.jpg",
        'image/jpeg',
        output.tell(),
        None
    ) 