---
title: "Enhancing Your Hugo Blog: Embedding GitHub Repositories"
date: 2023-07-25T12:48:00+01:00
draft: false

tags:
- ubuntu
- docker
- home automation
- backup

cover:
    image: "cover.png"
    alt: "GitHub Logo"
    
summary:
   "Since I code a lot of stuff and want to make this public on GitHub more I decided that I also wanted to showcase it on this website. In this article, we'll explore two ways to showcase your GitHub repositories on your Hugo blog:"
---


Since I code a lot of stuff and want to make this public on GitHub more I decided that I also wanted to showcase it on this website. In this article, we'll explore two ways to showcase your GitHub repositories on your Hugo blog:

1. **Shortcodes**: For manually embedding specific repositories in markdown.
2. **Partials with Python**: For automating the display of selected repositories using a Python script.

## 1. Embedding a GitHub Repo Using Shortcodes

### Styling with CSS:

For a consistent appearance between shortcodes and partials, we're employing a basic CSS design. Here's a style snippet that you can add to your site's CSS file:

```css
.github-card {
    border: 1px solid #e1e4e8;
    padding: 15px;
    margin: 20px 0;
    border-radius: 5px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    background: #f6f8fa;
}
.github-card h2 {
    font-size: 1.2em;
    margin-bottom: 8px;
    margin: auto;
}
.github-card h2 a {
    text-decoration: none;
    color: #0366d6;
}
.github-card p {
    margin-bottom: 10px;
}
.card-details {
    display: flex;
    gap: 10px;
    font-size: 0.9em;
}
.language {
    color: #586069;
}
.stars, .forks {
    color: #586069;
}
```

This CSS ensures a neat card-style presentation for the GitHub repositories. Both our shortcode and our partial will utilize this styling.

### The Shortcode:

Now, let's create a new shortcode. In your Hugo site's `layouts/shortcodes` directory, create a file called `githubRepoCard.html` and paste the following:

```html
<div class="github-repo-card">
    <a href="{{ .Get "url" }}" target="_blank">
        <h3>{{ .Get "name" }}</h3>
    </a>
    <p>{{ .Get "description" }}</p>
    <p><strong>Language:</strong> {{ .Get "language" }}</p>
    <p><strong>Stars:</strong> {{ .Get "stars" }}</p>
    <p><strong>Forks:</strong> {{ .Get "forks" }}</p>
</div>
```

### Using the Shortcode:

In any markdown file, you can now use the shortcode like this (note the space I added between {{ to prevent hugo from rendering the shortcode on this page): 

```markdown

{ {< githubRepoCard url="https://github.com/username/myrepo" name="MyRepo" description="This is my awesome repo" language="JavaScript" stars="100" forks="50" >}}
```

## 2. Auto-generating a Partial with Python

### The Partial:
Similair to the shortcode we now make a partial called `githubRepoCard.html` and place it in our Hugo site's `layouts/partials`:

```html
<div class="github-repo-card">
    <a href="{{ .url }}" target="_blank">
        <h3>{{ .name }}</h3>
    </a>
    <p>{{ .description }}</p>
    <p><strong>Language:</strong> {{ .language }}</p>
    <p><strong>Stars:</strong> {{ .stars }}</p>
    <p><strong>Forks:</strong> {{ .forks }}</p>
    <p><strong>Last Updated:</strong> {{ .lastUpdated }}</p>
</div>
```

### The Python Script:

The Python script is designed to scrape your GitHub profile and retrieve information about specific repositories. I use the `BeautifulSoup` library for this, which made parsing HTML and navigating the DOM pretty easy.

**1. Setting Up**

Before diving into the script, ensure you have the necessary libraries installed:

```bash
pip install requests beautifulsoup4
```

**2. Initialize Constants and Fetch Profile Page**

Start by setting up the base URL and headers. The headers, especially the 'User-Agent', help in avoiding blocks when making requests to GitHub.

```python
URL = "https://github.com/daangeijs?tab=repositories"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
```

Then, fetch the repos from the main profile page, I found the information for each in the div with the class `col-10 col-lg-9 d-inline-block`:

```python
response = requests.get(BASE_URL, headers=HEADERS)
soup = BeautifulSoup(response.content, 'html.parser')
repos = soup.find_all('div', class_='col-10 col-lg-9 d-inline-block')
```

**3. Filtering Repositories**

Since I don't want to list all my repos on the website I only collect a subset of repositories. To do this, I create a list of repository names that I want to include:

```python
specified_repos = ['daangeijs.nl', 'dekeukenvandael.nl']
partials = []
nl = '\n' # Newline character since it is not possible to use newlines in formatted strings
```

**4. Loop through Repositories**

Now, for each repository on the profile page, check if its name matches any of the names in our `specified_repos` list. If there's a match, extract additional information:

```python
for repo in repos:
    name = repo.find('a', itemprop='name codeRepository').text.strip()
    
    if name in specified_repos:
        ...
```

**5. Dive Deeper into Each Repo**

For more detailed data, like the exact number of stars and forks, we need to visit each repo's individual page, here you see how I extracted the main project language, description and last updated time:

```python
# Extract base info  
repo_url = f"https://github.com{repo.find('a', itemprop='name codeRepository')['href']}"  
description_elem = repo.find('p', itemprop='description')  
description = description_elem.text.strip() if description_elem else "No description provided."  
language_elem = repo.find('span', itemprop='programmingLanguage')  
language = language_elem.text.strip() if language_elem else "Not specified"  
last_updated = repo.find('relative-time').attrs.get('datetime', 'Unknown Date')
```

**6. Extract Stars, Forks, and Last Updated Time**

Using these specified HTML locations we extract the number of stars and forks:

```python
# Fetch repo-specific page to extract stars and forks  
repo_response = requests.get(repo_url, headers=HEADERS)  
repo_soup = BeautifulSoup(repo_response.content, 'html.parser')  
  
stars_elem = repo_soup.find('span', id="repo-stars-counter-star")  
forks_elem = repo_soup.find('span', id="repo-network-counter")  
  
stars = stars_elem['title'] if stars_elem and 'title' in stars_elem.attrs else '0'  
forks = forks_elem['title'] if forks_elem and 'title' in forks_elem.attrs else '0'
```

We then generate the partial string that we add to a list

```python
partial = f'''{{{{ partial "githubRepoCard.html" (dict "url" "{repo_url}" "name" "{name}" "description" "{description}" "language" "{language}" "stars" "{stars}" "forks" "{forks}" "lastUpdated" "{last_updated}") }}}}'''  
partials.append(partial)
```

**7. Save Extracted Data as Hugo Partials**

Once all the desired data is scraped and the partials are generated we save them in a file and we add a little bit of html to create a div and title around the partials:

```python
wrapped_content = f'''
<div class="latest-publications">
    <h2>My GitHub repositories</h2>
    {"\n".join(partials)}
</div>
'''

with open("partials_generated.html", "w") as file:
    file.write(wrapped_content)
```

---

### Using the Generated HTML:

Once you run the Python script, it'll create an HTML file named `partials_generated.html` in your directory. This file contains wrapped partial calls, which you can include in your Hugo layouts or content. I store mine here: `layouts/partials/github.html`

To add the partial to a page simply use this in your html template: 
`{{ partial "github.html" }}`

---
So that is it, two ways I implemented partials and shortcodes to add my GitHub repo's to this Hugo generated website. Here the final result together with the already existing gist shortcode from Hugo. Stacked on each other it looks great! For the latest version have a look at the source of my website. Or you can copy the code for the python script below:

{{< githubRepoCard url="https://github.com/daangeijs/daangeijs.nl" name="daangeijs.nl" description="This repo contains the sourcecode of the website https://daangeijs.nl/, my personal website. It is built using Hugo, a static site generator. The theme is based on PapermodX." language="HTML" stars="1" forks="0" >}}


{{< gist daangeijs e00759f976d6d8df96a89761d772ee2d >}}