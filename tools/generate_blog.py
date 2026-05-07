#!/usr/bin/env python3
"""Generate card-style paper-reading blog posts matching axi404 layout."""
import sys, os, re, subprocess, datetime, yaml

BLOG_DIR = '/mnt/c/Users/zjc/astro-github-pages-site'
CONTENT_DIR = os.path.join(BLOG_DIR, 'src/content/blog')
PAPERS_DIR = '/mnt/c/Users/zjc/Desktop/papers'
FIGURE_SCRIPT = os.path.join(BLOG_DIR, 'tools/extract_figure.py')

def extract_figure(arxiv_id: str) -> str | None:
    r = subprocess.run(['python3', FIGURE_SCRIPT, arxiv_id], capture_output=True, text=True, timeout=30)
    if r.returncode == 0 and r.stdout.startswith('OK:'):
        return r.stdout.strip()[3:]
    return None

def extract_arxiv_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as f: data = f.read(100000)
        ids = re.findall(r'(\d{4}\.\d{4,5})', data.decode('latin-1', errors='replace'))
        if ids:
            from collections import Counter
            return Counter(ids).most_common(1)[0][0]
    except: pass
    return None

def extract_title_from_pdf_name(fname):
    base = fname.replace('.pdf', '')
    base = re.sub(r'^\d+\s*-\s*', '', base).strip()
    return base

def normalize_title(title: str) -> str:
    """Remove leading number prefix like '1. ' or '**'."""
    title = re.sub(r'^\*?\d+\.?\s*', '', title).strip().strip('*')
    return title

def get_papers_from_date(date: str) -> list[dict]:
    guide_path = os.path.join(PAPERS_DIR, date, 'READING_GUIDE.md')
    papers = []
    if os.path.exists(guide_path):
        with open(guide_path) as f: text = f.read()
        for m in re.finditer(r'\|\s*\d+\s*\|\s*([\d.]+)\s*\|\s*(.+?)\s*\|', text):
            aid, title = m.group(1).strip(), m.group(2).strip()
            if len(aid) >= 8 and aid.count('.') >= 1:
                if not any(p['arxiv_id'] == aid for p in papers):
                    papers.append({'arxiv_id': aid, 'title': normalize_title(title)})
        for m in re.finditer(r'`(\d{4}\.\d{4,5})`', text):
            aid = m.group(1)
            title_m = re.search(r'\*\*([^*]+)\*\*', text[m.start():m.start()+500])
            title = normalize_title(title_m.group(1)) if title_m else aid
            if not any(p['arxiv_id'] == aid for p in papers):
                papers.append({'arxiv_id': aid, 'title': title})
    if not papers:
        papers_dir = os.path.join(PAPERS_DIR, date)
        if os.path.isdir(papers_dir):
            for fname in sorted(os.listdir(papers_dir)):
                if fname.endswith('.pdf'):
                    pdf_path = os.path.join(papers_dir, fname)
                    aid = extract_arxiv_from_pdf(pdf_path)
                    title = extract_title_from_pdf_name(fname)
                    if aid and title: papers.append({'arxiv_id': aid, 'title': title})
    if not papers and os.path.exists(guide_path):
        with open(guide_path) as f: text = f.read()
        for aid in set(re.findall(r'(\d{4}\.\d{4,5})', text)):
            if not any(p['arxiv_id'] == aid for p in papers):
                papers.append({'arxiv_id': aid, 'title': aid})
    return papers[:12]

def extract_summaries(date: str) -> dict:
    """Extract one-line summaries from READING_GUIDE."""
    guide_path = os.path.join(PAPERS_DIR, date, 'READING_GUIDE.md')
    summaries = {}
    if not os.path.exists(guide_path): return summaries
    with open(guide_path) as f: text = f.read()
    
    # Try to find summary lines near paper references
    for m in re.finditer(r'(?:`|^)(\d{4}\.\d{4,5})(?:`)?\s*[|—–-]?\s*(.+?)(?:\n|$)', text, re.M):
        aid = m.group(1)
        desc = m.group(2).strip().rstrip('|').strip()
        if len(desc) > 5 and len(desc) < 200:
            summaries[aid] = desc
    
    # Also try "一句话理由" lines
    for m in re.finditer(r'一句话理由[：:]\s*(.+)', text):
        line = m.group(1).strip()
        # Find the nearest arxiv ID before this line
        prev = text[:m.start()]
        ids = re.findall(r'(\d{4}\.\d{4,5})', prev)
        if ids:
            summaries[ids[-1]] = line[:150]
    
    return summaries

def gen(date: str, papers: list[dict], do_deploy: bool):
    dt = datetime.datetime.strptime(date, '%Y-%m-%d')
    ds = dt.strftime('%Y-%m-%d')
    n = len(papers)
    
    # Download figures
    figures = {}
    for p in papers:
        aid = p['arxiv_id']
        local = f'images/blog/paper-{aid}.png'
        if os.path.exists(os.path.join(BLOG_DIR, 'public', local)):
            figures[aid] = local
        else:
            result = extract_figure(aid)
            if result: figures[aid] = result
    
    # Extract summaries
    summaries = extract_summaries(date)
    
    fm = {
        'title': f'{ds} Paper Reading',
        'description': f'今日 arXiv 论文速读：{n} 篇入选 shortlist。',
        'date': ds,
        'tags': ['paper reading', 'arXiv'],
        'category': 'Research',
        'comments': True,
        'draft': False,
    }
    
    lines = ['---', yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False).strip(), '---', '']
    
    # Brief intro line
    lines.append(f'今日从 arXiv 订阅中筛选 {n} 篇论文。')
    lines.append('')
    
    # Each paper as a card
    for i, p in enumerate(papers):
        aid = p['arxiv_id']
        title = p['title']
        summary = summaries.get(aid, '')
        
        lines.append(f'<div class="paper-card">')
        lines.append('')
        
        # Pill links row
        lines.append(f'<div class="paper-links paper-links-inline">'
                     f'<a href="https://arxiv.org/abs/{aid}" target="_blank" rel="noreferrer">'
                     f'<span>Arxiv ID</span>{aid}</a>'
                     f'<a href="https://hjfy.top/arxiv/{aid}" target="_blank" rel="noreferrer">'
                     f'<span>幻觉翻译</span>{aid}</a>'
                     f'</div>')
        lines.append('')
        
        # Title with number
        lines.append(f'<h2 class="paper-card-title">⚡ {title}</h2>')
        lines.append('')
        
        # Summary line if available
        if summary:
            lines.append(f'<p class="paper-card-summary">{summary}</p>')
            lines.append('')
        
        # Image
        if aid in figures:
            lines.append(f'<figure class="paper-card-figure">'
                         f'<img src="/{figures[aid]}" alt="{title}" loading="lazy" />'
                         f'</figure>')
            lines.append('')
        
        lines.append('</div>')
        lines.append('')
    
    lines.append('---')
    lines.append(f'*自动生成于 {ds} · 基于 arXiv Daily Digest*')
    lines.append('')
    
    md_content = '\n'.join(lines)
    slug = f'{date}-paper-reading'
    md_path = os.path.join(CONTENT_DIR, f'{slug}.md')
    with open(md_path, 'w') as f: f.write(md_content)
    
    print(f"  {date}: {n} papers, {len(figures)} figures → {md_path} ({len(md_content)} chars)")
    
    if do_deploy:
        os.chdir(BLOG_DIR)
        subprocess.run(['git', 'add', 'src/content/blog/', 'public/images/blog/'], capture_output=True)
        r = subprocess.run(['git', 'diff', '--cached', '--stat'], capture_output=True, text=True)
        if '0 files changed' not in r.stdout:
            subprocess.run(['git', 'commit', '-m', f'Card-style paper reading layout for {date}'], capture_output=True)
            subprocess.run(['git', 'push'], capture_output=True)
            print(f"  Deployed!")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: generate_blog.py YYYY-MM-DD [--deploy]"); sys.exit(1)
    dates = sys.argv[1:]; do_deploy = '--deploy' in dates
    dates = [d for d in dates if d != '--deploy']
    for date in dates:
        papers = get_papers_from_date(date)
        if not papers: print(f"  {date}: SKIP"); continue
        gen(date, papers, do_deploy)
