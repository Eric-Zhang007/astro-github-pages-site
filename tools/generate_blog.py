#!/usr/bin/env python3
"""Generate paper-reading blog posts from READING_GUIDE.md files and deploy via git."""
import sys, os, re, subprocess, datetime, yaml
from pathlib import Path

BLOG_DIR = '/mnt/c/Users/zjc/astro-github-pages-site'
CONTENT_DIR = os.path.join(BLOG_DIR, 'src/content/blog')
IMG_DIR = os.path.join(BLOG_DIR, 'public/images/blog')
PAPERS_DIR = '/mnt/c/Users/zjc/Desktop/papers'
FIGURE_SCRIPT = os.path.join(BLOG_DIR, 'tools/extract_figure.py')

def extract_figure(arxiv_id: str) -> str | None:
    r = subprocess.run(['python3', FIGURE_SCRIPT, arxiv_id], capture_output=True, text=True, timeout=30)
    if r.returncode == 0 and r.stdout.startswith('OK:'):
        return r.stdout.strip()[3:]
    return None

def parse_reading_guide(date: str) -> list[dict]:
    """Parse any READING_GUIDE format and extract paper entries."""
    guide_path = os.path.join(PAPERS_DIR, date, 'READING_GUIDE.md')
    if not os.path.exists(guide_path):
        return []
    
    with open(guide_path) as f:
        text = f.read()
    
    papers = []
    
    # Format 1: Table rows | # | arxiv_id | title | ...
    for m in re.finditer(r'\|\s*\d+\s*\|\s*([\d.]+)\s*\|\s*(.+?)\s*\|', text):
        aid = m.group(1).strip()
        title = m.group(2).strip()
        if len(aid) >= 8 and aid.count('.') >= 1:
            if not any(p['arxiv_id'] == aid for p in papers):
                papers.append({'arxiv_id': aid, 'title': title})
    
    # Format 2: `2605.XXXXX` backtick format (5/6 style)
    for m in re.finditer(r'`(\d{4}\.\d{4,5})`', text):
        aid = m.group(1)
        # Try to find the title nearby (bold text on same or next lines)
        title_match = re.search(r'\*\*([^*]+)\*\*', text[m.start():m.start()+500])
        title = title_match.group(1).strip() if title_match else aid
        if len(aid) >= 8 and not any(p['arxiv_id'] == aid for p in papers):
            papers.append({'arxiv_id': aid, 'title': title})
    
    # Format 3: Numbered list with bold titles (old format)
    for m in re.finditer(r'\d+\.\s*\*\*(.+?)\*\*', text):
        title = m.group(1).strip()
        # Find arxiv ID nearby
        nearby = text[m.start():m.start()+300]
        aid_m = re.search(r'(\d{4}\.\d{4,5})', nearby)
        if aid_m:
            aid = aid_m.group(1)
            if len(aid) >= 8 and not any(p['arxiv_id'] == aid for p in papers):
                papers.append({'arxiv_id': aid, 'title': title})
    
    # Format 4: Section headers with arxiv ID pattern
    for m in re.finditer(r'###\s*(?:T\d+\.\s*)?([\d.]+)\s*[—–-]\s*(.+)', text):
        aid = m.group(1).strip()
        title = m.group(2).strip()
        if len(aid) >= 8 and aid.count('.') >= 1:
            if not any(p['arxiv_id'] == aid for p in papers):
                papers.append({'arxiv_id': aid, 'title': title})
    
    return papers

def download_figures(papers: list[dict]) -> dict:
    """Download figures, return {arxiv_id: relative_path}."""
    figures = {}
    for p in papers:
        aid = p['arxiv_id']
        local_rel = f'images/blog/paper-{aid}.png'
        local_abs = os.path.join(BLOG_DIR, 'public', local_rel)
        if os.path.exists(local_abs):
            figures[aid] = local_rel
        else:
            result = extract_figure(aid)
            if result:
                figures[aid] = result
    return figures

def generate_markdown(date: str, papers: list[dict], figures: dict) -> str:
    """Generate blog markdown."""
    dt = datetime.datetime.strptime(date, '%Y-%m-%d')
    ds = dt.strftime('%Y-%m-%d')
    n = len(papers)
    
    # Build figure entries for YAML
    fig_entries = []
    for p in papers:
        aid = p['arxiv_id']
        src = figures.get(aid, '')
        if src and os.path.exists(os.path.join(BLOG_DIR, 'public', src)):
            fig_entries.append({'src': src, 'alt': p['title']})
    
    frontmatter = {
        'title': f'{ds} Paper Reading',
        'description': f'今日 arXiv 论文速读：{n} 篇入选 shortlist。',
        'date': ds,
        'tags': ['paper reading', 'arXiv', 'world model', 'autonomous driving', 'embodied AI'],
        'category': 'Research',
        'comments': True,
        'draft': False,
        'figures': fig_entries,
    }
    
    lines = ['---']
    lines.append(yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False, sort_keys=False).strip())
    lines.append('---')
    lines.append('')
    lines.append(f'# {ds} Paper Reading')
    lines.append('')
    lines.append(f'今日从 arXiv 订阅中筛选 {n} 篇论文。')
    lines.append('')
    lines.append('## 论文速览')
    lines.append('')
    lines.append('| # | arXiv ID | 标题 | 链接 |')
    lines.append('|---|----------|------|------|')
    for i, p in enumerate(papers):
        aid = p['arxiv_id']
        lines.append(f'| {i+1} | {aid} | {p["title"]} | [arXiv](https://arxiv.org/abs/{aid}) · [幻觉翻译](https://hjfy.top/arxiv/{aid}) |')
    lines.append('')
    
    for p in papers:
        aid = p['arxiv_id']
        lines.append(f'## {aid} — {p["title"]}')
        lines.append('')
        lines.append(f'- **arXiv**: [{aid}](https://arxiv.org/abs/{aid})')
        lines.append(f'- **幻觉翻译**: [{aid}](https://hjfy.top/arxiv/{aid})')
        lines.append(f'- **PDF**: [arxiv.org/pdf/{aid}](https://arxiv.org/pdf/{aid})')
        lines.append('')
    
    lines.append('---')
    lines.append('')
    lines.append(f'*自动生成于 {ds} · 基于 arXiv Daily Digest*')
    lines.append('')
    
    return '\n'.join(lines)

def build_and_deploy(date: str):
    """Build Astro site and push."""
    os.chdir(BLOG_DIR)
    
    # Git
    subprocess.run(['git', 'add', 'src/content/blog/', 'public/images/blog/'], capture_output=True)
    r = subprocess.run(['git', 'diff', '--cached', '--stat'], capture_output=True, text=True)
    if '0 files changed' in r.stdout:
        print("  Nothing to commit")
        return
    
    subprocess.run(['git', 'commit', '-m', f'Add paper reading blog for {date}'], capture_output=True)
    subprocess.run(['git', 'push'], capture_output=True)
    print(f"  Pushed: {date}")

def main():
    if len(sys.argv) < 2:
        print("Usage: generate_blog.py YYYY-MM-DD [--deploy]")
        sys.exit(1)
    
    dates = sys.argv[1:]
    do_deploy = '--deploy' in dates
    dates = [d for d in dates if d != '--deploy']
    
    for date in dates:
        print(f"=== {date} ===")
        papers = parse_reading_guide(date)
        print(f"  Papers: {len(papers)}")
        if not papers:
            print("  SKIP")
            continue
        
        figures = download_figures(papers)
        print(f"  Figures: {len(figures)}/{len(papers)}")
        
        md = generate_markdown(date, papers, figures)
        slug = f'{date}-paper-reading'
        md_path = os.path.join(CONTENT_DIR, f'{slug}.md')
        with open(md_path, 'w') as f:
            f.write(md)
        print(f"  Written: {md_path} ({len(md)} chars)")
        
        if do_deploy:
            build_and_deploy(date)

if __name__ == '__main__':
    main()
