// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require('prism-react-renderer').themes.github;
const darkCodeTheme = require('prism-react-renderer').themes.dracula;

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'A comprehensive 13-week curriculum for learning Physical AI and building autonomous humanoid robots',
  favicon: 'img/favicon.ico',

  // Set the production url of your site here
  url: 'https://nailaimran.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/',

  // GitHub pages deployment config.
  organizationName: 'NailaImran', // Usually your GitHub org/user name.
  projectName: 'ai-driven-robo-book', // Usually your repo name.
  deploymentBranch: 'gh-pages',
  trailingSlash: false,

  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',

  // Internationalization (Urdu disabled until translations are added)
  i18n: {
    defaultLocale: 'en',
    locales: ['en'], // Only English for now
    localeConfigs: {
      en: {
        label: 'English',
        direction: 'ltr',
        htmlLang: 'en-US',
      },
      // Urdu will be enabled after translations are complete
      // ur: {
      //   label: 'اردو',
      //   direction: 'rtl',
      //   htmlLang: 'ur-PK',
      // },
    },
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/NailaImran/ai-driven-robo-book/tree/main/website/',
          // Math plugins disabled until packages are installed
          // remarkPlugins: [require('remark-math')],
          // rehypePlugins: [require('rehype-katex')],
        },
        blog: false, // Disable blog
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  // Mermaid support is built-in with Docusaurus 3.x
  markdown: {
    mermaid: true,
  },

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/social-card.png',

      // Color mode configuration
      colorMode: {
        defaultMode: 'light',
        disableSwitch: false,
        respectPrefersColorScheme: true,
      },

      navbar: {
        title: 'Physical AI & Humanoid Robotics',
        logo: {
          alt: 'Robot Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'docsSidebar',
            position: 'left',
            label: 'Textbook',
          },
          {
            type: 'localeDropdown',
            position: 'right',
          },
          {
            href: 'https://github.com/NailaImran/ai-driven-robo-book',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },

      footer: {
        style: 'dark',
        links: [
          {
            title: 'Learn',
            items: [
              {
                label: 'Introduction',
                to: '/docs/introduction',
              },
              {
                label: 'Course Overview',
                to: '/docs/introduction/course-overview',
              },
              {
                label: 'Capstone Project',
                to: '/docs/capstone',
              },
            ],
          },
          {
            title: 'Resources',
            items: [
              {
                label: 'ROS 2 Documentation',
                href: 'https://docs.ros.org/en/humble/',
              },
              {
                label: 'NVIDIA Isaac',
                href: 'https://developer.nvidia.com/isaac',
              },
              {
                label: 'Gazebo',
                href: 'https://gazebosim.org/',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/NailaImran/ai-driven-robo-book',
              },
              {
                label: 'Discussions',
                href: 'https://github.com/NailaImran/ai-driven-robo-book/discussions',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Physical AI & Humanoid Robotics Textbook. Built with Docusaurus.`,
      },

      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
        additionalLanguages: ['python', 'bash', 'cpp', 'yaml', 'json'],
      },

      // Algolia search (configure later)
      // algolia: {
      //   appId: 'YOUR_APP_ID',
      //   apiKey: 'YOUR_SEARCH_API_KEY',
      //   indexName: 'humanoid_robotics',
      // },

      // Mermaid theme
      mermaid: {
        theme: {light: 'neutral', dark: 'dark'},
        options: {
          maxTextSize: 50000,
        },
      },

      // Announcement bar
      announcementBar: {
        id: 'announcement_bar',
        content:
          '⭐ If you find this textbook helpful, give it a star on <a target="_blank" rel="noopener noreferrer" href="https://github.com/NailaImran/ai-driven-robo-book">GitHub</a>!',
        backgroundColor: '#4CAF50',
        textColor: '#FFFFFF',
        isCloseable: true,
      },

      // Table of contents
      tableOfContents: {
        minHeadingLevel: 2,
        maxHeadingLevel: 5,
      },

      // Docs sidebar
      docs: {
        sidebar: {
          hideable: true,
          autoCollapseCategories: true,
        },
      },
    }),

  // KaTeX stylesheets disabled until plugins are installed
  // stylesheets: [
  //   {
  //     href: 'https://cdn.jsdelivr.net/npm/katex@0.13.24/dist/katex.min.css',
  //     type: 'text/css',
  //   },
  // ],
};

module.exports = config;
