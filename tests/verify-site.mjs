import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';

const root = new URL('..', import.meta.url).pathname;
const dist = join(root, 'dist');
const requiredPages = [
  'index.html',
  'blog/index.html',
  'research/index.html',
  'notes/index.html',
  'projects/index.html',
  'links/index.html',
  'about/index.html',
  'login/index.html',
  'blog/jepa-introduction/index.html',
  'tags/JEPA/index.html',
  'tags/world model/index.html',
];

for (const page of requiredPages) {
  const file = join(dist, page);
  if (!existsSync(file)) {
    throw new Error(`Missing built page: ${page}`);
  }
}

const read = (page) => readFileSync(join(dist, page), 'utf8');
const homepage = read('index.html');
const blog = read('blog/index.html');
const research = read('research/index.html');
const notes = read('notes/index.html');
const projects = read('projects/index.html');
const article = read('blog/jepa-introduction/index.html');
const login = read('login/index.html');
const css = readdirSync(join(dist, '_astro'))
  .filter((file) => file.endsWith('.css'))
  .map((file) => readFileSync(join(dist, '_astro', file), 'utf8'))
  .join('\n');

const forbidden = [
  'Reading notes on world models',
  'Visual risk understanding for driving agents',
  'Object-centric reasoning and physical prediction',
  'writing heatmap',
  'Papers in Zotero',
  'Local PDFs',
  'Notes to write',
  'hello@example.com',
  'No blog posts yet',
  'No activity yet',
  'No projects yet',
  'No notes yet',
  '后续补充',
  '会出现在这里',
  '没有内容时',
  '真实方向',
  '真实经历',
];

for (const text of forbidden) {
  for (const [name, html] of Object.entries({ homepage, blog, research, notes, projects, article })) {
    if (html.includes(text)) {
      throw new Error(`Found placeholder/fake content in ${name}: ${text}`);
    }
  }
}

const pageChecks = {
  homepage: ['href="/astro-github-pages-site/blog/"', 'href="/astro-github-pages-site/research/"'],
  blog: ['Collections', 'Tags', 'href="/astro-github-pages-site/tags/JEPA/"', 'View all posts by years', 'jepa-introduction'],
  research: ['Page 1 - Showing 5 of 5 interests', 'Collections', 'Tags', 'Research interests'],
  notes: ['Page 1 - Showing 0 of 0 notes', 'Collections', 'Tags'],
  projects: ['Page 1 - Showing 0 of 0 projects', 'Collections', 'Tags'],
  article: ['toc-panel', 'Comments', 'Arxiv ID', '幻觉翻译', 'paper-figure-link', 'collection-list', 'World Models', 'article-info-card', 'Buy me a cup of coffee', 'post-neighbors', 'CC BY-NC-SA 4.0'],
  login: ['Content manager', 'GitHub token', 'Only', 'Commit post to GitHub', 'New collection label', 'arXiv ID'],
};

for (const [name, needles] of Object.entries(pageChecks)) {
  const html = { homepage, blog, research, notes, projects, article, login }[name];
  for (const needle of needles) {
    if (!html.includes(needle)) {
      throw new Error(`${name} missing expected content: ${needle}`);
    }
  }
}

for (const needle of ['cursor-ring', 'cursor-dot', 'cursor-trail', 'cursor-ripple', 'cursor-hover', 'has-custom-cursor *{cursor:none!important}']) {
  if (!article.includes(needle) && !css.includes(needle)) {
    throw new Error(`Missing visible cursor marker: ${needle}`);
  }
}

if (blog.includes('blog/collections/research') || blog.includes('blog/collections/notes')) {
  throw new Error('Blog collections still point to Research/Notes as fake collections.');
}

if (!blog.includes('blog/collections/world-models/')) {
  throw new Error('Configured Blog collection is missing.');
}

if (homepage.includes('login/')) {
  throw new Error('Login should stay hidden from homepage navigation.');
}

if (research.includes('href="/astro-github-pages-site/tags/World%20models')) {
  throw new Error('Research tags are not article-derived; research interests should not become tag links.');
}

console.log('Site verification passed');
