import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/docs/de/blog',
    component: ComponentCreator('/docs/de/blog', 'd5f'),
    exact: true
  },
  {
    path: '/docs/de/blog/archive',
    component: ComponentCreator('/docs/de/blog/archive', '3a9'),
    exact: true
  },
  {
    path: '/docs/de/blog/first-blog-post',
    component: ComponentCreator('/docs/de/blog/first-blog-post', 'c27'),
    exact: true
  },
  {
    path: '/docs/de/blog/long-blog-post',
    component: ComponentCreator('/docs/de/blog/long-blog-post', '36d'),
    exact: true
  },
  {
    path: '/docs/de/blog/mdx-blog-post',
    component: ComponentCreator('/docs/de/blog/mdx-blog-post', 'a7d'),
    exact: true
  },
  {
    path: '/docs/de/blog/tags',
    component: ComponentCreator('/docs/de/blog/tags', '40a'),
    exact: true
  },
  {
    path: '/docs/de/blog/tags/docusaurus',
    component: ComponentCreator('/docs/de/blog/tags/docusaurus', '04e'),
    exact: true
  },
  {
    path: '/docs/de/blog/tags/facebook',
    component: ComponentCreator('/docs/de/blog/tags/facebook', 'eaa'),
    exact: true
  },
  {
    path: '/docs/de/blog/tags/hello',
    component: ComponentCreator('/docs/de/blog/tags/hello', '983'),
    exact: true
  },
  {
    path: '/docs/de/blog/tags/hola',
    component: ComponentCreator('/docs/de/blog/tags/hola', 'cc3'),
    exact: true
  },
  {
    path: '/docs/de/blog/welcome',
    component: ComponentCreator('/docs/de/blog/welcome', '28d'),
    exact: true
  },
  {
    path: '/docs/de/markdown-page',
    component: ComponentCreator('/docs/de/markdown-page', '794'),
    exact: true
  },
  {
    path: '/docs/de/search',
    component: ComponentCreator('/docs/de/search', 'bc3'),
    exact: true
  },
  {
    path: '/docs/de/Storybook',
    component: ComponentCreator('/docs/de/Storybook', '1dc'),
    exact: true
  },
  {
    path: '/docs/de/2.0',
    component: ComponentCreator('/docs/de/2.0', 'e26'),
    routes: [
      {
        path: '/docs/de/2.0/',
        component: ComponentCreator('/docs/de/2.0/', 'ac0'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/category/accessibility-indicators',
        component: ComponentCreator('/docs/de/2.0/category/accessibility-indicators', 'd86'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/category/data',
        component: ComponentCreator('/docs/de/2.0/category/data', '70b'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/category/data-management',
        component: ComponentCreator('/docs/de/2.0/category/data-management', 'adf'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/category/geoanalysis',
        component: ComponentCreator('/docs/de/2.0/category/geoanalysis', '3c9'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/category/geoprocessing',
        component: ComponentCreator('/docs/de/2.0/category/geoprocessing', 'a86'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/category/layer-styling',
        component: ComponentCreator('/docs/de/2.0/category/layer-styling', '88a'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/category/literature',
        component: ComponentCreator('/docs/de/2.0/category/literature', '4da'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/category/map',
        component: ComponentCreator('/docs/de/2.0/category/map', '1b9'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/category/routing',
        component: ComponentCreator('/docs/de/2.0/category/routing', 'ef2'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/category/technical-insights',
        component: ComponentCreator('/docs/de/2.0/category/technical-insights', 'a06'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/category/toolbox',
        component: ComponentCreator('/docs/de/2.0/category/toolbox', '541'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/category/workspace',
        component: ComponentCreator('/docs/de/2.0/category/workspace', 'bda'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/data/data_basis',
        component: ComponentCreator('/docs/de/2.0/data/data_basis', '991'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/data/data_types',
        component: ComponentCreator('/docs/de/2.0/data/data_types', 'f62'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/data/dataset_types',
        component: ComponentCreator('/docs/de/2.0/data/dataset_types', '328'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/further_reading/glossary',
        component: ComponentCreator('/docs/de/2.0/further_reading/glossary', '3cf'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/further_reading/publications',
        component: ComponentCreator('/docs/de/2.0/further_reading/publications', 'a09'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/map/filter',
        component: ComponentCreator('/docs/de/2.0/map/filter', 'e18'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/map/interface_overview',
        component: ComponentCreator('/docs/de/2.0/map/interface_overview', 'e34'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/map/layer_style/attribute_based_styling',
        component: ComponentCreator('/docs/de/2.0/map/layer_style/attribute_based_styling', '849'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/map/layer_style/styling',
        component: ComponentCreator('/docs/de/2.0/map/layer_style/styling', '203'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/map/layers',
        component: ComponentCreator('/docs/de/2.0/map/layers', '70e'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/nerdy_content/architecture',
        component: ComponentCreator('/docs/de/2.0/nerdy_content/architecture', 'f89'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/routing/bicycle',
        component: ComponentCreator('/docs/de/2.0/routing/bicycle', '9e0'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/routing/car',
        component: ComponentCreator('/docs/de/2.0/routing/car', 'f29'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/routing/public_transport',
        component: ComponentCreator('/docs/de/2.0/routing/public_transport', '6cd'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/routing/walking',
        component: ComponentCreator('/docs/de/2.0/routing/walking', 'e52'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/sharing',
        component: ComponentCreator('/docs/de/2.0/sharing', 'bcd'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/Szenarien',
        component: ComponentCreator('/docs/de/2.0/Szenarien', '35f'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/toolbox/accessibility_indicators/catchments',
        component: ComponentCreator('/docs/de/2.0/toolbox/accessibility_indicators/catchments', '398'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/toolbox/accessibility_indicators/closest_average',
        component: ComponentCreator('/docs/de/2.0/toolbox/accessibility_indicators/closest_average', '119'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/toolbox/accessibility_indicators/connectivity',
        component: ComponentCreator('/docs/de/2.0/toolbox/accessibility_indicators/connectivity', '513'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/toolbox/accessibility_indicators/gravity',
        component: ComponentCreator('/docs/de/2.0/toolbox/accessibility_indicators/gravity', '2e7'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/toolbox/accessibility_indicators/nearby_stations',
        component: ComponentCreator('/docs/de/2.0/toolbox/accessibility_indicators/nearby_stations', 'c56'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/toolbox/accessibility_indicators/oev_gueteklassen',
        component: ComponentCreator('/docs/de/2.0/toolbox/accessibility_indicators/oev_gueteklassen', 'be2'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/toolbox/accessibility_indicators/pt_trip_count',
        component: ComponentCreator('/docs/de/2.0/toolbox/accessibility_indicators/pt_trip_count', '5be'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/toolbox/data_management/join',
        component: ComponentCreator('/docs/de/2.0/toolbox/data_management/join', 'cb5'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/toolbox/data_management/spatial_join',
        component: ComponentCreator('/docs/de/2.0/toolbox/data_management/spatial_join', 'a42'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/toolbox/geoanalysis/aggregate_points',
        component: ComponentCreator('/docs/de/2.0/toolbox/geoanalysis/aggregate_points', '7cc'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/toolbox/geoanalysis/aggregate_polygons',
        component: ComponentCreator('/docs/de/2.0/toolbox/geoanalysis/aggregate_polygons', '731'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/toolbox/geoanalysis/origin_destination',
        component: ComponentCreator('/docs/de/2.0/toolbox/geoanalysis/origin_destination', '51b'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/toolbox/geoprocessing/buffer',
        component: ComponentCreator('/docs/de/2.0/toolbox/geoprocessing/buffer', 'b11'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/workspace/catalog',
        component: ComponentCreator('/docs/de/2.0/workspace/catalog', 'e40'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/workspace/datasets',
        component: ComponentCreator('/docs/de/2.0/workspace/datasets', 'f8e'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/workspace/home',
        component: ComponentCreator('/docs/de/2.0/workspace/home', '58e'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/workspace/projects',
        component: ComponentCreator('/docs/de/2.0/workspace/projects', '0a2'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/de/2.0/workspace/settings',
        component: ComponentCreator('/docs/de/2.0/workspace/settings', 'bdb'),
        exact: true,
        sidebar: "tutorialSidebar"
      }
    ]
  },
  {
    path: '/docs/de/',
    component: ComponentCreator('/docs/de/', '86b'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
