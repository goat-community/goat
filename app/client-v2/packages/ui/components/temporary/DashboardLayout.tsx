import React from "react";

import { makeStyles } from "../../lib/ThemeProvider";
import { DashboardSidebar } from "../DashboardSidebar";
import { Icon } from "../theme";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

const DashboardLayout = ({ children }: DashboardLayoutProps) => {
  const { classes, cx } = useStyles();

  const sidebarItems = [
    {
      link: "https://google.com",
      icon: () => <Icon iconId="home" iconVariant="gray" />,
      placeholder: "Home",
    },
    {
      link: "https://google.com",
      icon: () => <Icon iconId="folder" iconVariant="gray" />,
      placeholder: "Content",
    },
    {
      link: "https://google.com",
      icon: () => <Icon iconId="settings" iconVariant="gray" />,
      placeholder: "Settings",
    },
    {
      link: "https://google.com",
      icon: () => <Icon iconId="help" iconVariant="gray" />,
      placeholder: "Help",
    },
  ];

  return (
    <DashboardSidebar items={sidebarItems} width={60} extended_width={200}>
      <div className={classes.container}>{children}</div>
    </DashboardSidebar>
  );
};

const useStyles = makeStyles({ name: { DashboardLayout } })((theme) => ({
  container: {
    width: "1344px",
    margin: "0 auto",
    paddingLeft: "200px",
    "@media (max-width: 1714px)": {
      width: "90%",
    },
    "@media (max-width: 1500px)": {
      width: "90%",
    },
    "@media (max-width: 1268px)": {
      paddingLeft: "50px",
    },
  },
}));

export default DashboardLayout;
