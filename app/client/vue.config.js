module.exports = {
  devServer: {
    port: 80,
    overlay: {
      warnings: true,
      errors: true
    },
    proxy: {
      "/api": {
        target: process.env.API_BASEURL,
        changeOrigin: true,
        secure: false,
        logLevel: "debug"
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
  },
  configureWebpack: {
    devtool: "source-map"
  }
};
