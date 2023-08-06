import os
from pybtex.database.input import bibtex
from pathlib import Path

import re


def latex_to_unicode(text):
    conversions = {
        r"\\'a": "á", r"\\'e": "é", r"\\'i": "í", r"\\'o": "ó", r"\\'u": "ú",
        r"\\'A": "Á", r"\\'E": "É", r"\\'I": "Í", r"\\'O": "Ó", r"\\'U": "Ú",
        r'\\"a': 'ä', r'\\"e': 'ë', r'\\"i': 'ï', r'\\"o': 'ö', r'\\"u': 'ü',
        r'\\"A': 'Ä', r'\\"E': 'Ë', r'\\"I': 'Ï', r'\\"O': 'Ö', r'\\"U': 'Ü',
        r"\\`a": "à", r"\\`e": "è", r"\\`i": "ì", r"\\`o": "ò", r"\\`u": "ù",
        r"\\`A": "À", r"\\`E": "È", r"\\`I": "Ì", r"\\`O": "Ò", r"\\`U": "Ù",
        r'\\^a': 'â', r'\\^e': 'ê', r'\\^i': 'î', r'\\^o': 'ô', r'\\^u': 'û',
        r'\\^A': 'Â', r'\\^E': 'Ê', r'\\^I': 'Î', r'\\^O': 'Ô', r'\\^U': 'Û',
        r"\\c\{c\}": "ç", r"\\c\{C\}": "Ç",
        r"\\.z": "ż", r"\\.Z": "Ż",
        r"\\v\{s\}": "š", r"\\v\{S\}": "Š",
        # ... add other conversions as needed
    }

    for latex, char in conversions.items():
        text = re.sub(latex, char, text)

    # Remove any remaining curly braces
    text = re.sub(r"{(.*?)}", r"\1", text)

    return text


def create_or_update_md(entry):
    # Extracting common fields
    key = entry.key
    title = entry.fields.get('title', '')
    year = entry.fields.get('year', '')
    journal = entry.fields.get('journal', entry.fields.get('booktitle', ''))
    volume = entry.fields.get('volume', '')
    pages = entry.fields.get('pages', '')
    publisher = entry.fields.get('publisher', '')
    url = entry.fields.get('url', '')

    # Extracting the author list and convert it to a list of authors
    authors = [str(author) for author in entry.persons.get('author', [])]

    # Define the path
    folder_path = Path(f"content/publications/{key}")
    file_path = folder_path / "index.md"

    # Check if file exists
    if file_path.exists():
        # Read the content and update
        with open(file_path, 'r') as f:
            content = f.read()

        # Logic to update the fields remains the same, but you may want to adjust it to match the TOML format if needed.
        # ...

    else:
        # If file doesn't exist, create a new markdown file with TOML front matter
        folder_path.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            f.write("+++\n")
            f.write(f'title= "{title}"\n')
            f.write('draft= false\n')
            f.write(f'authors  = {authors}\n')
            f.write(f'date = {year}-01-01\n')
            f.write(f'journal= "{journal}"\n')
            f.write(f'volume= "{volume}"\n')
            f.write(f'pages= "{pages}"\n')
            f.write(f'publisher= "{publisher}"\n')
            f.write(f'url= "{url}"\n')
            f.write("+++\n\n")
            f.write(f"Summary about {title}.")


def get_author_list(entry):
    if 'author' in entry.persons:
        authors = entry.persons['author']
        author_str = ' and '.join(str(author) for author in authors)
        return latex_to_unicode(author_str)
    return ''

def update_field(content, field, value):
    # If the field exists, update it. If not, just return the content as is.
    if f"{field}:" in content:
        content = re.sub(f'{field}:.*', f'{field}: "{value}"', content)
    return content

def main():
    parser = bibtex.Parser()
    bib_data = parser.parse_file("resources/references.bib")

    for entry in bib_data.entries.values():
        create_or_update_md(entry)

if __name__ == "__main__":
    main()