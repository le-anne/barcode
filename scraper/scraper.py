import requests
from bs4 import BeautifulSoup
import os
import re

def search_filmgrab(movie_name):
    """
    Finds a movie URL on Film-Grab and extracts clean Title, Director, and Year.
    """
    # Clean up punctuation for the URL slug
    clean_name = movie_name.replace("’", "'").replace("“", '"').replace("”", '"')
    
    # Predict the URL slug (e.g., Moulin Rouge! -> moulin-rouge)
    slug = re.sub(r'[^a-z0-9\s-]', '', clean_name.lower()).replace(" ", "-")
    direct_url = f"https://film-grab.com/movies/{slug}/"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
    
    try:
        response = requests.get(direct_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. Extract Title from the <h1>
            title_tag = soup.find('h1', class_='entry-title')
            matched_title = title_tag.get_text().strip() if title_tag else movie_name.title()

            scraped_director = "Unknown Director"
            scraped_year = "Undated"

            # 2. Extract Metadata
            meta_block = soup.find('div', class_='entry-content')
            if meta_block:
                full_text = meta_block.get_text()
                
                # UPDATED DIRECTOR REGEX:
                # This now looks for "Director" OR "Directed by"
                # It captures everything until it hits a bullet (•), dash (–), or newline.
                dir_match = re.search(r"(?:Director|Directed by)\s*[:\-]?\s*([^\•\–\n\r\.]+)", full_text, re.IGNORECASE)
                if dir_match:
                    scraped_director = dir_match.group(1).strip()
                
                # YEAR REGEX:
                # Looks for the 4-digit year
                yr_match = re.search(r"(\d{4})", full_text)
                if yr_match:
                    scraped_year = yr_match.group(1)

            return {
                "url": direct_url, 
                "title": matched_title, 
                "director": scraped_director, 
                "year": scraped_year
            }
            
    except Exception as e:
        print(f"Scraper error: {e}")
        
    return None

def download_film_stills(url, folder_name):
    """
    Downloads high-resolution images from the identified Film-Grab page.
    """
    save_path = os.path.join("movie_stills", folder_name)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
        
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        response = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Target Film-Grab's specific image containers
        images = soup.select('img[class*="bwg-main-img"], .entry-content img, .bwg-container img')
        
        count = 0
        for img in images:
            img_url = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            
            if img_url and 'http' in img_url:
                # Strip resizing logic to get original high-res file
                clean_url = re.sub(r'-\d+x\d+', '', img_url).split('?')[0]
                
                try:
                    img_data = requests.get(clean_url, headers=headers, timeout=20).content
                    filename = f"still_{count:03d}.jpg"
                    
                    with open(os.path.join(save_path, filename), 'wb') as f:
                        f.write(img_data)
                    count += 1
                except:
                    continue
                    
        return count
    except Exception as e:
        print(f"Download error: {e}")
        return 0