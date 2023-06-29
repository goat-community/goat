import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import ForwardIcon from "@mui/icons-material/Forward";
import React from "react";

import { makeStyles } from "../../lib/ThemeProvider";
import { DashboardSidebar } from "../DashboardSidebar";
import Footer from "../Footer";
import { createIcon } from "../Icon";
import { Toolbar } from "../Toolbar";
import type { IconId } from "../theme";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

const { Icon } = createIcon({
  info: ForwardIcon,
  profile: AccountCircleIcon,
});

const DashboardLayout = ({ children }: DashboardLayoutProps) => {
  const { classes, cx } = useStyles();

  const items = [
    { link: "https://google.com", icon: () => <Icon iconId="profile" size="medium" iconVariant="gray2" /> },
    { link: "https://google.com", icon: () => <Icon iconId="info" size="medium" iconVariant="gray2" /> },
  ];

  const sidebarItems: { link: string; icon: IconId; placeholder: string }[] = [
    {
      link: "https://google.com",
      icon: "home",
      placeholder: "Home",
    },
    {
      link: "https://google.com",
      icon: "folder",
      placeholder: "Content",
    },
    {
      link: "https://google.com",
      icon: "settings",
      placeholder: "Settings",
    },
    {
      link: "https://google.com",
      icon: "help",
      placeholder: "Help",
    },
  ];

  const footerLinks: { header: string; links: { name: string; underline?: boolean; icon?: IconId }[] }[] = [
    {
      header: "Navigate",
      links: [
        {
          name: "Home it work",
        },
        {
          name: "Pricing",
        },
        {
          name: "Blog",
        },
        {
          name: "Demo",
        },
      ],
    },
    {
      header: "Study Areas",
      links: [
        {
          name: "Germany",
        },
        {
          name: "EU",
        },
        {
          name: "UK",
        },
        {
          name: "Asia",
        },
        {
          name: "Americas",
        },
      ],
    },
    {
      header: "Contact ",
      links: [
        {
          icon: "phone",
          name: "+49 89 2000 708 30",
          underline: true,
        },
        {
          icon: "email",
          name: "info@plan4better.de",
          underline: true,
        },
        {
          icon: "marker",
          name: "Am Kartoffelgarten 14 c/o WERK1 81671 München Germany",
          underline: true,
        },
      ],
    },
  ];

  return (
    <>
      <Toolbar height={52} items={items} />
      <DashboardSidebar items={sidebarItems} width={60} extended_width={200}>
        <div className={classes.container}>{children}</div>
      </DashboardSidebar>
      <Footer
        links={footerLinks}
        text="Lörem ipsum od ohet dilogi. Bell trabel, samuligt, ohöbel utom diska. Jinesade bel när feras redorade i belogi. FAR paratyp i muvåning, och pesask vyfisat. Viktiga poddradio har un mad och inde."
      />
    </>
  );
};

const useStyles = makeStyles({ name: { DashboardLayout } })((theme) => ({
  container: {
    width: "1344px",
    minHeight: "100vh",
    margin: "0 auto",
    marginTop: "52px",
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
