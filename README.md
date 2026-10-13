# OSVerify website

Project page for **OSVerify: One-Sided Verification Under Limited Expert Review**.
Plain static HTML/CSS with no build step, meant for GitHub Pages and eventually served at `osv.stanford.edu`.

```
index.html            home page: summary, 01 problem, 02 method, 03 evidence, citation
blog/index.html       Coming soon placeholder; blog links are temporarily hidden
case-studies.html     index of OpenAI paper referee case studies
cases/               individual paper pages, grouped by Major / Minor issues
data/                curated findings and source-report provenance
scripts/             static case study page generator
404.html              GitHub Pages not-found page
assets/css/style.css  all styles (light + dark via prefers-color-scheme)
assets/js/site.js     BibTeX copy button
assets/papers/        OSVerify preprint PDF, linked from the Paper button
assets/img/           logo (PNG, light + dark), paper figures (PNG, 1920 px wide), icons, social preview
.nojekyll             serve files as-is (no Jekyll processing)
```

## Preview locally

```bash
python3 -m http.server 8765
```

Then open http://localhost:8765.

## Navigation and results

The shared top menu is **Results / Contribute**; the logo links to
the home page. Blog links are temporarily removed from navigation and the home
page; `blog/` displays "Coming soon". Restore the earlier article from Git history
when it is ready to publish. Contribute opens the home page's `#contribute`
section. The home page's BibTeX button opens its `#citation` section. Results pages inherit the header and footer from `index.html`,
with Results marked current. `blog/index.html` keeps its own copy of the
header and footer, so edit both when the chrome changes.

`case-studies.html#paper-referee` lists reports with released findings. Each
paper has an original-paper link, reviewed version date, and separate Major
and Minor groups. Each issue has a stable shareable anchor.

Repair sections use **Proposed repair by OSVerify** and are collapsed by default,
like **Related context**.
An optional `expert_comment` on an issue renders as a visible **Human expert comment** block
between the evidence and the repair. Expanding them displays the original released repair
feedback in full; collapsing the UI must not shorten or rewrite the content.

Severity defaults to the source report. Explicit editorial reclassifications
are recorded in `data/case-study-provenance.json` under `severity_overrides`;
the original report and its classification remain unchanged. Incomplete review coverage is shown explicitly. Source
commit strings are not shown on the pages.

Full referee PDFs are temporarily withheld while their formatting is revised.
Keep those draft files outside the published website directory.

To update entries, edit `data/case-studies.json` and run:

```bash
python3 scripts/build_case_studies.py
```

The script also rewrites the block between `<!-- referee-summary:start -->`
and `<!-- referee-summary:end -->` in `index.html`: the paper and issue
counts, and cards for every paper with a Major issue. Commit the generated
HTML along with its input data; GitHub Pages needs no build step. `data/case-study-provenance.json` records report hashes and issue
IDs for checking the import. The imported findings are OSVerify-reviewed,
not author-confirmed. Reference-only follow-ups do not replace the original
full-paper review's coverage state. The three expanded counterexample cards
adapt the earlier social summaries; original feedback remains in the data.

## Updating figures

Figures are rendered from the paper repo's PDFs:

```bash
pdftocairo -png -scale-to-x 1920 -scale-to-y -1 -singlefile ../validator-paper/figures/fig1_teaser.pdf assets/img/fig1_teaser
```

The same command works for `fig1_motivation_row` and `scaling_rows`. Numbers in the results table are copied by hand from the paper's Table 1 (`sections/05_evaluation.tex`).

## Paper PDF

The home page's Paper button links to `assets/papers/osverify.pdf`. This is the
40-page arXiv-ready PDF prepared on 2026-10-13 from manuscript commit
`ed8b95a9f38591f95b0432047d02b0edc8589cf7`. It matches the verified release
PDF byte for byte. Publish only the PDF here; source archives and cleanup
reports stay outside the site. Once the arXiv entry is public, change the Paper
button to its `https://arxiv.org/abs/...` URL and add the identifier to BibTeX.

## Before going public

- [x] Paper PDF available from the home page
- [ ] Replace the hosted Paper PDF link with the public arXiv entry
- [x] Code link → https://github.com/OSVerify
- [ ] arXiv eprint / url in the BibTeX
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

Case pages display printed paper references from the referee export's
`paper-locations/locations.json`. `data/paper-locations.json` keeps that mapping,
its frozen-source hashes, and the original line spans for traceability. Numbers
come from LaTeX cross-references or exact named headings in the original PDF.
Classification explanations and raw source-line lists are not rendered in the
case-page metadata; the Major/Minor grouping is retained.


Each published issue must have `issue_passages`: the precise paragraph/formula,
original PDF page, short quotation, and an explanation identifying the disputed
step. Quotes are transcribed from the reviewed PDF; `source_quote` and
`source_span` retain the corresponding frozen LaTeX evidence. Printed references
inside quotations are preserved, including erroneous citations in the paper.
`related_context` labels every other reference as background or a downstream use
and explains its relevance. A proof error must not be presented as a refutation
of its theorem. The historical `paper_references` union remains audit metadata
and is not rendered as a list of error locations.
