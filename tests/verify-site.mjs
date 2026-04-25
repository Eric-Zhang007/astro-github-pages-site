import { existsSync, readFileSync } from 'node:fs';
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
];

for (const page of requiredPages) {
  const file = join(dist, page);
  if (!existsSync(file)) {
    throw new Error(`Missing built page: ${page}`);
  }
}

const homepage = readFileSync(join(dist, 'index.html'), 'utf8');
const blog = readFileSync(join(dist, 'blog/index.html'), 'utf8');
const research = readFileSync(join(dist, 'research/index.html'), 'utf8');

const forbidden = [
  'Reading notes on world models',
  'Visual risk understanding for driving agents',
  'Object-centric reasoning and physical prediction',
  'writing heatmap',
  'Papers in Zotero',
  'Local PDFs',
  'Notes to write',
  'hello@example.com',
  '491',
  '41',
  '∞',
];

for (const text of forbidden) {
  if (homepage.includes(text) || blog.includes(text) || research.includes(text)) {
    throw new Error(`Found placeholder/fake content: ${text}`);
  }
}

const expectedHomepage = [
  'href="/astro-github-pages-site/blog/"',
  'href="/astro-github-pages-site/research/"',
  'No blog posts yet',
  'No activity yet',
  'Research interests',
  'Education',
];

for (const text of expectedHomepage) {
  if (!homepage.includes(text)) {
    throw new Error(`Homepage missing expected real-state content: ${text}`);
  }
}

if (!blog.includes('No blog posts yet')) {
  throw new Error('Blog page should show a truthful empty state when there are no posts.');
}

if (!research.includes('World models')) {
  throw new Error('Research page should include the real research interests.');
}

console.log('Site verification passed');
