"use client";

import GridContainer from "@/components/grid/GridContainer";
import SingleGrid from "@/components/grid/SingleGrid";
import { makeStyles } from "@/lib/theme";
import { Text } from "@/lib/theme";
import { useState } from "react";

import { Divider } from "@p4b/ui/components/DataDisplay/Divider";

import Organization from "./organization/page";
import PrivacyPreferences from "./privacy-preference/page";
import SubscriptionSettings from "./subscription/SubscriptionSettings";

const Settings = () => {
  const [currentSetting, setCurrentSetting] = useState<{ children: React.ReactNode; value: string }>({
    children: <Organization />,
    value: "Organization",
  });

  const { classes, cx } = useStyles();

  return (
    <GridContainer>
      <SingleGrid span={1}>
        <div>
          <span
            onClick={() =>
              setCurrentSetting({
                children: <Organization />,
                value: "Organization",
              })
            }>
            <Text
              typo="body 2"
              className={
                currentSetting.value === "Organization" ? classes.selectedSidebarText : classes.SidebarText
              }>
              Organization
            </Text>
          </span>
          <Divider width="100%" color="main" className={classes.hr} />
          <span
            onClick={() =>
              setCurrentSetting({
                children: <SubscriptionSettings />,
                value: "Subscription",
              })
            }>
            <Text
              typo="body 2"
              className={
                currentSetting.value === "Subscription" ? classes.selectedSidebarText : classes.SidebarText
              }>
              Subscription
            </Text>
          </span>
          <Divider width="100%" color="main" className={classes.hr} />
          <span
            onClick={() =>
              setCurrentSetting({
                children: <PrivacyPreferences />,
                value: "Privacy preferences",
              })
            }>
            <Text
              typo="body 2"
              className={
                currentSetting.value === "Privacy preferences"
                  ? classes.selectedSidebarText
                  : classes.SidebarText
              }>
              Privacy preferences
            </Text>
          </span>
          <Divider width="100%" color="main" className={classes.hr} />
        </div>
      </SingleGrid>
      <SingleGrid span={3}>
        <div>{currentSetting.children}</div>
      </SingleGrid>
    </GridContainer>
  );
};

const useStyles = makeStyles({ name: { Settings } })((theme) => ({
  wrapper: {
    display: "flex",
    gap: "1%",
  },
  SidebarText: {
    // padding: theme.spacing(1) theme.spacing(4),
    padding: `${theme.spacing(1)}px ${theme.spacing(4)}px`,
    cursor: "pointer",
    "&:hover": {
      backgroundColor: theme.colors.palette[theme.isDarkModeEnabled ? "dark" : "light"].greyVariant1 + "50",
    },
  },
  selectedSidebarText: {
    padding: `${theme.spacing(1)}px ${theme.spacing(4)}px`,
    cursor: "pointer",
    backgroundColor: theme.colors.palette.focus.light + "14",
  },
  hr: {
    margin: `${theme.spacing(1)}px 0`,
  },
}));

export default Settings;
