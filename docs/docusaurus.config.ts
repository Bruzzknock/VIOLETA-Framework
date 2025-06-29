import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'VIOLETA Docs',
  tagline: 'VIOLETA is a practical blueprint for turning any learning objective into a playable experience in which fun, emotion and adaptive challenge are all deliberately engineered to drive real-world skill mastery.',
  favicon: 'img/logo.svg',

  // Future flags, see https://docusaurus.io/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://violeta-framework.com',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/docs/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'Bruzzknock', // Usually your GitHub org/user name.
  projectName: 'VIOLETA-Framework', // Usually your repo name.

  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          routeBasePath: '/',
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/Bruzzknock/VIOLETA-Framework/',
        },
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/Bruzzknock/VIOLETA-Framework/blog/',
          // Useful options to enforce blogging best practices
          onInlineTags: 'warn',
          onInlineAuthors: 'warn',
          onUntruncatedBlogPosts: 'warn',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    // Replace with your project's social card
    image: 'img/logo.svg',
    navbar: {
      title: 'VIOLETA Docs',
      logo: {
        alt: 'VIOLETA Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',       // <— NEW
          sidebarId: 'theorySidebar',
          position: 'left',
          label: 'Theory',
        },
        {href: 'https://medium.com/@kristijan.djokic', label: 'Blog', position: 'left'},
        {
          href: 'https://github.com/Bruzzknock/VIOLETA-Framework',
          label: 'GitHub',
          position: 'right',
        },
        {
          type: 'docsVersionDropdown',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Theory',
              to: '/theory',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'Discord',
              href: 'https://discord.gg/KbShmvV8fv',
            },
            {
              label: 'Reddit',
              href: 'https://www.reddit.com/r/VIOLETAFramework/',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'Blog',
              href: 'https://medium.com/@kristijan.djokic',
            },
            {
              label: 'GitHub',
              href: 'https://github.com/Bruzzknock/VIOLETA-Framework',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} VIOLETA Framework, Inc. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
