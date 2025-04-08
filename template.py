import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO , format='[%(asctime)s]:%(message)s:')

list_of_files = [
    "src/__init__.py",
    "src/helper.py",
    "src/prompt.py",
    ".env",
    "setup.py",
    "app.py",
    "research/trials.ipynb",
    "requirements.txt"
]

for filepath in list_of_files:
    filepath = Path(filepath)
    filedir, filename = os.path.split(filepath)
    
    if filedir !="":
        os.makedirs(filedir , exist_ok=True)
        logging.info(f"creating directory: {filedir} for file: {filename}")
        
    if (not os.path.exists(filepath)):
        with open(filepath , "w") as f:
            pass
        logging.info(f"creating file: {filepath}") 
    else:
        logging.info(f"{filename} is already exist")       