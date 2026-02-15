from typing import List, Dict, Any
import os

root_path_instruction = "instructions"


# Load the txt file and return in string format
def load_instruction_file(file_path: str) -> str:

    # Get current working directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, root_path_instruction, file_path)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    with open(file_path, 'r') as file:
        content = file.read()
        
    return content