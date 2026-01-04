# Utility Function for file and Json Handling

import json
from pathlib import Path
from typing import List, Dict

def pick_requirement(file_path: str = None, req_dir: str= "data/requirements") -> Path:
    if file_path:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File {file_path} does not exist.")
        return path
    
    # Pick the first requirement file in the directory
    txt_files = sorted(Path(req_dir).glob("*.txt"))
    if not txt_files:
        raise FileNotFoundError(f"No requirement files found in directory {req_dir}.")
    return txt_files[0]

def parse_json_safely(text: str, raw_file: Path) -> List[Dict]:
    raw_file.parent.mkdir(parents=True, exist_ok=True)
    raw_file.write_text(text, encoding="utf-8")
    
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
    except:
        pass
    
    cleaned = text.strip();
    
    if cleaned.startswith("```"):
        # Remove Backticks
        cleaned = cleaned.strip("`")
        # Remove language specifier if present
        if "\\n" in cleaned:
            lines = cleaned.split("\\n",1)
            if lines[0].strip() in ["json", "jsonc", "JSON", ""]:
                cleaned = lines[1]
    
    data = json.loads(cleaned)
    if not isinstance(data, list):
        raise ValueError("Expected JSON array. But got something else.")
    return data