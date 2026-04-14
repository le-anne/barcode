import os
from PIL import Image, ImageDraw, ImageFont

# Canvas size for Instagram Stories (9:16)
STORY_WIDTH = 1080
STORY_HEIGHT = 1920
BACKGROUND_COLOR = "#000000"
TITLE_COLOR = "#FFFFFF"
META_COLOR = "#D1D1D1"  # Muted off-white for a classier look

# Memory optimization: Cache loaded fonts
FONT_CACHE = {}

def get_cinematic_font(size=80, bold=False):
    """Loads a refined serif or geometric sans-serif for a cinematic feel."""
    cache_key = f"font_{size}_{bold}"
    if cache_key in FONT_CACHE:
        return FONT_CACHE[cache_key]

    # Priority list for "Intelligent/Classy" fonts available on most systems
    font_names = [
        "/System/Library/Fonts/Times.ttc",                # Elegant Serif (Mac)
        "/System/Library/Fonts/HelveticaNeue.ttc",        # Clean Geometric (Mac)
        "/System/Library/Fonts/Optima.ttc",               # High-end Sans/Serif hybrid (Mac)
        "C:\\Windows\\Fonts\\georgiab.ttf",               # Strong Serif (Windows)
        "/usr/share/fonts/truetype/liberation/Serif.ttf"  # Linux fallback
    ]
    
    for font_path in font_names:
        if os.path.exists(font_path):
            try:
                # Use index=1 for .ttc files to often get the 'Bold' or 'Regular' variant
                font = ImageFont.truetype(font_path, size, index=0)
                FONT_CACHE[cache_key] = font
                return font
            except:
                continue
            
    # Absolute fallback
    font = ImageFont.load_default()
    FONT_CACHE[cache_key] = font
    return font

def draw_centered_spaced_text(draw, text, y_pos, font, spacing=10, color="#FFFFFF"):
    """
    Draws text with custom letter spacing (tracking) and centers it.
    This is a hallmark of cinematic title design.
    """
    # Create spaced text (e.g., M O U L I N)
    spaced_text = " ".join(list(text.upper())) if spacing > 0 else text.upper()
    
    try:
        # Pillow >= 9.2.0
        text_w = draw.textlength(spaced_text, font=font)
    except AttributeError:
        # Pillow < 9.2.0
        text_w, _ = draw.textsize(spaced_text, font=font)
    
    x = (STORY_WIDTH - text_w) / 2
    draw.text((x, y_pos), spaced_text, fill=color, font=font)

def generate_instagram_story(movie_title, year, director, colors, output_path):
    """Generates a high-res 9:16 JPG with tracked titles and muted metadata."""
    try:
        story = Image.new("RGB", (STORY_WIDTH, STORY_HEIGHT), BACKGROUND_COLOR)
        draw = ImageDraw.Draw(story)
        
        # Setup Refined Fonts
        title_font = get_cinematic_font(75)  # Slightly smaller title for more "air"
        meta_font = get_cinematic_font(40)   # Smaller metadata is more sophisticated

        # --- Barcode Logic ---
        barcode_y_end = 1450  # Give the text more room to breathe
        
        if colors:
            bar_width = STORY_WIDTH / len(colors)
            for i, color in enumerate(colors):
                draw.rectangle([i*bar_width, 0, (i+1)*bar_width, barcode_y_end], fill=color)
        
        # --- Metadata Logic (Centered & Classy) ---
        # Position text in the bottom black third
        text_area_center = barcode_y_end + ((STORY_HEIGHT - barcode_y_end) / 2)
        title_y = text_area_center - 80
        meta_y = text_area_center + 40

        # Draw Title with wide tracking
        draw_centered_spaced_text(draw, movie_title, title_y, title_font, spacing=15, color=TITLE_COLOR)
        
        # Draw Director / Year with tighter tracking and muted color
        meta_text = f"DIRECTED BY {director} • {year}"
        draw_centered_spaced_text(draw, meta_text, meta_y, meta_font, spacing=2, color=META_COLOR)

        story.save(output_path, "JPEG", quality=95)
        return True
    except Exception as e:
        print(f"Story Gen Error: {e}")
        return False

def generate_master_graphic(movie_title, year, director, colors, output_path):
    """Horizontal high-res barcode (Legacy support for the app)."""
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
    except:
        return False