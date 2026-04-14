import os
from PIL import Image, ImageDraw, ImageFont

# Canvas Constants
STORY_WIDTH = 1080
STORY_HEIGHT = 1920
BACKGROUND_COLOR = "#000000"
TITLE_COLOR = "#FFFFFF"
META_COLOR = "#A0A0A0" 

def get_cinematic_font(size=80):
    # This ensures we find cinematic_font.ttf regardless of where the script runs
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    local_ttf = os.path.join(base_dir, "cinematic_font.ttf")
    
    paths_to_check = [
        local_ttf,
        "cinematic_font.ttf",
        "../cinematic_font.ttf"
    ]
    
    for path in paths_to_check:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, int(size))
            except:
                continue
    
    # Linux system backups for Streamlit Cloud
    linux_fonts = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
    ]
    for path in linux_fonts:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    
    return ImageFont.load_default()

def draw_centered_spaced_text(draw, text, y_pos, font, spacing=10, color="#FFFFFF", wrap=False):
    words = text.upper().split()
    lines = []
    
    # Wrap logic for longer titles
    if wrap and len(words) > 3:
        mid = len(words) // 2
        lines.append(" ".join(words[:mid]))
        lines.append(" ".join(words[mid:]))
    else:
        lines.append(text.upper())

    current_y = y_pos
    for line in lines:
        # Add spacing between letters for that cinematic look
        spaced_text = " ".join(list(line))
        draw.text((STORY_WIDTH / 2, current_y), spaced_text, fill=color, font=font, anchor="mt")
        # Line spacing based on font size
        current_y += (font.size if hasattr(font, 'size') else 40) + 30 
    return current_y

def generate_instagram_story(movie_title, year, director, colors, output_path):
    try:
        story = Image.new("RGB", (STORY_WIDTH, STORY_HEIGHT), BACKGROUND_COLOR)
        draw = ImageDraw.Draw(story)
        
        # ADJUSTED SIZES (Goldilocks Zone)
        title_font = get_cinematic_font(110) 
        meta_font = get_cinematic_font(45)   
        barcode_y_end = 1450 
        
        # Draw Barcode
        if colors:
            bar_width = STORY_WIDTH / len(colors)
            for i, color in enumerate(colors):
                draw.rectangle([i*bar_width, 0, (i+1)*bar_width, barcode_y_end], fill=color)
        
        # Draw Title
        title_y = barcode_y_end + 100
        new_y = draw_centered_spaced_text(draw, movie_title, title_y, title_font, wrap=True)
        
        # Draw Metadata
        meta_y = new_y + 10
        meta_text = f"DIRECTED BY {director} • {year}"
        draw_centered_spaced_text(draw, meta_text, meta_y, meta_font, color=META_COLOR, spacing=4)

        story.save(output_path, "JPEG", quality=95)
        return True
    except Exception as e:
        print(f"Error generating story: {e}")
        return False

def generate_master_graphic(movie_title, year, director, colors, output_path):
    # Placeholder to keep app.py functional
    try:
        img = Image.new("RGB", (2400, 1200), BACKGROUND_COLOR)
        img.save(output_path, "JPEG")
        return True
    except: 
        return False