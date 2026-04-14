import os
from PIL import Image, ImageDraw

def get_dual_average_colors(image_path):
    """Slices the image in half to get two DNA points per still."""
    try:
        with Image.open(image_path) as img:
            img = img.convert('RGB')
            w, h = img.size
            
            # Left Half Average
            left = img.crop((0, 0, w // 2, h))
            left = left.resize((1, 1), resample=Image.Resampling.BILINEAR)
            l_r, l_g, l_b = left.getpixel((0, 0))
            
            # Right Half Average
            right = img.crop((w // 2, 0, w, h))
            right = right.resize((1, 1), resample=Image.Resampling.BILINEAR)
            r_r, r_g, r_b = right.getpixel((0, 0))
            
            return [f"#{l_r:02x}{l_g:02x}{l_b:02x}", f"#{r_r:02x}{r_g:02x}{r_b:02x}"]
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return ["#000000", "#000000"]

def generate_barcode_data(movie_folder):
    """Processes stills and returns a doubled list of hex colors."""
    base_dir = "movie_stills"
    full_path = os.path.join(base_dir, movie_folder)
    
    if not os.path.exists(full_path):
        return []

    files = sorted([f for f in os.listdir(full_path) if f.endswith('.jpg')])
    
    doubled_colors = []
    for file in files:
        pair = get_dual_average_colors(os.path.join(full_path, file))
        doubled_colors.extend(pair)
        
    return doubled_colors

def create_barcode_image(colors, output_path, width=2000, height=800):
    """Creates a physical PNG image of the movie barcode."""
    if not colors:
        return None
    
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)
    
    bar_width = width / len(colors)
    
    for i, color in enumerate(colors):
        left = i * bar_width
        right = (i + 1) * bar_width
        draw.rectangle([left, 0, right, height], fill=color)
    
    img.save(output_path, "PNG")
    return output_path