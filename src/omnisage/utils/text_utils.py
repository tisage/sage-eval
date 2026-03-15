# PROJECT_FOLDER/src/omnisage/utils/text_utils.py
"""
Simplified text processing utilities.
"""

import re
from typing import Union

def count_words(text: str, language: str = "Chinese") -> int:
    """Count words in text based on language."""
    if not text:
        return 0
    
    if language.lower() in ["chinese", "中文"]:
        # Count Chinese characters
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        return len(chinese_chars)
    else:
        # Count words for other languages
        words = text.split()
        return len(words)

def clean_content(content: str) -> str:
    """Clean and normalize content."""
    # Remove excessive whitespace
    content = re.sub(r'\n\s*\n', '\n\n', content)
    content = re.sub(r' +', ' ', content)
    
    # Remove leading/trailing whitespace
    content = content.strip()
    
    return content