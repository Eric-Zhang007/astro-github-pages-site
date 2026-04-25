import { sitePath } from './site';

export const blogCollections = [
  { label: 'Research', slug: 'research', href: 'blog/collections/research/' },
  { label: 'Notes', slug: 'notes', href: 'notes/' },
] as const;

export const comments = {
  walineServerURL: '',
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

export function tagHref(tag: string) {
  return sitePath(`tags/${encodeURIComponent(tag)}/`);
}

export function collectionHref(category = 'Research') {
  const slug = slugify(category);
  return sitePath(`blog/collections/${slug}/`);
}
