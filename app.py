import streamlit as st
import os

# 1. Page Config - Wide layout allows us to use CSS to center specific content blocks
st.set_page_config(page_title="Movie Barcode Scraper", layout="wide")

# --- MOBILE-FIRST CENTERING & CLASSY UI CSS ---
css = """
<style>
    /* Global alignment and padding */
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    
    /* Center all headings and captions */
    h1, h2, h3, h4, .stCaption { text-align: center !important; }

    /* Center and constrain the width of the input area */
    div.stTextInput, div.stButton, div[data-testid="stForm"] {
        margin: auto !important;
        width: 100% !important;
        max-width: 600px !important;
    }
    
    /* Ensure all column content (IG Stories) is centered */
    div[data-testid="stHorizontalBlock"] > div {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    /* Center the stacked barcodes and buttons underneath */
    div[data-testid="stVerticalBlock"] > div > div > img {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    
    div.stDownloadButton {
        display: flex;
        justify-content: center;
    }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# --- 2. Imports & Session State ---
try:
    from scraper.scraper import download_film_stills, search_filmgrab
    from scraper.analyzer import generate_barcode_data, create_barcode_image
    from scraper.story_generator import generate_instagram_story, generate_master_graphic
except ImportError as e:
    st.error(f"Import Error: {e}")

if "current_movie" not in st.session_state:
    st.session_state.current_movie = None

# --- 3. Header & Inputs ---
st.title("Movie Barcode Scraper")
st.markdown("---")

movie_name = st.text_input("Enter Movie Title:", placeholder="e.g. Moulin Rouge")

c_meta1, c_meta2 = st.columns(2)
with c_meta1:
    ov_director = st.text_input("Director (Optional):")
with c_meta2:
    ov_year = st.text_input("Year (Optional):")

# --- 4. Processing Logic ---
if st.button("Start Scraper", use_container_width=True):
    if movie_name:
        with st.spinner("Analyzing cinematic data..."):
            scraped_data = search_filmgrab(movie_name)
            if scraped_data:
                final_year = ov_year if ov_year else scraped_data['year']
                final_dir = ov_director if ov_director else scraped_data['director']
                
                folder = f"{movie_name.lower().replace(' ', '_')}_{final_year}"
                count = download_film_stills(scraped_data['url'], folder)
                
                if count > 0:
                    colors = generate_barcode_data(folder)
                    path = os.path.join("movie_stills", folder)
                    
                    st.session_state.current_movie = {
                        "title": scraped_data['title'], "year": final_year, 
                        "director": final_dir, "folder": folder, 
                        "path": path, "colors": colors
                    }
                    
                    # Asset Generation: 65 Frames
                    c65 = colors[::2]
                    p_s65 = os.path.join(path, f"{folder}_story_65.jpg")
                    p_b65 = os.path.join(path, f"{folder}_barcode_65.png")
                    generate_instagram_story(scraped_data['title'], final_year, final_dir, c65, p_s65)
                    create_barcode_image(c65, p_b65)
                    
                    # Asset Generation: 130 Frames
                    p_s130 = os.path.join(path, f"{folder}_story_130.jpg")
                    p_b130 = os.path.join(path, f"{folder}_barcode_130.png")
                    generate_instagram_story(scraped_data['title'], final_year, final_dir, colors, p_s130)
                    create_barcode_image(colors, p_b130)
                    
                    st.balloons()

# --- 5. Display Results ---
if st.session_state.current_movie:
    m = st.session_state.current_movie
    st.divider()
    st.subheader(f"{m['title']} ({m['year']})")
    
    # Dual Instagram Stories (Side-by-Side)
    st.markdown("#### Instagram Story Images")
    c_story1, c_story2 = st.columns(2)
    
    s65_path = os.path.join(m['path'], f"{m['folder']}_story_65.jpg")
    s130_path = os.path.join(m['path'], f"{m['folder']}_story_130.jpg")

    with c_story1:
        if os.path.exists(s65_path):
            st.caption("Variant: 65 Frames")
            st.image(s65_path, width=380) # Slightly smaller for clean look
            with open(s65_path, "rb") as f:
                st.download_button("Download Story (65)", f, file_name="story_65.jpg", key="dl_s65")
    
    with c_story2:
        if os.path.exists(s130_path):
            st.caption("Variant: 130 Frames")
            st.image(s130_path, width=380)
            with open(s130_path, "rb") as f:
                st.download_button("Download Story (130)", f, file_name="story_130.jpg", key="dl_s130")

    st.divider()
    
    # Stacked Barcodes (Vertically stacked and 20% smaller)
    st.markdown("#### Movie Barcodes")
    b65_path = os.path.join(m['path'], f"{m['folder']}_barcode_65.png")
    b130_path = os.path.join(m['path'], f"{m['folder']}_barcode_130.png")

    if os.path.exists(b65_path):
        st.image(b65_path, caption="Barcode (65 Frames)", width=900) # Reduced display width
        with open(b65_path, "rb") as f:
            st.download_button("Download Barcode (65)", f, file_name="barcode_65.png", key="dl_b65")

    st.markdown("<br>", unsafe_allow_html=True) # Extra breathing room

    if os.path.exists(b130_path):
        st.image(b130_path, caption="Barcode (130 Frames)", width=900) # Reduced display width
        with open(b130_path, "rb") as f:
            st.download_button("Download Barcode (130)", f, file_name="barcode_130.png", key="dl_b130")