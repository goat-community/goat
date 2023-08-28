"use client";

import { DashboardSidebar } from "@/app/[lng]/(dashboard)/DashboardSidebar";
import { TranslationSwitcher } from "@/app/[lng]/components/TranslationSwitcher";
// import { useTranslation } from "@/app/i18/client";
import { makeStyles } from "@/lib/theme";
import { signOut } from "next-auth/react";
import { useState, useRef } from "react";

import { InfoMenu } from "@p4b/ui/components/InfoMenu";
import Footer from "@p4b/ui/components/Navigation/Footer";
import { Toolbar } from "@p4b/ui/components/Navigation/Toolbar";
import { Text, Button } from "@p4b/ui/components/theme";
import CorporateFareIcon from '@mui/icons-material/CorporateFare';
import PersonIcon from '@mui/icons-material/Person';
import HelpIcon from '@mui/icons-material/Help';
import { ICON_NAME } from "@p4b/ui/components/Icon";

interface DashboardLayoutProps {
  children: React.ReactNode;
  params: { lng: string };
}

const DashboardLayout = ({ children, params: { lng } }: DashboardLayoutProps) => {
  const { classes, cx } = useStyles();
  const [isVisible, setIsVisible] = useState<boolean>(false);
  const ButtonElement = useRef(null);
  // const { t } = useTranslation(lng);

  const handleClick = () => {
    setIsVisible(true);
  };
  const handleClose = () => {
    setIsVisible(false);
  };

  const menuHeader = (
    <span style={{ display: "flex", alignItems: "center" }}>
      <span style={{ marginRight: "5px" }}>
        <CorporateFareIcon />
      </span>{" "}
      <Text typo="body 2">GOAT</Text>
    </span>
  );

  const actionHeader = (
    // <Button startIcon="powerOff" onClick={() => signOut()}>
    //   Log Out
    // </Button>
    <Button onClick={() => signOut()}>
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
            {/* <Icon iconId="user" size="medium" iconVariant="gray2" /> */}
            <PersonIcon />
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
          <HelpIcon />
        </div>
      ),
    },
  ];

  const sidebarItems: { link: string; icon: ICON_NAME; placeholder: string }[] = [
    {
      link: "/home",
      icon: ICON_NAME.HOUSE,
      placeholder: "Home",
    },
    {
      link: "/content",
      icon: ICON_NAME.FOLDER,
      placeholder: "Content",
    },
    {
      link: "/settings",
      icon: ICON_NAME.SETTINGS,
      placeholder: "Settings",
    },
    {
      //todo change test to id logic
      link: "/map/test",
      icon: ICON_NAME.STYLE,
      placeholder: "Styling",
    },
    {
      link: "/help",
      icon: ICON_NAME.HELP,
      placeholder: "Help",
    },
  ];

  return (
    <>
      <Toolbar height={52} items={items} />
      <DashboardSidebar lng={lng} items={sidebarItems} width={52} extended_width={200}>
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
    marginTop: "52px",
    width: "calc(100% - 96px)",
  },
}));

export default DashboardLayout;
