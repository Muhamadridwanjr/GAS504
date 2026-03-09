import os

class StyleManager:
    def get_style(self, style_name: str):
        styles = {
            "scalping": {"tf1": "H4", "tf2": "H1", "tf3": "M15", "tf4": "M5"},
            "intraday": {"tf1": "D1", "tf2": "H4", "tf3": "H1", "tf4": "M15"},
            "swing": {"tf1": "W1", "tf2": "D1", "tf3": "H4", "tf4": "H1"}
        }
        return styles.get(style_name.lower(), styles["intraday"])
