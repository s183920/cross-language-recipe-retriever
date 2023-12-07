"""
Module which includes functions for creating index .json files
and indexes.
"""

from bs4 import BeautifulSoup

def html_to_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text()

# Load HTML file
with open('../google_results/beef+mushrooms+pasta/english/Creamy Beef and Mushroom Stroganoff - Cafe Delites.html', 'r') as file:
    html_content = file.read()

# Convert to text
text_content = html_to_text(html_content)

print(text_content)