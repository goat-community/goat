module.exports = {
  devServer: {
    port: 5000,
    overlay: {
      warnings: true,
      errors: true
    },
    proxy: {
      "/api": {
        target: process.env.API_BASEURL,
        changeOrigin: true
      },
      "/geoserver": {
        target: process.env.GEOSERVER_BASEURL,
        changeOrigin: true
      },
      "/printproxy": {
        target: "https://geomapfish-demo-2-4.camptocamp.com/",
        changeOrigin: true
      }
    }
  },

  pluginOptions: {
    i18n: {
      locale: "en",
      fallbackLocale: "en",
      localeDir: "locales",
      enableInSFC: true
    }
  }
};
