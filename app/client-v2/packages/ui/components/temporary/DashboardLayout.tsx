import React from "react";

import { makeStyles } from "../../lib/ThemeProvider";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

const DashboardLayout = ({ children }: DashboardLayoutProps) => {
  const { classes, cx } = useStyles();

  return (
    <>
      <div className={classes.container}>{children}</div>
    </>
  );
};

const useStyles = makeStyles({ name: { DashboardLayout } })((theme) => ({
  container: {
    width: "1144px",
    margin: "0 auto",
    "@media (max-width: 1714px)": {
      width: "70%",
    },
    "@media (max-width: 1500px)": {
      width: "80%",
    },
    "@media (max-width: 1268px)": {
      width: "90%",
    },
  },
}));

export default DashboardLayout;
