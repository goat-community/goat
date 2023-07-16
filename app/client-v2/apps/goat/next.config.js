module.exports = {
  output: "standalone",
  reactStrictMode: true,
  transpilePackages: ["@p4b/ui", "@p4b/tsconfig", "@p4b/config"],
  modularizeImports: {
    "@mui/icons-material": {
      transform: "@mui/icons-material/{{member}}",
    },
  },
};
