import json
import sys
from pathlib import Path
from typing import Dict, List
import pandas as pd

from src.core import chat, parse_json_safely, pick_requirement

# Project Paths
ROOT = Path(__file__).resolve().parents[2]
REQ_DIR = ROOT / "data" / "requirements"
OUT_DIR = ROOT / "outputs" / "testcase_generated"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Prompt

SYSTEM_PROMPT = """You are a QA engineer. Generate test cases from requirements.

Return ONLY a JSON array with this structure:
[
  {
    "id": "TC-001",
    "title": "Short test title",
    "steps": ["Step 1", "Step 2", "Step 3"],
    "expected": "Expected result",
    "priority": "High"
  }
]

Rules:
- Return 5 test cases
- Cover positive and negative scenarios
- Include edge cases
- Keep steps clear and actionable
- Priority: High, Medium, or Low
- Return ONLY JSON, no markdown fences"""


def save_as_csv(test_cases: List[Dict], csv_file: Path) -> None:
    rows = []
    for i, case in enumerate(test_cases, 1):
        # Extract fields with defaults
        test_id = case.get("id", f"TC-{i:03d}")
        title = case.get("title", "")
        expected = case.get("expected", "")
        priority = case.get("priority", "Medium")
        
        # Handling Steps
        steps = case.get("steps", [])
        if isinstance(steps, list):
            steps_text = " | ".join(steps)
        else:
            steps_text = str(steps)
        
        rows.append({
            "TestID": test_id,
            "Title": title,
            "Steps": steps_text,
            "Expected": expected,
            "Priority": priority
        })
        
        pd.DataFrame(rows).to_csv(csv_file, index=False, encoding="utf-8")

def main():
    # Pick requirement file
    file_arg = sys.argv[1] if len(sys.argv) > 1 else None
    req_file = pick_requirement(file_arg,REQ_DIR)
    requirement = req_file.read_text(encoding="utf-8")
    print(f"Processing requirement file: {req_file}")
    
    # Build messages for LLM
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Requirements are follows:\n\n{requirement}"}
    ]
    
    # Call LLM
    print("Calling LLM to generate test cases...")
    response = chat(messages)
    
    # Parse Json Response
    raw_file_txt = OUT_DIR / "raw_output.txt"
    raw_file_json = OUT_DIR / "raw_output.json"
    testcases = parse_json_safely(response, raw_file_txt)
    raw_file_json.write_text(json.dumps(testcases, indent=2), encoding="utf-8")
    
    # Save as CSV
    csv_file = OUT_DIR / "testcases.csv"
    save_as_csv(testcases, csv_file)
    
    print(f"Generated test cases: {len(testcases)}")
    print(f"Raw Text saved to: {raw_file_txt}")
    print(f"Raw Json saved to: {raw_file_json}")
    print(f"CSV saved to: {csv_file}")
    
if __name__ == "__main__":  # Check: is this file run directly (not imported)?
    main()                   # If yes, execute main() function