from typing import Any
import pathlib
import json


class ConfigLoader:
    def __init__(self, config_path: str):
        current_dir = pathlib.Path(__file__).parent
        self.config_path = f"{current_dir}\\{config_path}"

    def load_config(self) -> dict[str, Any]:

        with open(self.config_path, 'r') as f:
            config = json.load(f)

        return config