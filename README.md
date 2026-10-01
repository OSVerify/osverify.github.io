# OSVerify website

Project page for **OSVerify: One-Sided Verification Under Limited Expert Review**.
Plain static HTML/CSS with no build step, meant for GitHub Pages and eventually served at `osv.stanford.edu`.

```
index.html            single-page site
404.html              GitHub Pages not-found page
assets/css/style.css  all styles (light + dark via prefers-color-scheme)
assets/js/site.js     BibTeX copy button
assets/img/           logo (SVG), paper figures (PNG, 1920 px wide), icons, social preview
.nojekyll             serve files as-is (no Jekyll processing)
```

## Preview locally

```bash
python3 -m http.server 8765
```

Then open http://localhost:8765.

## Updating figures

Figures are rendered from the paper repo's PDFs:

```bash
pdftocairo -png -scale-to-x 1920 -scale-to-y -1 -singlefile ../validator-paper/figures/fig1_teaser.pdf assets/img/fig1_teaser
```

The same command works for `fig1_motivation_row` and `scaling_rows`. Numbers in the results table are copied by hand from the paper's Table 1 (`sections/05_evaluation.tex`).

## Before going public

- [ ] arXiv and code links (replace the two "coming soon" buttons)
- [ ] arXiv eprint / url in the BibTeX
- [ ] Contact address with a Stanford affiliation in the footer
- [ ] Absolute `og:image` / `og:url` once the final domain is known

## Deploy (GitHub Pages)

1. Create the public repo `OSVerify/osverify.github.io` and push this folder to `main`.
2. Repo **Settings → Pages**: Source = *Deploy from a branch*, Branch = `main` / `(root)`.
   The site goes live at `https://osverify.github.io`.

## Custom domain (`osv.stanford.edu`)

1. **Verify the domain for the org first** (prevents takeover): org **Settings → Pages → Add a domain** → `osv.stanford.edu`.
   GitHub shows a TXT record `_github-pages-challenge-OSVerify.osv.stanford.edu`. Ask Stanford to create it in the same NetDB request.
2. Stanford creates `CNAME osv.stanford.edu → osverify.github.io` in NetDB, after University Communications approves the name.
3. Repo **Settings → Pages → Custom domain** = `osv.stanford.edu`. This commits a `CNAME` file; do not add it by hand earlier.
4. Once the certificate is issued, enable **Enforce HTTPS**. Stanford requires HTTPS-only.
5. Register the site in Siteimprove, as Stanford's Minimum Web Standards require for public sites.

Stanford sites such as `crfm.stanford.edu` and `hazyresearch.stanford.edu` use this same CNAME-to-GitHub-Pages setup.
