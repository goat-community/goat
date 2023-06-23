import { Box } from "@mui/material";
import Grid from "@mui/material/Unstable_Grid2/Grid2";
import React from "react";

import { makeStyles } from "../../../lib/ThemeProvider";

interface AuthTemplateProps {
  children: React.ReactNode;
}

const AuthTemplate = (props: AuthTemplateProps) => {
  const { children } = props;

  const { classes } = useStyles();

  return (
    <div className={classes.root}>
      <Grid container className={classes.gridContainer}>
        <Grid xs={12} lg={6} className={classes.gridLeft}>
          <Box
            component="header"
            sx={{
              left: 0,
              p: 3,
              position: "fixed",
              top: 0,
              width: "100%",
            }}>
            <Box
              component="a"
              href="https://www.plan4better.de/"
              target="_blank"
              sx={{
                display: "inline-flex",
                width: 160,
              }}>
              <img
                width="100%"
                src="https://assets.plan4better.de/img/logo/plan4better_standard.svg"
                alt="Plan4Better Logo"
              />
            </Box>
          </Box>
          <div className={classes.child}>{children}</div>
        </Grid>
        <Grid xs={12} lg={6} className={classes.gridRight}>
          <Box sx={{ p: 3, width: 350 }} component="div">
            <img
              width="100%"
              src="https://assets.plan4better.de/img/logo/goat_white.svg"
              alt="Plan4Better Logo"
            />
          </Box>
        </Grid>
      </Grid>
    </div>
  );
};

const useStyles = makeStyles({ name: { AuthTemplate } })((theme) => ({
  root: {
    display: "flex",
  },
  gridContainer: {
    flex: "1 1 auto",
  },
  child: {
    width: "100%",
    height: "100%",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    backgroundColor: theme.colors.useCases.surfaces.background,
  },
  image: {
    width: "50%",
    backgroundImage: 'url("https://assets.plan4better.de/img/login/artwork_1.png")',
    height: "100vh",
  },
  gridLeft: {
    height: "100vh",
    display: "flex",
    flexDirection: "column",
    backgroundColor: theme.colors.useCases.surfaces.background,
  },
  gridRight: {
    alignItems: "center",
    background:
      "radial-gradient(50% 50% at 50% 50%, rgba(40,54,72,0.8) 0%, rgba(40,54,72,0.9) 100%), url(https://assets.plan4better.de/img/login/artwork_1.png) no-repeat center",
    backgroundSize: "cover",
    color: "white",
    display: "flex",
    justifyContent: "center",
    "& img": {
      maxWidth: "100%",
    },
  },
}));

export default AuthTemplate;
