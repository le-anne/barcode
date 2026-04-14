import tmdbsimple as tmdb

# Paste your API Read Access Token here
tmdb.API_KEY = '6b232b899bbfdd2d115ecd5f80e73424'

def get_movie_variants(title, year=None):
    search = tmdb.Search()
    response = search.movie(query=title, year=year)
    
    variants = []
    if search.results:
        # Get the top result
        movie = search.results[0]
        variants.append(movie['title'])           # English Title
        variants.append(movie['original_title'])  # Original Language Title (e.g., Hausu)
        
        # Get even more titles (alternative titles)
        m = tmdb.Movies(movie['id'])
        alt_titles = m.alternative_titles()
        for alt in alt_titles.get('titles', []):
            variants.append(alt['title'])
            
    return list(set(variants)) # Remove duplicates