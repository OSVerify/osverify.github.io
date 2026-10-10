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
    head = head.replace('<a href="./" aria-current="page">Blog</a>', '<a href="./">Blog</a>')
    head = head.replace('<a href="case-studies.html">Results</a>', '<a href="case-studies.html" aria-current="page">Results</a>')
    foot = FOOT
    if prefix:
        for attr in ('href', 'src', 'srcset', 'content'):
            head = head.replace(f'{attr}="assets/', f'{attr}="{prefix}assets/')
            foot = foot.replace(f'{attr}="assets/', f'{attr}="{prefix}assets/')
        head = head.replace('href="./', f'href="{prefix}')
        head = head.replace('href="case-studies.html"', f'href="{prefix}case-studies.html"')
    return head + '  <main id="main">\n' + body + '\n  </main>\n\n' + foot


def count(paper, severity):
    return sum(i['severity'] == severity for i in paper['issues'])


def badges(paper):
    result = ''.join(f'<span class="severity {s}">{count(paper, s)} {s.title()}</span>' for s in ('major', 'minor'))
    if not paper['coverage_complete']:
        result += '<span class="review-status">Coverage incomplete</span>'
    return '<div class="finding-counts">' + result + '</div>'


def card(paper):
    slug = text(paper['slug'])
    return f'''<article class="paper-card">
      <div class="study-meta"><span>OpenAI · {text(paper['version'])}</span>{badges(paper)}</div>
      <h3><a href="cases/{slug}.html">{text(paper['title'])}</a></h3>
      <p>{text(paper['summary'])}</p>
      <div class="paper-links"><a href="cases/{slug}.html">Read issues <span aria-hidden="true">→</span></a>
        <a href="{text(paper['paper_url'])}">Original paper <span aria-hidden="true">↗</span></a></div>
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


def main():
    (ROOT / 'cases').mkdir(exist_ok=True)
    total = sum(len(p['issues']) for p in PAPERS)
    majors = sum(count(p, 'major') for p in PAPERS)
    body = f'''<div class="page-intro container">
      <p class="eyebrow">Paper Referee · OpenAI Math</p><h1>Results</h1>
      <p class="lead">Specific issues, counterexamples, and proposed repairs from OSVerify’s reviews of OpenAI’s mathematical preprints.</p>
      <p class="muted">Browse each paper’s findings, grouped into Major and Minor issues, alongside a link to the original paper.</p>
      <p class="collection-summary">{len(PAPERS)} papers <span aria-hidden="true">·</span> {total} findings <span aria-hidden="true">·</span> {majors} Major / {total-majors} Minor</p>
    </div>
    <section class="study-section" id="paper-referee" aria-labelledby="paper-referee-title"><div class="container">
      <h2 id="paper-referee-title">Paper Referee</h2>
      <p class="collection-note">This collection includes reports with released findings. Counts and severity labels reflect OSVerify’s internal review, not author confirmation. Any remaining coverage limitations are noted on the individual paper.</p>
      <div class="paper-list">{''.join(card(p) for p in PAPERS)}</div>
    </div></section>'''
    (ROOT / 'case-studies.html').write_text(document('Results', 'Paper Referee results from OSVerify, with original papers, Major and Minor findings, and proposed repairs.', body))
    for paper in PAPERS:
        (ROOT / f'cases/{paper["slug"]}.html').write_text(paper_page(paper))
    print(f'Rendered results index and {len(PAPERS)} paper pages ({total} issues).')


if __name__ == '__main__':
    main()
