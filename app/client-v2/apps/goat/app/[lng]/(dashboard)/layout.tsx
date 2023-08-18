"use client";

import { DashboardSidebar } from "@/app/[lng]/(dashboard)/DashboardSidebar";
import { TranslationSwitcher } from "@/app/[lng]/components/TranslationSwitcher";
import { useTranslation } from "@/app/i18/client";
import { makeStyles } from "@/lib/theme";
import { signOut } from "next-auth/react";
import { useState, useRef } from "react";

import { InfoMenu } from "@p4b/ui/components/InfoMenu";
import Footer from "@p4b/ui/components/Navigation/Footer";
import { Toolbar } from "@p4b/ui/components/Navigation/Toolbar";
import { Icon, Text, Button } from "@p4b/ui/components/theme";
import type { IconId } from "@p4b/ui/components/theme";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

const DashboardLayout = ({ children, params: { lng } }: DashboardLayoutProps) => {
  const { classes, cx } = useStyles();
  const [isVisible, setIsVisible] = useState<boolean>(false);
  const ButtonElement = useRef(null);
  const { t } = useTranslation(lng);

  const handleClick = () => {
    setIsVisible(true);
  };
  const handleClose = () => {
    setIsVisible(false);
  };

  const menuHeader = (
    <span style={{ display: "flex", alignItems: "center" }}>
      <span style={{ marginRight: "5px" }}>
        <Icon iconId="coorperate" />
      </span>{" "}
      <Text typo="body 2">GOAT</Text>
    </span>
  );

  const actionHeader = (
    <Button startIcon="powerOff" onClick={() => signOut()}>
      Log Out
    </Button>
  );

  const items = [
    {
      link: "",
      icon: () => <TranslationSwitcher lng={lng} />,
    },
    {
      link: "https://google.com",
      icon: () => (
        <>
          <div
            onClick={handleClick}
            ref={ButtonElement}
            style={{ padding: "3px 10px", borderRight: "2px solid #ccc" }}>
            <Icon iconId="user" size="medium" iconVariant="gray2" />
          </div>
          <InfoMenu
            ref={ButtonElement}
            handleCloseFunction={handleClose}
            status={isVisible}
            menuHeader={menuHeader}
            menuActions={actionHeader}>
            <Text typo="body 1">randomuser@outlook.com</Text>
            <Text typo="caption">Admin</Text>
          </InfoMenu>
        </>
      ),
    },
    {
      link: "https://google.com",
      icon: () => (
        <div style={{ padding: "3px 10px" }}>
          <Icon iconId="help" size="medium" iconVariant="gray2" />
        </div>
      ),
    },
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
      link: "/styling",
      icon: "colorLens",
      placeholder: "Styling",
    },
    {
      link: "/help",
      icon: "help",
      placeholder: "Help",
    },
  ];

  return (
    <>
      <Toolbar height={52} items={items} />
      <DashboardSidebar items={sidebarItems} width={60} extended_width={200}>
        <div className={cx(classes.container)}>{children}</div>
      </DashboardSidebar>
      <Footer lng={lng} />
    </>
  );
};

const useStyles = makeStyles({ name: { DashboardLayout } })(() => ({
  container: {
    minHeight: "100vh",
    margin: "0 auto",
    marginTop: "104px",
    width: "80%",
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
