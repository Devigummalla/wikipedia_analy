class CodePalette:
    def __init__(self, name, colors):
        self.name = name
        self.colors = colors

    def get_colors(self):
        return self.colors

class MaterialPalette(CodePalette):
    def __init__(self):
        super().__init__('Material', [
            '#f44336',  # Red
            '#e91e63',  # Pink
            '#9c27b0',  # Purple
            '#673ab7',  # Deep Purple
            '#3f51b5',  # Indigo
            '#2196f3',  # Blue
            '#03a9f4',  # Light Blue
            '#00bcd4',  # Cyan
            '#009688',  # Teal
            '#4caf50'   # Green
        ])

class SolarizedPalette(CodePalette):
    def __init__(self):
        super().__init__('Solarized', [
            '#002b36',  # Base03
            '#073642',  # Base02
            '#586e75',  # Base01
            '#657b83',  # Base00
            '#839496',  # Base0
            '#93a1a1',  # Base1
            '#eee8d5',  # Base2
            '#fdf6e3',  # Base3
            '#b58900',  # Yellow
            '#cb4b16'   # Orange
        ])

class DraculaPalette(CodePalette):
    def __init__(self):
        super().__init__('Dracula', [
            '#282a36',  # Background
            '#44475a',  # Current Line
            '#f8f8f2',  # Foreground
            '#6272a4',  # Comment
            '#8be9fd',  # Cyan
            '#50fa7b',  # Green
            '#ffb86c',  # Orange
            '#ff79c6',  # Pink
            '#bd93f9',  # Purple
            '#ff5555'   # Red
        ])

class MonokaiPalette(CodePalette):
    def __init__(self):
        super().__init__('Monokai', [
            '#272822',  # Background
            '#f8f8f2',  # Foreground
            '#f92672',  # Red
            '#fd971f',  # Orange
            '#e6db74',  # Yellow
            '#a6e22e',  # Green
            '#66d9ef'   # Blue
        ])

class RGBColorPalatte(CodePalette):
    def __init__(self):
        super().__init__('RGB', [
            '#ff0000',  # Red
            '#00ff00',  # Green
            '#0000ff'   # Blue
        ])

def get_all_color_palette():
    return {
        'material': MaterialPalette(),
        'solarized': SolarizedPalette(),
        'dracula': DraculaPalette(),
        'monokai': MonokaiPalette(),
        'rgb': RGBColorPalatte()
    }

def get_color_palette(name):
    """Get a specific color palette by name."""
    # First try to get from the class-based palettes
    class_palettes = get_all_color_palette()
    if name.lower() in class_palettes:
        return class_palettes[name.lower()].get_colors()

    # If not found, try the predefined palettes
    predefined_palettes = {
        'Default': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'],
        'Warm': ['#ff4d4d', '#ff8533', '#ffcc00', '#ff6666', '#ff944d', '#ffd633', '#ff8080', '#ffa366', '#ffe066'],
        'Cool': ['#4d4dff', '#33ccff', '#00ff99', '#6666ff', '#4dccff', '#33ffb3', '#8080ff', '#66ccff', '#66ffcc'],
        'Pastel': ['#ffb3b3', '#ffd9b3', '#ffffb3', '#b3ffb3', '#b3d9ff', '#e6b3ff', '#ffb3ff', '#ffb3d9', '#b3ffff'],
        'Dark': ['#1a1a1a', '#333333', '#4d4d4d', '#666666', '#808080', '#999999', '#b3b3b3', '#cccccc', '#e6e6e6'],
        'Rainbow': ['#ff0000', '#ff7f00', '#ffff00', '#00ff00', '#0000ff', '#4b0082', '#8f00ff', '#ff69b4', '#00ffff'],
        'Forest': ['#004d00', '#006600', '#008000', '#009900', '#00b300', '#00cc00', '#00e600', '#00ff00', '#33ff33'],
        'Ocean': ['#000066', '#000099', '#0000cc', '#0000ff', '#3333ff', '#6666ff', '#9999ff', '#ccccff', '#e6e6ff']
    }
    return predefined_palettes.get(name, predefined_palettes['Default'])

def get_all_color_palettes():
    """Get a list of all available color palette names."""
    # Combine class-based and predefined palettes
    class_palettes = [p.name for p in get_all_color_palette().values()]
    predefined_palettes = ['Default', 'Warm', 'Cool', 'Pastel', 'Dark', 'Rainbow', 'Forest', 'Ocean']
    return sorted(class_palettes + predefined_palettes)