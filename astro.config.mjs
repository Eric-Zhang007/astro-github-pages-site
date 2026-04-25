import { defineConfig } from 'astro/config';

const repo = process.env.GITHUB_REPOSITORY?.split('/')[1];
const isUserOrOrgPage = repo?.endsWith('.github.io');

export default defineConfig({
  site: process.env.GITHUB_PAGES_URL || 'https://example.github.io',
  base: repo && !isUserOrOrgPage ? `/${repo}` : '/',
});
