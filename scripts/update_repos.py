"""Refresh the pirate README from public GitHub repository metadata (stdlib only)."""
import html
import json
import os
from pathlib import Path
import textwrap
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
START, END = '<!-- REPOS:START -->', '<!-- REPOS:END -->'


def fetch_repos(username):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'pirate-profile'}
    if os.environ.get('GH_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GH_TOKEN']
    repos = []
    for page in range(1, 101):
        url = f'https://api.github.com/users/{username}/repos?type=owner&sort=pushed&direction=desc&per_page=100&page={page}'
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as response:
            batch = json.load(response)
        repos.extend(r for r in batch if not r['private'] and r['name'].lower() != username.lower())
        if len(batch) < 100:
            break
    return sorted(repos, key=lambda r: r.get('pushed_at') or '', reverse=True)


def card(repo):
    esc = lambda value: html.escape(str(value), quote=True)
    title = textwrap.shorten(repo['name'], width=38, placeholder='…')
    description = ' '.join((repo.get('description') or 'An expedition in code.').split())
    lines = textwrap.wrap(description, width=53)[:2]
    if len(textwrap.wrap(description, width=53)) > 2:
        lines[-1] = textwrap.shorten(lines[-1], width=49, placeholder='') + '…'
    description_svg = ''.join(f'<text x="25" y="{96+i*21}" class="desc">{esc(line)}</text>' for i, line in enumerate(lines))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="195" viewBox="0 0 600 195" role="img" aria-label="{esc(repo['name'])}">
<defs><linearGradient id="sea" x2="1" y2="1"><stop stop-color="#132923"/><stop offset="1" stop-color="#080f13"/></linearGradient><linearGradient id="gold"><stop stop-color="#8e622b"/><stop offset=".5" stop-color="#f1d491"/><stop offset="1" stop-color="#95703b"/></linearGradient></defs>
<style>.desc{{font:14px Georgia,serif;fill:#d7cfb9}}.meta{{font:12px monospace;fill:#c7b88e}}</style>
<rect x="2" y="2" width="596" height="191" rx="12" fill="url(#sea)" stroke="url(#gold)" stroke-width="3"/>
<g stroke="#c7a15a" fill="none" opacity=".12"><circle cx="530" cy="93" r="53"/><circle cx="530" cy="93" r="38"/><path d="M530 23V163M460 93H600M480 43L580 143M480 143L580 43"/><path d="M0 160Q75 130 150 160T300 160T450 160T600 160M0 175Q75 145 150 175T300 175T450 175T600 175"/></g>
<path d="M22 25H65M22 29H45M22 145H578" stroke="#98743c"/>
<text x="25" y="66" fill="#f0d395" font-family="Georgia,serif" font-size="23" font-weight="bold">{esc(title)}</text>
{description_svg}
<text x="25" y="170" class="meta">{esc(repo.get('language') or 'Code')} · ★ {int(repo.get('stargazers_count', 0))} · Forks {int(repo.get('forks_count', 0))}</text>
<text x="575" y="170" text-anchor="end" class="meta">{esc((repo.get('pushed_at') or '')[:10])}</text>
</svg>'''


def update(repos):
    assets = ROOT / 'assets' / 'repos'
    assets.mkdir(parents=True, exist_ok=True)
    pieces = ['<table>']
    for i, repo in enumerate(repos[:8]):
        filename = f"{int(repo['id'])}.svg"
        (assets / filename).write_text(card(repo), encoding='utf-8')
        if i % 2 == 0:
            pieces.append('<tr>')
        name = html.escape(repo['name'], quote=True)
        url = html.escape(repo['html_url'], quote=True)
        pieces.append(f'<td width="50%"><a href="{url}"><img src="assets/repos/{filename}" width="100%" alt="{name} — open repository" /></a></td>')
        if i % 2 == 1:
            pieces.append('</tr>')
    if len(repos[:8]) % 2:
        pieces.append('<td width="50%"></td></tr>')
    pieces.append('</table>')
    if not repos:
        pieces = ['<p>The fleet is preparing for its next voyage. No public repositories found.</p>']
    readme = ROOT / 'README.md'
    text = readme.read_text()
    assert text.count(START) == text.count(END) == 1, 'Repository section markers must appear exactly once.'
    before, rest = text.split(START)
    _, after = rest.split(END)
    readme.write_text(before + START + '\n' + '\n'.join(pieces) + '\n' + END + after)


if __name__ == '__main__':
    update(fetch_repos(os.environ.get('PROFILE_USERNAME', 'coutdg')))
