import requests
from bs4 import BeautifulSoup
import os
import re

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}

def search_filmgrab(movie_name):
    """
    Finds a movie URL on Film-Grab. Tries direct slug first, then site search.
    """
    # Clean up punctuation
    clean_name = movie_name.replace("’", "'").replace("“", '"').replace("”", '"').strip()
    
    # 1. Generate the predicted slug
    # This regex is cleaner: keeps only alphanumeric and replaces spaces with dashes
    slug = re.sub(r'[^a-z0-9\s-]', '', clean_name.lower())
    slug = re.sub(r'\s+', '-', slug)
    
    # Film-Grab uses /movies/ or /movie/. We check both or use search.
    urls_to_try = [
        f"https://film-grab.com/movies/{slug}/",
        f"https://film-grab.com/movie/{slug}/"
    ]
    
    for direct_url in urls_to_try:
        try:
            response = requests.get(direct_url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                return extract_metadata(response.text, direct_url, movie_name)
        except:
            continue

    # 2. FALLBACK: Use the site's internal search if direct URL fails
    # This is how we find 'House' (1977) if the slug is weird like /house-hausu/
    try:
        search_url = f"https://film-grab.com/?s={movie_name.replace(' ', '+')}"
        search_resp = requests.get(search_url, headers=HEADERS, timeout=15)
        search_soup = BeautifulSoup(search_resp.text, 'html.parser')
        
        # Grab the first search result link
        first_article = search_soup.find('article')
        if first_article:
            link_tag = first_article.find('a')
            if link_tag:
                new_url = link_tag['href']
                # Check if the search result is actually a close match
                if movie_name.lower() in link_tag.get_text().lower():
                    resp = requests.get(new_url, headers=HEADERS)
                    return extract_metadata(resp.text, new_url, movie_name)
    except Exception as e:
        print(f"Search fallback error: {e}")

    return None

def extract_metadata(html, url, original_name):
    """Helper to pull director, year, and title from a known page."""
    soup = BeautifulSoup(html, 'html.parser')
    
    # 1. Title from <h1>
    title_tag = soup.find('h1', class_='entry-title')
    matched_title = title_tag.get_text().strip() if title_tag else original_name.title()

    scraped_director = "Unknown Director"
    scraped_year = "Undated"

    # 2. Extract Metadata from content
    meta_block = soup.find('div', class_='entry-content')
    if meta_block:
        full_text = meta_block.get_text()
        
        # Improved Director Regex
        dir_match = re.search(r"(?:Director|Directed by)\s*[:\-]?\s*([^\•\–\n\r\.]+)", full_text, re.IGNORECASE)
        if dir_match:
            scraped_director = dir_match.group(1).strip()
        
        # Improved Year Regex (Looks for 4 digits in a range)
        yr_match = re.search(r"\b(19\d{2}|20\d{2})\b", full_text)
        if yr_match:
            scraped_year = yr_match.group(1)

    return {
        "url": url, 
        "title": matched_title, 
        "director": scraped_director, 
        "year": scraped_year
    }

def download_film_stills(url, folder_name):
    """
    Downloads original high-resolution images.
    """
    save_path = os.path.join("movie_stills", folder_name)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
        
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Targeting specific containers for stills
        images = soup.select('.entry-content img, .bwg-container img, img[class*="bwg-main-img"]')
        
        count = 0
        seen_urls = set()
        
        for img in images:
            img_url = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            
            if img_url and 'http' in img_url:
                # STRIP RESIZING: Remove dimensions like -1024x576 or -scaled
                clean_url = re.sub(r'-\d+x\d+', '', img_url)
                clean_url = clean_url.replace('-scaled', '').split('?')[0]
                
                if clean_url in seen_urls: continue
                seen_urls.add(clean_url)

                try:
                    img_data = requests.get(clean_url, headers=HEADERS, timeout=20).content
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