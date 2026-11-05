# BioCode Commons website

Public website for the [BioCode-Commons organization](https://github.com/BioCode-Commons).

The mission, three Community Engagement sections, and four Our Approach sections are reproduced from the supplied [BioCommons document](https://docs.google.com/document/d/1w9EBx7nDaz8boPwisk31kjCKy8vyJB_KMRgfcQD0oYc/edit), retrieved on November 5, 2026. The source document was last modified on November 4, 2026. Original body wording is retained; navigation, display headings, and calls to action were added for the website. The document is copied into the site, not embedded, and future document changes do not automatically synchronize.

## Edit and preview

Edit `content/source.txt` for body content, `template.html` for page structure, and `styles.css` for styling. Python 3 is the only build dependency:

```sh
python3 build.py
python3 -m http.server 8080
```

Open http://localhost:8080. Commit the generated `index.html` alongside source changes. GitHub Pages serves the root of the `main` branch; `.nojekyll` keeps it a static site.

The site uses system fonts, local SVG artwork, no third-party scripts, no analytics, and no package dependencies. It supports mobile layouts, keyboard navigation, and reduced-motion preferences.

AI assisted with the page implementation. The source document's statements about human review describe the organization's stated approach; they do not certify that this website or any individual software project has undergone a comprehensive human audit.
