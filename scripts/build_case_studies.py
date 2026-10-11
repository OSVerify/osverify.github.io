#!/usr/bin/env python3
"""Render the curated referee snapshots as standalone static HTML pages."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPERS = json.loads((ROOT / 'data/case-studies.json').read_text())
HOME = (ROOT / 'index.html').read_text()
HEAD = HOME.split('  <main id="main">', 1)[0]
FOOT = '  <footer>' + HOME.split('  <footer>', 1)[1]
FOOT = re.sub(r'  <script[^>]+></script>\n', '', FOOT)


def text(value):
    return html.escape(str(value), quote=True)


def rich(value, reference_labels=None):
    for label, number in (reference_labels or {}).items():
        value = value.replace(label, number)
    result = text(value)
    result = re.sub(r'\[([^\]]+)\]\((https://[^\s)]+)\)', r'<a href="\2">\1</a>', result)
    result = re.sub(r'`([^`]+)`', r'<code>\1</code>', result)
    replacements = {
        'p_*ω_{H×N}': 'p<sub>*</sub>ω<sub>H×N</sub>',
        'Rπ_*ℂ_{SL₂}': 'Rπ<sub>*</sub>ℂ<sub>SL₂</sub>',
        'H*(': 'H<sup>*</sup>(', 'SL_2': 'SL₂',
        'P^1': 'ℙ¹', 'A^1': '𝔸¹', 'B_0': 'B₀',
        'X^I': 'X<sup>I</sup>', 'V_n': 'V<sub>n</sub>',
    }
    for original, replacement in replacements.items():
        result = result.replace(original, replacement)
    return result


def document(title, description, body, prefix=''):
    head = HEAD.replace('<title>OSVerify: One-Sided Verification</title>', f'<title>{text(title)} · OSVerify</title>')
    head = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m[1] + text(description), head)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m[1] + text(title + ' · OSVerify'), head)
    head = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m[1] + text(description), head)
    head = head.replace('<a href="case-studies.html">Results</a>', '<a href="case-studies.html" aria-current="page">Results</a>')
    foot = FOOT
    if prefix:
        for attr in ('href', 'src', 'srcset', 'content'):
            head = head.replace(f'{attr}="assets/', f'{attr}="{prefix}assets/')
            foot = foot.replace(f'{attr}="assets/', f'{attr}="{prefix}assets/')
        head = head.replace('href="./', f'href="{prefix}')
        head = head.replace('href="case-studies.html"', f'href="{prefix}case-studies.html"')
        head = head.replace('href="blog/"', f'href="{prefix}blog/"')
    return head + '  <main id="main">\n' + body + '\n  </main>\n\n' + foot


def count(paper, severity):
    return sum(i['severity'] == severity for i in paper['issues'])


def badges(paper):
    result = ''.join(f'<span class="severity {s}">{count(paper, s)} {s.title()}</span>' for s in ('major', 'minor'))
    if not paper['coverage_complete']:
        result += '<span class="review-status">Coverage incomplete</span>'
    return '<div class="finding-counts">' + result + '</div>'


def card(paper, heading='h2'):
    slug = text(paper['slug'])
    return f'''<article class="paper-card">
      <div class="study-meta"><span>OpenAI · {text(paper['version'])}</span>{badges(paper)}</div>
      <{heading}><a href="cases/{slug}.html">{text(paper['title'])}</a></{heading}>
      <p>{text(paper['summary'])}</p>
      <div class="paper-links">
        <a class="paper-link-primary" href="cases/{slug}.html">Read issues <svg viewBox="0 0 20 20" aria-hidden="true" focusable="false"><path d="M4 10h12m-5-5 5 5-5 5"/></svg></a>
        <a class="paper-link-secondary" href="{text(paper['paper_url'])}"><span>Original paper</span><svg viewBox="0 0 20 20" aria-hidden="true" focusable="false"><path d="M8 5H5a1 1 0 0 0-1 1v9a1 1 0 0 0 1 1h9a1 1 0 0 0 1-1v-3M11 4h5v5m0-5-8 8"/></svg></a>
      </div>
    </article>'''


def issue_card(issue, number):
    anchor = text(issue['anchor']); severity = text(issue['severity']); social = issue.get('social')
    def prose(value):
        return rich(value, issue.get('reference_labels'))

    diagnoses = [f for f in issue['feedback'] if f['kind'] == 'diagnosis']
    if social:
        evidence = f'<h4>Issue</h4><p>{prose(social["claim"])}</p><h4>Counterexample</h4>'
        evidence += ''.join(f'<p>{prose(p)}</p>' for p in social['evidence'])
        evidence += '<div class="issue-equations">' + ''.join(f'<div>{prose(eq)}</div>' for eq in social['equations']) + '</div>'
        evidence += f'<p>{prose(social["conclusion"])}</p>'
    else:
        evidence = '<h4>Issue &amp; evidence</h4>' + ''.join(f'<p>{prose(f["text"])}</p>' for f in diagnoses)
    suggestions = [f for f in issue['feedback'] if f['kind'] == 'repair_suggestion']
    requests = [f for f in issue['feedback'] if f['kind'] == 'repair_request']
    repairs = suggestions or requests
    repair_title = 'Proposed repair by OSVerify' if suggestions else 'Correction requested by OSVerify'
    repair = f'<aside class="issue-repair"><h4>{repair_title}</h4>' + ''.join(f'<p>{prose(f["text"])}</p>' for f in repairs) + '</aside>'
    references = issue['paper_references']
    details = '<details class="issue-context"><summary>Locations in the paper</summary>'
    details += '<p class="source-location">' + text('; '.join(references)) + '.</p>'
    details += '</details>'
    return f'''<article class="issue-card {severity}" id="{anchor}" data-issue-id="{text(issue['source_issue_id'])}">
      <div class="issue-masthead"><span class="severity {severity}">{severity.title()} · Issue {number:02d}</span><a href="#{anchor}" aria-label="Link to issue: {text(issue['title'])}">Link <span aria-hidden="true">↗</span></a></div>
      <h3>{text(issue['title'])}</h3><p class="issue-location">{text(issue['location'])}</p>
      {evidence}{repair}{details}
    </article>'''


def paper_page(paper):
    title = text(paper['title'])
    nav = ''.join(f'<a href="#{s}-issues">{s.title()} issues ({count(paper, s)})</a>' for s in ('major', 'minor'))
    scope = ''
    if not paper['coverage_complete']:
        scope = f'<p class="review-note"><b>Review coverage.</b> This report searched {paper["scopes_searched"]} of {paper["scopes_total"]} planned scopes. The findings below passed OSVerify’s internal review; the full-paper search is incomplete.</p>'
    if paper.get("review_note"):
        scope += f'<p class="review-note"><b>Review note.</b> {text(paper["review_note"])}</p>'
    body = f'''<header class="paper-intro container">
      <a class="back-link" href="../case-studies.html">← All results</a>
      <p class="eyebrow">Paper Referee · OpenAI</p><h1>{title}</h1>
      <p class="paper-version">Reviewed version: {text(paper['version'])}</p>{badges(paper)}
      <div class="paper-actions"><a class="btn" href="{text(paper['paper_url'])}">Original paper <span aria-hidden="true">↗</span></a></div>
      <p class="review-note">Findings and severity labels below are from OSVerify’s internal review. They do not by themselves establish that the paper’s main theorem is false.</p>{scope}
      <nav class="case-nav issue-nav" aria-label="Issue severity">{nav}</nav>
    </header>'''
    number = 0
    for severity in ('major', 'minor'):
        issues = [i for i in paper['issues'] if i['severity'] == severity]
        body += f'<section class="issue-group" id="{severity}-issues" aria-labelledby="{severity}-title"><div class="container"><h2 id="{severity}-title">{severity.title()} issues <span class="group-count">{len(issues)}</span></h2>'
        if not issues:
            body += f'<p class="muted">No {severity} issues were released in this report.</p>'
        for issue in issues:
            number += 1
            body += issue_card(issue, number)
        body += '</div></section>'
    return document(paper['title'], paper['summary'], body, '../')


def home_referee():
    """Write referee counts and the papers with major issues into the home page."""
    papers = len(PAPERS)
    major = sum(count(p, 'major') for p in PAPERS)
    minor = sum(count(p, 'minor') for p in PAPERS)
    featured = [p for p in PAPERS if count(p, 'major')]
    block = f'''<!-- referee-summary:start -->
        <p>We now also run OSVerify as a referee on new mathematics preprints from OpenAI. Across <b>{papers} papers</b>, it has flagged <mark class="hl rose">{major} major</mark> and <b>{minor} minor</b> issues, each verified by human experts. The papers with major issues:</p>
        <div class="paper-list featured">{''.join(card(p, 'h4') for p in featured)}</div>
        <p class="more"><a class="btn secondary" href="case-studies.html#paper-referee">See all {papers} referee reports <span aria-hidden="true">→</span></a></p>
<!-- referee-summary:end -->'''
    home = (ROOT / 'index.html').read_text()
    home = re.sub(r'<!-- referee-summary:start -->.*?<!-- referee-summary:end -->', lambda m: block, home, flags=re.S)
    (ROOT / 'index.html').write_text(home)


def main():
    (ROOT / 'cases').mkdir(exist_ok=True)
    total = sum(len(p['issues']) for p in PAPERS)
    major = sum(count(p, 'major') for p in PAPERS)
    minor = sum(count(p, 'minor') for p in PAPERS)
    body = f'''<section class="study-section" id="paper-referee" aria-labelledby="paper-referee-title"><div class="container">
      <h1 class="collection-title" id="paper-referee-title">Paper Referee</h1>
      <p class="collection-note">This collection presents referee reports generated by OSVerify. All of them are further verified by human experts.</p>
      <p class="collection-stats">Across <b>{len(PAPERS)} papers</b>, OSVerify has found <span class="severity major">{major} Major</span> and <span class="severity minor">{minor} Minor</span> issues.</p>
      <div class="paper-list">{''.join(card(p) for p in PAPERS)}</div>
    </div></section>'''
    (ROOT / 'case-studies.html').write_text(document('Results', 'Paper Referee results from OSVerify, with original papers, Major and Minor findings, and proposed repairs.', body))
    for paper in PAPERS:
        (ROOT / f'cases/{paper["slug"]}.html').write_text(paper_page(paper))
    home_referee()
    print(f'Rendered results index and {len(PAPERS)} paper pages ({total} issues).')


if __name__ == '__main__':
    main()
