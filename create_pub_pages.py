import os
from pybtex.database.input import bibtex
from pathlib import Path
from pylatexenc.latex2text import LatexNodes2Text
import re


def latex_to_unicode(text):
    return LatexNodes2Text().latex_to_text(text)


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
    authors = [latex_to_unicode(str(author)) for author in entry.persons.get('author', [])]

    # Define the path
    folder_path = Path(f"content/publications/{key}")
    file_path = folder_path / "index.md"

    # Check if file exists
    if not file_path.exists():
        # If file doesn't exist, create a new markdown file with TOML front matter
        folder_path.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            f.write("+++\n")
            f.write(f'title = "{title}"\n')
            f.write('hidden = true\n')
            f.write(f'authors  = {authors}\n')
            f.write(f'date = {year}-01-01\n')
            f.write(f'journal = "{journal}"\n')
            f.write(f'volume = "{volume}"\n')
            f.write(f'pages = "{pages}"\n')
            f.write(f'publisher = "{publisher}"\n')
            f.write(f'url = "{url}"\n')
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
