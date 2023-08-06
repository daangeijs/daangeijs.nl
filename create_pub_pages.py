import os
import re
from pybtex.database.input import bibtex

def extract_fields_from_md(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    fields = re.findall(r'^(\w+): (.+)$', content, re.MULTILINE)
    return dict(fields)

def extract_summary_from_md(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    # Everything after the front matter (after '---\n\n') is considered the summary
    return content.split('---\n\n', 1)[-1]

def create_or_update_md(entry):
    key = entry.key
    folder_path = os.path.join("path_to_your_content_folder", key)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file_path = os.path.join(folder_path, "index.md")

    # Extract fields from entry
    title = entry.fields.get("title", "")
    author = entry.fields.get("author", "")
    journal_or_booktitle = entry.fields.get("journal", entry.fields.get("booktitle", ""))
    year = entry.fields.get("year", "")
    publisher = entry.fields.get("publisher", "")
    volume = entry.fields.get("volume", "")
    number = entry.fields.get("number", "")
    pages = entry.fields.get("pages", "")
    url = entry.fields.get("url", "")
    school = entry.fields.get("school", "")  # for mastersthesis

    new_front_matter = f"""---
title: {title}
author: {author}
journal: {journal_or_booktitle}
year: {year}
publisher: {publisher}
volume: {volume}
number: {number}
pages: {pages}
url: {url}
school: {school}
---"""

    if os.path.exists(file_path):
        existing_fields = extract_fields_from_md(file_path)
        summary = extract_summary_from_md(file_path)

        # Check if fields are different and need updating
        fields_changed = (
            existing_fields.get("title") != title or
            existing_fields.get("author") != author or
            existing_fields.get("journal") != journal_or_booktitle or
            existing_fields.get("year") != year or
            existing_fields.get("publisher") != publisher or
            existing_fields.get("volume") != volume or
            existing_fields.get("number") != number or
            existing_fields.get("pages") != pages or
            existing_fields.get("url") != url or
            existing_fields.get("school") != school
        )

        if fields_changed:
            with open(file_path, 'w') as f:
                f.write(new_front_matter + "\n\n" + summary)
    else:
        with open(file_path, 'w') as f:
            f.write(new_front_matter + "\n\nShort summary about the publication goes here...")

def main():
    parser = bibtex.Parser()
    bib_data = parser.parse_file("resources/references.bib")

    for entry in bib_data.entries.values():
        create_or_update_md(entry)

if __name__ == "__main__":
    main()
