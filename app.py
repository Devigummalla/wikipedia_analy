from flask import Flask, render_template, jsonify, request
import json
import os
import sys
import nltk
from wiki_category_analyzer import load_from_cache, analyze_category, ensure_dirs, download_nltk_data
from color_palette import get_color_palette, get_all_color_palettes

app = Flask(__name__)

@app.route('/')
def index():
    try:
        # Ensure directories exist and NLTK data is downloaded
        ensure_dirs()
        download_nltk_data()
        return render_template('index.html')
    except Exception as e:
        app.logger.error(f"Error initializing application: {str(e)}")
        return jsonify({'error': 'Failed to initialize application'}), 500

@app.route('/color-palettes', methods=['GET'])
def get_palettes():
    try:
        palettes = get_all_color_palettes()
        palette_data = {name: get_color_palette(name) for name in palettes}
        return jsonify(palette_data)
    except Exception as e:
        app.logger.error(f"Error getting color palettes: {str(e)}")
        return jsonify({'error': 'Failed to get color palettes'}), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        category = request.form.get('category')
        palette_name = request.form.get('palette', 'Default')
        
        if not category:
            return jsonify({'error': 'Category is required'}), 400
        
        # Try to load from cache first
        cached_data = load_from_cache(category)
        
        if cached_data is None:
            # If not in cache, run the analysis
            try:
                frequencies = analyze_category(category)
                if frequencies is None:
                    return jsonify({'error': 'Failed to analyze category'}), 500
                cached_data = frequencies
            except Exception as e:
                app.logger.error(f"Error analyzing category: {str(e)}")
                return jsonify({'error': f'Error analyzing category: {str(e)}'}), 500
        
        # Convert frequencies to the format expected by the word cloud
        word_list = [{'text': word, 'size': min(100, max(20, count / 2))} 
                    for word, count in cached_data.items()]
        
        # Sort by size (frequency) and take top 100 words
        word_list.sort(key=lambda x: x['size'], reverse=True)
        word_list = word_list[:100]
        
        # Get the color palette
        colors = get_color_palette(palette_name)
        
        return jsonify({
            'words': word_list,
            'colors': colors
        })
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

if __name__ == '__main__':
    # Set NLTK_DATA environment variable to our custom directory
    nltk_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nltk_data')
    os.environ['NLTK_DATA'] = nltk_data_dir
    
    # Initialize the application
    try:
        ensure_dirs()
        download_nltk_data()
        app.run(debug=True)
    except Exception as e:
        print(f"Failed to initialize application: {str(e)}")
        sys.exit(1)
