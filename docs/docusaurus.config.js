// @ts-nocheck
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require("prism-react-renderer/themes/github");
// const darkCodeTheme = require('prism-react-renderer/themes/dracula');
// const DarkTheme = require('@site/src/custom_theme.ts');

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: "My Site",
  tagline: "Dinosaurs are cool",
  favicon: "img/favicon.ico",

  // Set the production url of your site here
  url: "https://your-docusaurus-test-site.com",
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: "/docs/",

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: "facebook", // Usually your GitHub org/user name.
  projectName: "docusaurus", // Usually your repo name.

  onBrokenLinks: "throw",
  onBrokenMarkdownLinks: "warn",

  // Even if you don't use internalization, you can use this field to set useful
  // metadata like html lang. For example, if your site is Chinese, you may want
  // to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: "en",
    locales: ["en", "de"],
    path: "i18n",
    localeConfigs: {
      en: {
        label: "English",
      },
      de: {
        label: "Deutsch",
      },
    },
  },

  presets: [
    [
      "classic",
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          routeBasePath: "/",
          sidebarPath: require.resolve("./sidebars.js"),
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            "https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/",

          lastVersion: "current",
          versions: {
            current: {
              label: "1.5",
              path: "1.5",
            },
          },
        },
        // blog: {
        //   showReadingTime: true,
        //   // Please change this to your repo.
        //   // Remove this to remove the "edit this page" links.
        //   editUrl:
        //     "https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/",
        // },
        theme: {
          customCss: require.resolve("./src/css/custom.css"),
        },
      }),
    ],
    // [
    //   'redocusaurus',
    //   {
    //     // Plugin Options for loading OpenAPI files
    //     specs: [
    //       {
    //         spec: './openapi.json', //https://v2.goat.plan4better.de/api/v1/openapi.json
    //         route: '/api/',
    //       },
    //     ],
    //     // Theme Options for modifying how redoc renders them
    //     theme: {
    //       primaryColor: '#2BB381',
    //       theme: {
    //         // sidebar:{
    //         //   backgroundColor: '#F8F7F3',
    //         // },
    //       },
    //     },
    //   },
    // ]
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: "img/docusaurus-social-card.jpg",
      navbar: {
        logo: {
          alt: "Plan4Better",
          src: "https://assets.plan4better.de/img/logo/plan4better_standard.svg",
        },
        items: [
          {
            type: "docSidebar",
            sidebarId: "tutorialSidebar",
            position: "left",
            label: "Docs",
          },
          // {
          //   to: "/api",
          //   label: "Api",
          //   position: "left",
          // },
          {
            to: "/Storybook",
            label: "Storybook",
            position: "left",
          },
          {
            to: "https://plan4better.de/en/blog/",
            label: "Blog",
            position: "left",
          },
          {
            type: "localeDropdown",
            position: "right",
            dropdownItemsAfter: [
              {
                to: "https://my-site.com/help-us-translate",
              },
            ],
          },
          {
            type: "docsVersionDropdown",
            position: "right",
            dropdownActiveClassDisabled: true,
          },
          {
            href: "https://github.com/goat-community/goat",
            label: "GitHub",
            position: "right",
          },
        ],
      },
      footer: {
        links: [
          {
            title: "Subscribe To Newsletter",
            items: [
              {
                html: `
                  <div>
                    <input type="email" placeholder="Enter your email" class="input_subscription"/>
                    <button class="subscription_button">Subscribe</button>
                  </div>
                `,
              },
            ],
          },
          {
            title: "Docs",
            items: [
              {
                label: "Software Architecture",
                to: "/",
              },
              {
                label: "Frontend",
                to: "/",
              },
              {
                label: "Data Preperation",
                to: "/",
              },
            ],
          },
          {
            title: "Community",
            items: [
              {
                label: "Linkedin",
                href: "https://www.linkedin.com/company/plan4better/",
              },
              {
                label: "Github",
                href: "https://discordapp.com/invite/docusaurus",
              },
              {
                label: "Twitter",
                href: "https://github.com/goat-community/",
              },
            ],
          },
          {
            title: "More",
            items: [
              {
                label: "Blog",
                to: "https://plan4better.de/en/blog/",
              },
              {
                label: "References",
                href: "https://plan4better.de/en/references/",
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Plan4Better, Inc. Built with Docusaurus.`,
      },
    }),
};

module.exports = config;
