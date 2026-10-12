const path = require("path");
const { getLoader, loaderByName } = require("@craco/craco");

const packages = [];
console.log(__dirname);
packages.push(path.join(__dirname, "../ui"));

// @p4b/ui is compiled from source and resolves its own React (the web app's
// version). A second React breaks every hook and a second MUI/Emotion loses
// the theme context, so both resolve to this package's copies.
const sharedModules = [
  "react",
  "react-dom",
  "@emotion/react",
  "@emotion/styled",
  "@mui/material",
  "@mui/system",
  "@mui/icons-material",
];
const sharedAliases = {};
for (const name of sharedModules) {
  try {
    // Transitive packages (e.g. @mui/system) resolve through the ones found so far.
    const paths = [__dirname, ...Object.values(sharedAliases)];
    sharedAliases[name] = path.dirname(require.resolve(`${name}/package.json`, { paths }));
  } catch {
    // Not a dependency of this package; @p4b/ui keeps its own copy.
  }
}

module.exports = {
  webpack: {
    configure: (webpackConfig, arg) => {
      const { isFound, match } = getLoader(webpackConfig, loaderByName("babel-loader"));
      if (isFound) {
        const include = Array.isArray(match.loader.include) ? match.loader.include : [match.loader.include];

        match.loader.include = include.concat(packages);
      }
      webpackConfig.resolve.alias = { ...webpackConfig.resolve.alias, ...sharedAliases };
      // The aliases point into the pnpm store, outside src/; CRA's scope check
      // would reject them.
      webpackConfig.resolve.plugins = (webpackConfig.resolve.plugins || []).filter(
        (plugin) => plugin.constructor.name !== "ModuleScopePlugin"
      );
      return webpackConfig;
    },
  },
};
