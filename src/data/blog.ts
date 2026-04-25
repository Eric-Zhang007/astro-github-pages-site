import { sitePath } from './site';

export type SectionKey = 'blog' | 'research' | 'notes' | 'projects';

export type OwnerCollection = {
  label: string;
  slug: string;
  href: string;
};

export const siteOwner = {
  githubLogin: 'Eric-Zhang007',
  repo: 'Eric-Zhang007/astro-github-pages-site',
  branch: 'main',
} as const;

export const sectionCollections: Record<SectionKey, OwnerCollection[]> = {
  blog: [
    { label: 'World Models', slug: 'world-models', href: 'blog/collections/world-models/' },
  ],
  research: [],
  notes: [],
  projects: [],
} as const;

export const comments = {
  provider: 'utterances',
  enabled: true,
  repo: 'Eric-Zhang007/astro-github-pages-site',
  issueTerm: 'pathname',
  label: 'comment',
  theme: 'github-dark-orange',
} as const;

export function slugify(value: string) {
  return value
    .trim()
    .toLowerCase()
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^\p{L}\p{N}]+/gu, '-')
    .replace(/^-+|-+$/g, '');
}

export function uniqueTags(items: Array<{ data?: { tags?: string[] }; tags?: string[] }>) {
  return Array.from(new Set(items.flatMap((item) => item.data?.tags ?? item.tags ?? []))).sort((a, b) => a.localeCompare(b));
}

export function tagHref(tag: string) {
  return sitePath(`tags/${encodeURIComponent(tag)}/`);
}

export function collectionHref(section: SectionKey, slug: string) {
  return sitePath(`${section}/collections/${slug}/`);
}
