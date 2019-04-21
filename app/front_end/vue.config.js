module.exports = {
  devServer: {
    port: 5000,
    overlay: {
      warnings: true,
      errors: true
    },
    proxy: {
      "/api": {
        target: "http://localhost:3000/api", //ADD THIS TO .ENV VARIABLES
        changeOrigin: true
      },
      "/geoserver": {
        target: "http://localhost:8080/geoserver", //ADD THIS TO .ENV VARIABLES
        changeOrigin: true
      }
    }
  }
};
