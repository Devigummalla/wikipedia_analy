import sys
import json
import os
import requests
import nltk
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from datetime import datetime, timedelta
import pickle
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CACHE_DIR = "cache"
NLTK_DATA_DIR = "nltk_data"
CACHE_EXPIRY_DAYS = 7

def ensure_dirs():
    for directory in [CACHE_DIR, NLTK_DATA_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)

def get_cache_filename(category):
    # Create a safe filename from the category name
    safe_name = "".join(c if c.isalnum() else "_" for c in category)
    return os.path.join(CACHE_DIR, f"{safe_name}.json")

def get_nltk_cache_path(resource):
    return os.path.join(NLTK_DATA_DIR, f"{resource}.pickle")

def download_nltk_data():
    ensure_dirs()
    resources = ['punkt', 'stopwords']
    
    for resource in resources:
        cache_path = get_nltk_cache_path(resource)
        if os.path.exists(cache_path):
            # Load from local cache
            try:
                with open(cache_path, 'rb') as f:
                    nltk.data.load(cache_path)
                logger.info(f"Loaded {resource} from cache")
                continue
            except Exception as e:
                logger.warning(f"Failed to load {resource} from cache: {e}")
        
        try:
            # Try to download and cache
            nltk.download(resource, download_dir=NLTK_DATA_DIR, quiet=True)
            # Save to pickle for offline use
            if resource == 'stopwords':
                data = stopwords.words('english')
                with open(cache_path, 'wb') as f:
                    pickle.dump(data, f)
            elif resource == 'punkt':
                data = nltk.data.load('tokenizers/punkt/english.pickle')
                with open(cache_path, 'wb') as f:
                    pickle.dump(data, f)
            logger.info(f"Downloaded and cached {resource}")
        except Exception as e:
            logger.error(f"Failed to download {resource}: {e}")
            if not os.path.exists(cache_path):
                raise Exception(f"Could not load or download {resource}")

def load_from_cache(category):
    cache_file = get_cache_filename(category)
    if not os.path.exists(cache_file):
        return None
    
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
            
        # Check if cache is expired
        cache_date = datetime.fromisoformat(cache_data['timestamp'])
        if datetime.now() - cache_date > timedelta(days=CACHE_EXPIRY_DAYS):
            logger.info(f"Cache expired for category: {category}")
            return None
            
        logger.info(f"Loaded cache for category: {category}")
        return cache_data['frequencies']
    except Exception as e:
        logger.error(f"Failed to load cache: {e}")
        return None

def save_to_cache(category, frequencies):
    try:
        ensure_dirs()
        cache_file = get_cache_filename(category)
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'frequencies': {word: count for word, count in frequencies.items()}
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved cache for category: {category}")
    except Exception as e:
        logger.error(f"Failed to save cache: {e}")

def get_category_members(category):
    try:
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "list": "categorymembers",
            "cmtitle": f"Category:{category}",
            "cmlimit": "500"
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'error' in data:
            raise Exception(f"Wikipedia API error: {data['error'].get('info', 'Unknown error')}")
            
        if 'query' not in data or 'categorymembers' not in data['query']:
            raise Exception("Invalid response from Wikipedia API")
            
        members = [page['title'] for page in data['query']['categorymembers']]
        logger.info(f"Found {len(members)} pages in category: {category}")
        return members
    except Exception as e:
        logger.error(f"Error fetching category members: {e}")
        raise Exception(f"Failed to fetch category members: {str(e)}")

def get_page_content(title):
    try:
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "titles": title,
            "prop": "extracts",
            "explaintext": True
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'error' in data:
            raise Exception(f"Wikipedia API error: {data['error'].get('info', 'Unknown error')}")
            
        pages = data['query']['pages']
        page_id = list(pages.keys())[0]
        
        if page_id == '-1':
            logger.warning(f"Page not found: {title}")
            return ""
            
        content = pages[page_id].get('extract', '')
        logger.info(f"Retrieved content for page: {title}")
        return content
    except Exception as e:
        logger.error(f"Error fetching page content for {title}: {e}")
        return ""

def process_text(text):
    try:
        # Tokenize and convert to lowercase
        tokens = word_tokenize(text.lower())
        
        # Remove stopwords and non-alphabetic tokens
        stop_words = set(stopwords.words('english'))
        words = [word for word in tokens if word.isalpha() and word not in stop_words]
        
        return Counter(words)
    except Exception as e:
        logger.error(f"Error processing text: {e}")
        raise Exception(f"Failed to process text: {str(e)}")

def analyze_category(category_name):
    """
    Analyze a category and return the word frequencies.
    This function is used by both the CLI and web interface.
    """
    try:
        logger.info(f"Starting analysis for category: {category_name}")
        
        # Download required NLTK data
        download_nltk_data()
        
        # Get all pages in the category
        pages = get_category_members(category_name)
        if not pages:
            raise Exception("No pages found in category")
            
        # Process each page and accumulate word frequencies
        total_frequencies = Counter()
        for page_title in pages:
            logger.info(f"Processing page: {page_title}")
            content = get_page_content(page_title)
            if content:
                frequencies = process_text(content)
                total_frequencies.update(frequencies)
        
        if not total_frequencies:
            raise Exception("No content found in category pages")
        
        # Save results to cache
        save_to_cache(category_name, total_frequencies)
        
        return dict(total_frequencies)
    except Exception as e:
        logger.error(f"Error analyzing category: {e}")
        raise Exception(f"Failed to analyze category: {str(e)}")

def main(category=None):
    """
    Main function that can be called from both CLI and web interface
    """
    if category is None:
        if len(sys.argv) != 2:
            print("Usage: python wiki_category_analyzer.py <category_name>")
            sys.exit(1)
        category = sys.argv[1]
    
    print(f"Analyzing category: {category}")
    
    try:
        # Try to load from cache first
        cached_frequencies = load_from_cache(category)
        if cached_frequencies is not None:
            print("Using cached results (cached within the last 7 days)")
            print_results(cached_frequencies)
            return cached_frequencies
        
        # If not in cache, analyze the category
        frequencies = analyze_category(category)
        if frequencies:
            print_results(frequencies)
            return frequencies
            
    except Exception as e:
        print(f"Error: {e}")
        cached_frequencies = load_from_cache(category)
        if cached_frequencies is not None:
            print("\nFalling back to cached results:")
            print_results(cached_frequencies)
            return cached_frequencies
        else:
            print("No cached results available")
            sys.exit(1)

def print_results(frequencies):
    print("\nTop 100 most frequent non-common words across all pages:")
    print("\nRank  Word                  Frequency")
    print("-" * 45)
    
    for rank, (word, count) in enumerate(Counter(frequencies).most_common(100), 1):
        try:
            print(f"{rank:4d}  {word:20s} {count:8d}")
        except UnicodeEncodeError:
            continue

if __name__ == "__main__":
    main()
