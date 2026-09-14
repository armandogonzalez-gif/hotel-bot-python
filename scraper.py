#!/usr/bin/env python3
"""
Text to Python Conversion
Generated: 2026-09-14T16:41:19.890Z
Total Lines: 14
"""

def process_text():
    """
    Process and analyze text data
    Returns: dictionary with text data and metadata
    """
    text_lines = [
    "import requests",
    "from bs4 import BeautifulSoup",
    "def extract_price(url):",
    "    try:",
    "        html = requests.get(url, timeout=10).text",
    "        soup = BeautifulSoup(html, \"html.parser\")",
    "        price = None",
    "        for tag in soup.find_all(text=True):",
    "            if \"$\" in tag:",
    "                price = tag.strip()",
    "                break",
    "        return price if price else \"No encontrado\"",
    "    except:",
    "        return \"Error\""
    ]
    
    # Calculate metadata
    metadata = {
        'total_lines': 14,
        'total_characters': 419,
        'total_words': 42,
        'created_at': '2026-09-14T16:41:19.890Z',
        'version': '1.0'
    }
    
    # Calculate statistics
    line_lengths = [len(line) for line in text_lines]
    statistics = {
        'average_line_length': sum(line_lengths) // len(line_lengths) if line_lengths else 0,
        'longest_line': max(line_lengths) if line_lengths else 0,
        'shortest_line': min(line_lengths) if line_lengths else 0,
        'empty_lines': 4
    }
    
    return {
        'lines': text_lines,
        'metadata': metadata,
        'statistics': statistics
    }

def display_text(data):
    """Display text data with metadata"""
    print("Metadata:")
    for key, value in data['metadata'].items():
        print(f"  {key}: {value}")
    
    print("\nStatistics:")
    for key, value in data['statistics'].items():
        print(f"  {key}: {value}")
    
    print("\nText Lines:")
    for i, line in enumerate(data['lines'], 1):
        print(f"Line {i}: {line}")

if __name__ == "__main__":
    data = process_text()
    display_text(data)