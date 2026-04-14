import os
from PIL import Image, ImageDraw, ImageFont

# Canvas size for Instagram Stories (9:16)
STORY_WIDTH = 1080
STORY_HEIGHT = 1920
BACKGROUND_COLOR = "#000000"
TITLE_COLOR = "#FFFFFF"
META_COLOR = "#A0A0A0" 

# Memory optimization: Cache loaded fonts
FONT_CACHE = {}

def get_cinematic_font(size=80, bold=False):
    """Loads a refined serif or geometric sans-serif."""
    cache_key = f"font_{size}_{bold}"
    if cache_key in FONT_CACHE: return FONT_CACHE[cache_key]
    font_names = [
        "/System/Library/Fonts/Times.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/Optima.ttc",
        "C:\\Windows\\Fonts\\georgiab.ttf",
        "/usr/share/fonts/truetype/liberation/Serif.ttf"
    ]
    for font_path in font_names:
        if os.path.exists(font_path):
            try:
                font = ImageFont.truetype(font_path, size, index=0)
                FONT_CACHE[cache_key] = font
                return font
            except: continue
    return ImageFont.load_default()

def draw_centered_spaced_text(draw, text, y_pos, font, spacing=10, color="#FFFFFF", wrap=False):
    """Draws perfectly horizontal centered text using Middle-Top anchoring."""
    words = text.upper().split()
    lines = []
    
    # Wrap logic: Split into two lines if title is long
    if wrap and len(words) > 3:
        mid = len(words) // 2
        lines.append(" ".join(words[:mid]))
        lines.append(" ".join(words[mid:]))
    else:
        lines.append(text.upper())

    current_y = y_pos
    for line in lines:
        spaced_text = " ".join(list(line)) if spacing > 0 else line
        # anchor="mt" ensures horizontal center is at 540px
        draw.text((STORY_WIDTH / 2, current_y), spaced_text, fill=color, font=font, anchor="mt")
        current_y += font.size + 45 # Increased leading for better legibility

    return current_y

def generate_instagram_story(movie_title, year, director, colors, output_path):
    """Generates 9:16 JPG with much larger, iPhone-friendly text."""
    try:
        story = Image.new("RGB", (STORY_WIDTH, STORY_HEIGHT), BACKGROUND_COLOR)
        draw = ImageDraw.Draw(story)
        
        # BUMPED UP FONT SIZES
        title_font = get_cinematic_font(100) # Was 70
        meta_font = get_cinematic_font(45)   # Was 32
        barcode_y_end = 1500 
        
        if colors:
            bar_width = STORY_WIDTH / len(colors)
            for i, color in enumerate(colors):
                draw.rectangle([i*bar_width, 0, (i+1)*bar_width, barcode_y_end], fill=color)
        
        # START POSITION: Pushed slightly higher to accommodate larger text block
        title_y = barcode_y_end + 65
        
        # Draw Title
        new_y = draw_centered_spaced_text(draw, movie_title, title_y, title_font, spacing=10, color=TITLE_COLOR, wrap=True)
        
        # Draw Meta (Director info) - Tighter gap to Title
        meta_y = new_y + 35
        meta_text = f"DIRECTED BY {director} • {year}"
        draw_centered_spaced_text(draw, meta_text, meta_y, meta_font, spacing=3, color=META_COLOR)

        story.save(output_path, "JPEG", quality=95)
        return True
    except Exception as e:
        print(f"Story Gen Error: {e}")
        return False

def generate_master_graphic(movie_title, year, director, colors, output_path):
    """Horizontal high-res barcode."""
    try:
        width, height = 2400, 1200
        img = Image.new("RGB", (width, height), BACKGROUND_COLOR)
        draw = ImageDraw.Draw(img)
        font = get_cinematic_font(60)
        meta_text = f"{movie_title.upper()} ({year}) | DIRECTED BY {director.upper()}"
        draw.text((80, 80), meta_text, fill=TITLE_COLOR, font=font)
        if colors:
            bar_width = width / len(colors)
            for i, color in enumerate(colors):
                draw.rectangle([i*bar_width, 250, (i+1)*bar_width, 1100], fill=color)
        img.save(output_path, "JPEG", quality=95)
        return True
    except: return False