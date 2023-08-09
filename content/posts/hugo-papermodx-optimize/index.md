---
title: "Journey to Optimized Images: Hugo, Decap CMS, and Page Bundles"
date: 2023-08-09T21:48:00+01:00
draft: false

tags:
- hugo
- papermodx
- cms
- netlify
- decap

cover:
    image: "cover.webp"
    alt: "Decap Logo"
    
summary:
    "This turned out to be an unexpected long journey. It all began when I realized that my [website](https://dekeukenvandael.nl) images weren't optimized as I had expected. I had been relying on the PaperMod and PaperModX themes in Hugo to handle image optimization. Everything seemed to be in place, but my images were still bulky and slow to load. The problem was evident, but the cause? Not so much."
---
This turned out to be an unexpected long journey. It all began when I realized that my [website](https://dekeukenvandael.nl) images weren't optimized as I had expected. I had been relying on the PaperMod and PaperModX themes in Hugo to handle image optimization. Everything seemed to be in place, but my images were still bulky and slow to load. The problem was evident, but the cause? Not so much.

Digging into the problem, I started by examining the `cover.html` file in the theme. This file is crucial for handling images. As I skimmed through the lines, an interesting section of the code caught my attention:

```go
## themes/PaperMod/layouts/partials/cover.html

{{- if $cover -}}{{/* i.e it is present in page bundle */}}
    ....optimisation code here
{{- else }}{{/* For absolute urls and external links, no img processing here */}}
    .... well...do nothing
```

The theme was checking for images within something called a "page bundle." If the image wasn't within this bundle, optimization processes wouldn't be triggered. That was my "Aha!" moment. For the themes to work their magic, my content needed to be organized into Hugo's page bundles.

So, with newfound clarity, I set about restructuring my content into these page bundles. The results? When building Hugo locally, the images were automatically resized and optimized, all thanks to the wonders of my new page bundles!

When I transitioned to page bundles, I anticipated that my `config.yml` for the CMS would require some adjustments. Luckily the CMS supported Page bundles by using so called `collections` and I followed the [official documentation](https://decapcms.org/docs/collection-types/) making the adjustments needed. 

However, with every solution came a new challenge. Now that my content was structured the right way for image optimization, my newly configured Decap CMS (previously Netlify CMS) threw a tantrum. Suddenly, it stopped listing any of my articles.  This was the most timeconsuming and puzzling setback. 

I scoured the internet for answers, hoping to stumble upon someone who had faced a similar issue. And then, I came across a post on [millerti.me](https://blog.millerti.me/2021/12/23/supporting-hugo-page-bundles-in-netlify-cms/) that held the missing piece to my puzzle. The article mentioned the specific lines I needed to integrate in the collections:

```yaml
# Support Hugo page bundles that puts index.md and images in folders named by slug
path: "{{slug}}/index"
media_folder: ""
```

Adding these lines was the magic touch. Now my CMS seamlessly stored new content, and it also listed my previous articles again and everything worked smoothly. This all resulted in the following config.yml:

```yaml
## admin/config.yml
backend:
  name: git-gateway
  branch: main # Branch to update (optional; defaults to master)
site_url: https://dekeukenvandael.nl
logo_url: https://www.dekeukenvandael.nl/images/static/logo.svg
publish_mode: editorial_workflow
media_folder: static/images
public_folder: /images
collections:
  - name: 'recipes'
    label: "Recipes"
    label_singular: "Recipe"
    folder: 'content/recipes'
    create: true
    slug: '{{year}}-{{month}}-{{day}}-{{slug}}/index'  # Note the /index here
    # Support Hugo page bundles that puts index.md and images in folders named by slug
    path: "{{year}}-{{month}}-{{day}}-{{slug}}/index"
    preview_path: 'recipes/{{year}}-{{month}}-{{day}}-{{slug}}'
    preview_path_date_field: date
    editor:
      preview: true
    fields:
      - { label: 'Title', name: 'title', widget: 'string' }
      - { label: 'Publish Date', name: 'date', widget: 'datetime' }
      - { label: "Authors", name: "author", widget: "list", summary: "{{fields.author_name}}", field: { label: "Author name", name: "author_name", widget: "string" }}
      - { label: 'Tags', name: 'tags', widget: 'list', required: false, items: [{ type: 'string' }] }
      - { label: 'Categories', name: 'categories', widget: 'list', required: false, items: [{ type: 'string' }] }
      - { label: 'Cover Image', name: 'cover', widget: 'object', fields: [
          { label: 'Image', name: 'image', required: false, widget: 'image' }
        ]
      }
      - { label: 'Summary', name: 'summary', widget: 'text', required: false }
      - { label: 'Body', name: 'body', widget: 'markdown' }
```

I hope it helps to reduce the time and effort for others facing similar issues. It wasn't a straightforward process for me, and I'd be pleased if others can benefit from the lessons I learned. Maybe with the time you saved you can write an nice article about how this helped you ;). 