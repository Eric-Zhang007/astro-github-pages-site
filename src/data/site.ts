export const basePath = import.meta.env.BASE_URL;

export const profile = {
  name: 'Eric Zhang',
  brand: "Eric's Blog",
  location: 'China',
  github: 'https://github.com/Eric-Zhang007',
  email: '',
  intro:
    '学生 / AI researcher. 关注 world models、自动驾驶、视觉风险理解、VLM / video reasoning、object-centric reasoning 与 embodied intelligence。',
};

export const navItems = [
  { label: 'Blog', href: 'blog/' },
  { label: 'Research', href: 'research/' },
  { label: 'Notes', href: 'notes/' },
  { label: 'Projects', href: 'projects/' },
  { label: 'Links', href: 'links/' },
  { label: 'About', href: 'about/' },
];

export const researchInterests = [
  'World models for autonomous driving',
  'Visual collision / accident anticipation',
  'Object-centric and scene-graph reasoning',
  'VLM / video reasoning',
  'Embodied intelligence',
];

export const educationEntries: Array<{
  school: string;
  degree: string;
  period: string;
  description?: string;
}> = [];

export const blogPosts: Array<{
  title: string;
  date: string;
  href: string;
  summary?: string;
}> = [];

export const notes: Array<{
  title: string;
  date: string;
  href: string;
  summary?: string;
}> = [];

export const projects: Array<{
  title: string;
  href: string;
  summary?: string;
  tags?: string[];
}> = [];

export const links = [
  { label: 'GitHub', href: profile.github, description: '代码与项目主页' },
];

export const activities: Array<{
  date: string;
  title: string;
  href?: string;
}> = [];

export const stats = [
  { label: 'Blog posts', value: blogPosts.length },
  { label: 'Notes', value: notes.length },
  { label: 'Projects', value: projects.length },
  { label: 'Activities', value: activities.length },
];

export function sitePath(path = '') {
  const normalizedBase = basePath.endsWith('/') ? basePath : `${basePath}/`;
  const normalizedPath = path.startsWith('/') ? path.slice(1) : path;
  return `${normalizedBase}${normalizedPath}`;
}
