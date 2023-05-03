import { createTheme } from "@mui/material";


const theme = createTheme({
  palette: {
    primary: {
      main: "#283648",
    },
    secondary: {
      main: "#2BB381",
    },
  },
  typography: {
    h1: {
      color: "#283648",
      fontSize: 32,
      fontWeight: 700,
    },
    h2: {
      color: "#283648",
      fontSize: 26,
    },
    h3: {
      color: "#283648",
      fontSize: 22,
      lineHeight: "28px",
    },
    h4: {
      color: "#283648",
      fontSize: 18,
    },
    h5: {
      color: "#283648",
      fontSize: 16,
    },
    h6: {
      fontSize: 12,
    },
  },
});

const lightTheme = theme;

export { lightTheme };
