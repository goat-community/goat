const data = {
  items: [
    {
      content_id: "1",
      name: "test",
      tags: ["tag1", "tag2", "tag3"],
      description: "test description",
      url: "https://geoservice.plan4better.de/tiles/xxxxx",
      thumbnail_url: "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png",
      owner: {
        id: "1",
        first_name: "test",
        last_name: "test",
        email: "test@plan4better.de",
      },
      metadata: {
        size: "123456",
        updated_by: "test@plan4better.de",
        created_at: "2020-01-01 00:00:00",
        updated_at: "2020-01-01 00:00:00",
      },
      shared_with: {
        groups: [
          {
            group_id: 1,
            group_name: "My Group 1",
            image_url: "https://assets.plan4better.de/api/thumbnail/1.png",
            permissions: ["view", "edit", "download"],
          },
          {
            group_id: 2,
            group_name: "My Group 2",
            image_url: "https://assets.plan4better.de/api/thumbnail/2.png",
            permissions: ["view", "edit", "download"],
          },
        ],
        public: {
          url: "https://geoservice.plan4better.de/tiles/xxxxx",
          expiration_date: "2024-01-01 00:00:00",
          password_enabled: true,
        },
      },
      type: "layer",
      layer_type: "feature_layer",
      feature_layer_type: "indicator",
      data_type: "mvt",
      style_id: "1234",
    },
    {
      content_id: "2",
      name: "test",
      tags: ["tag1", "tag2", "tag3"],
      description: "test description",
      url: "https://geoservice.plan4better.de/wms/xxxxx",
      thumbnail_url: "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png",
      owner: {
        id: "1",
        first_name: "test",
        last_name: "test",
        email: "test@plan4better.de",
      },
      metadata: {
        size: "123456",
        updated_by: "test@plan4better.de",
        created_at: "2020-01-01 00:00:00",
        updated_at: "2020-01-01 00:00:00",
      },
      shared_with: {
        organization: {
          permissions: ["view", "edit", "download"],
        },
        public: {
          url: "https://geoservice.plan4better.de/tiles/xxxxx",
          expiration_date: "2024-01-01 00:00:00",
          password_enabled: true,
        },
      },
      type: "layer",
      layer_type: "imagery_layer",
      data_type: "wms",
      legend_urls: [
        "https://geoservice.plan4better.de/wms/xxxxx?request=GetLegendGraphic&format=image/png&width=20&height=20&layer=xxxxx",
      ],
    },
    {
      content_id: "3",
      name: "test_project",
      tags: ["tag1", "tag2", "tag3"],
      description: "test description",
      thumbnail_url: "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png",
      owner: {
        id: "1",
        first_name: "test",
        last_name: "test",
        email: "test@plan4better.de",
      },
      metadata: {
        size: 1000,
        updated_by: "test@plan4better.de",
        created_at: "2020-01-01 00:00:00",
        updated_at: "2020-01-01 00:00:00",
      },
      shared_with: {
        groups: [
          {
            group_id: 1,
            group_name: "My Group 1",
            image_url: "https://assets.plan4better.de/api/thumbnail/1.png",
            permissions: ["view", "edit", "download"],
          },
          {
            group_id: 2,
            group_name: "My Group 2",
            image_url: "https://assets.plan4better.de/api/thumbnail/2.png",
            permissions: ["view", "edit", "download"],
          },
        ],
      },
      type: "project",
    },
  ],
  total: 0,
  page: 1,
  size: 1,
  pages: 0,
};

export default data;
