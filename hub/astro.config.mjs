// @ts-check
import { defineConfig } from 'astro/config';
import icon from 'astro-icon';
import tailwind from '@astrojs/tailwind';

// https://astro.build/config
export default defineConfig({
  site: 'https://violeta-framework.com',
  integrations: [icon(), tailwind()],
});