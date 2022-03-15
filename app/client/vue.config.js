module.exports = {
  devServer: {
    port: 3000,
    overlay: {
      warnings: true,
      errors: true
    },
    proxy: {
      "/api": {
        target: process.env.API_BASEURL,
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
