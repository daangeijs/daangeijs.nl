import requests
from bs4 import BeautifulSoup

URL = "https://github.com/daangeijs?tab=repositories"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
response = requests.get(URL, headers=HEADERS)

soup = BeautifulSoup(response.content, 'html.parser')
repos = soup.find_all('div', class_='col-10 col-lg-9 d-inline-block')

# List of specified repository titles
specified_repos = ['dekeukenvandael.nl', 'deepops-slurmjob', 'cobra', 'simple_wsi_viewer']

# Extracting data and creating partials
partials = []
nl = '\n' # Newline character since it is not possible to use newlines in formatted strings
for repo in repos:
    name = repo.find('a', itemprop='name codeRepository').text.strip()

    # Only process the repo if its name is in the specified list
    if name in specified_repos:
        # Extract base info
        repo_url = f"https://github.com{repo.find('a', itemprop='name codeRepository')['href']}"
        description_elem = repo.find('p', itemprop='description')
        description = description_elem.text.strip() if description_elem else "No description provided."
        language_elem = repo.find('span', itemprop='programmingLanguage')
        language = language_elem.text.strip() if language_elem else "Not specified"
        last_updated = repo.find('relative-time').attrs.get('datetime', 'Unknown Date')

        # Fetch repo-specific page to extract stars and forks
        repo_response = requests.get(repo_url, headers=HEADERS)
        repo_soup = BeautifulSoup(repo_response.content, 'html.parser')

        stars_elem = repo_soup.find('span', id="repo-stars-counter-star")
        forks_elem = repo_soup.find('span', id="repo-network-counter")

        stars = stars_elem['title'] if stars_elem and 'title' in stars_elem.attrs else '0'
        forks = forks_elem['title'] if forks_elem and 'title' in forks_elem.attrs else '0'

        partial = f'''{{{{ partial "githubRepoCard.html" (dict "url" "{repo_url}" "name" "{name}" "description" "{description}" "language" "{language}" "stars" "{stars}" "forks" "{forks}" "lastUpdated" "{last_updated}") }}}}'''
        partials.append(partial)

# Wrapping all partials in a div and saving to an HTML file
wrapped_content = f'''
<div class="latest-publications">
    <h2>My GitHub repositories</h2>
    {nl.join(partials)}
</div>
'''

with open("layouts/partials/github.html", "w") as file:
    file.write(wrapped_content)

print("layouts/partials/github.html")
