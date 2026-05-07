#!/usr/bin/env python3
"""Extract first figure from arxiv HTML page and save to blog images directory."""
import sys, os, re, urllib.request, shutil

BLOG_DIR = '/mnt/c/Users/zjc/astro-github-pages-site'
IMG_DIR = os.path.join(BLOG_DIR, 'public/images/blog')

def extract_figure(arxiv_id: str) -> str | None:
    """Download first figure from arxiv HTML. Returns relative path or None."""
    html_url = f'https://arxiv.org/html/{arxiv_id}v1'
    try:
        html = urllib.request.urlopen(
            urllib.request.Request(html_url, headers={'User-Agent': 'Mozilla/5.0'}),
            timeout=20
        ).read().decode('utf-8', 'replace')
    except Exception:
        return None
    
    figs = re.findall(r'<img[^>]*src="([^"]*x\d+[^"]*\.(?:png|jpg|jpeg))"', html, re.I)
    if not figs:
        return None
    
    # Use the first figure — arxiv src includes version dir, URL uses just filename
    fig_src = figs[0]
    filename = fig_src.rsplit('/', 1)[-1]
    full_url = f'https://arxiv.org/html/{arxiv_id}v1/{filename}'
    
    ext = filename.rsplit('.', 1)[-1].lower()
    if ext not in ('png', 'jpg', 'jpeg'):
        ext = 'png'
    
    local_name = f'paper-{arxiv_id}.{ext}'
    local_path = os.path.join(IMG_DIR, local_name)
    
    try:
        with urllib.request.urlopen(urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=20) as resp:
            with open(local_path, 'wb') as f:
                shutil.copyfileobj(resp, f)
        return f'images/blog/{local_name}'
    except Exception:
        return None

if __name__ == '__main__':
    aid = sys.argv[1] if len(sys.argv) > 1 else None
    if not aid:
        print("Usage: extract_figure.py <arxiv_id>")
        sys.exit(1)
    
    result = extract_figure(aid)
    if result:
        print(f"OK:{result}")
    else:
        print("FAIL:no figure found")
