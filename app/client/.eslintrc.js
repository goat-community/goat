module.exports = {
  root: true,
  // This tells ESLint to load the config from the package `eslint-config-p4b`
  extends: ["p4b"],
  settings: {
    next: {
      rootDir: ["apps/*/"],
    },
  },
};
