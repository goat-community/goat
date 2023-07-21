"use client";

import { makeStyles } from "@/lib/theme";

import Footer from "@p4b/ui/components/Navigation/Footer";
import { Toolbar } from "@p4b/ui/components/Navigation/Toolbar";
import { Icon } from "@p4b/ui/components/theme";
import type { IconId } from "@p4b/ui/components/theme";

import { DashboardSidebar } from "./DashboardSidebar";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

const DashboardLayout = ({ children }: DashboardLayoutProps) => {
  const { classes, cx } = useStyles();

  const items = [
    { link: "https://google.com", icon: () => <Icon iconId="user" size="medium" iconVariant="gray2" /> },
    { link: "https://google.com", icon: () => <Icon iconId="help" size="medium" iconVariant="gray2" /> },
  ];

  const sidebarItems: { link: string; icon: IconId; placeholder: string }[] = [
    {
      link: "/home",
      icon: "home",
      placeholder: "Home",
    },
    {
      link: "/content",
      icon: "folder",
      placeholder: "Content",
    },
    {
      link: "/settings",
      icon: "settings",
      placeholder: "Settings",
    },
    {
      link: "/help",
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
        <div className={cx(classes.container)}>{children}</div>
      </DashboardSidebar>
      <Footer
        links={footerLinks}
        text="Lörem ipsum od ohet dilogi. Bell trabel, samuligt, ohöbel utom diska. Jinesade bel när feras redorade i belogi. FAR paratyp i muvåning, och pesask vyfisat. Viktiga poddradio har un mad och inde."
      />
    </>
  );
};

const useStyles = makeStyles({ name: { DashboardLayout } })(() => ({
  container: {
    minHeight: "100vh",
    marginTop: "52px",
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
