from frontend.imports import *
from frontend.theme.stylesheet import STYLESHEET

def _hex_to_rgb(hex_color: str, brightness: int = 1) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip('#')
    
    assert len(hex_color) == 6, f"Invalid color value: {"#" + hex_color}"
    
    brightness = brightness / 255
    
    assert 1 > brightness >= 0, f"Invalid brightness value: {int(brightness * 255)}"
    
    r = int(int(hex_color[0:2], 16) * brightness)
    g = int(int(hex_color[2:4], 16) * brightness)
    b = int(int(hex_color[4:6], 16) * brightness)
    
    return (r, g, b, 255)

def _rgb_to_hex(rgb_color: tuple[int, int, int]) -> str:
    color = "#"
    for index, num in enumerate(rgb_color):
        if index < 3:
            pass
        elif num == 255:
            continue
        
        if len(hex(num).lstrip("0x")) == 0:
            color += "00"
        elif len(hex(num).lstrip("0x")) == 1:
            color += "0"
        color += hex(num).lstrip("0x")
    
    return color


def _interpolate_brightness(color: str, brightness: int):
    return _rgb_to_hex(_hex_to_rgb(color, brightness) if color is not None else (255, 255, 255, 255 - brightness))


def get_disabled_color(color: str | None) -> str:
    return _interpolate_brightness(color, 100)

def get_hover_color(color: str | None) -> str:
    return _interpolate_brightness(color, 200)

def get_pressed_color(color: str | None) -> str:
    return _interpolate_brightness(color, 150)


class ThemeManager:
    def __init__(self):
        self.themes: dict[str, dict[str, dict[str, str] | str]] = {}
        self.general_themes = {}
        self.file_path_mappings = {}
        self.current_theme = None
        
        self.func_mappings = {
            "hover": get_hover_color,
            "pressed": get_pressed_color,
            "disabled": get_disabled_color
        }
    
    def _process_stylesheet_func_pointers(self, delimeter: str, stylesheet: str, palette: dict[str, str]):
        index = 0
        
        replacements = {}
        
        for _ in range(stylesheet.count(delimeter)):
            index = stylesheet.find(delimeter, index + 1, -1)
            
            start_index = stylesheet.rfind("{", 0, index)
            end_index = stylesheet.find("}", index, -1)
            
            text = stylesheet[start_index + 1: end_index]
            stripped_text = text.strip()
            
            function_key, palette_key = stripped_text.split(delimeter)
            
            replacements["{" + text + "}"] = str(self.func_mappings[function_key](palette[palette_key]))
        
        for init_text, rep_text in replacements.items():
            stylesheet = stylesheet.replace(init_text, rep_text)
        
        return stylesheet
    
    def add_theme(self, name: str, theme_dict: dict):
        """Add a theme directly from a dict"""
        self.themes[name] = theme_dict

    def load_theme_from_file(self, file_path: str, stylesheet: str):
        """Load theme from a JSON file"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Theme file not found: {file_path}")
        
        with open(file_path, 'r') as f:
            theme = json.load(f)
            general = theme["general"]
            
            self.general_themes[file_path] = theme
            
            for name1, theme_palette in theme["theme"].items():
                for name2, color_palette in theme["color"].items():
                    palette = deepcopy(theme_palette)
                    palette.update(color_palette)
                    palette.update(general)
                    
                    self.add_theme(f"{name1}-{name2}", {"palette": palette, "stylesheet": stylesheet})
                    self.file_path_mappings[f"{name1}-{name2}"] = file_path

    def apply_theme(self, app: QApplication, name: str):
        """Apply a stylesheet-only theme using values from JSON"""
        
        if name not in self.themes:
            raise ValueError(f"Theme '{name}' not loaded.")
        
        self.current_theme = name
        
        theme = self.themes[self.current_theme]
        
        stylesheet_template = theme.get("stylesheet")
        
        app.setStyleSheet(self.parse_stylesheet(stylesheet_template))
    
    def parse_stylesheet(self, stylesheet: str):
        assert self.current_theme is not None, "No theme has been set"
        
        palette_vars = self.themes[self.current_theme].get("palette")
        
        try:
            stylesheet = self._process_stylesheet_func_pointers("__", stylesheet, palette_vars)
            return stylesheet.format(**palette_vars)
        except KeyError as e:
            raise KeyError(f"Missing color value for: {e} on line {stylesheet[:stylesheet.find(str(e)) + 1].count("\n") + 1}")
    
    def get_current_theme(self) -> dict[str, dict[str, str] | str]:
        return self.themes.get(self.current_theme, None)
    
    def get_current_palette(self):
        return self.get_current_theme().get("palette")

    def get_theme_names(self):
        return list(self.themes.keys())

    def get(self):
        return self.general_themes[self.file_path_mappings[self.current_theme]]

THEME_MANAGER = ThemeManager()
THEME_MANAGER.load_theme_from_file("frontend/theme/theme.json", STYLESHEET)

