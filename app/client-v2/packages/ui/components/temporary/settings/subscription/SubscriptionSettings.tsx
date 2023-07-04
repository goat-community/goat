import { makeStyles } from "../../../../lib/ThemeProvider";
import { Tabs } from "../../../Navigation/Tabs";
import Overview from "./Overview";
import Subscription from "./Subscription";

const SubscriptionSettings = () => {
  const { classes, cx } = useStyles();

  const tabs = [
    {
      child: <Overview />,
      name: "Overview",
    },
    {
      child: <Subscription />,
      name: "Subscription",
    },
  ];

  return (
    <>
      <Tabs tabs={tabs} className={classes.tabs} />
    </>
  );
};

const useStyles = makeStyles({ name: { SubscriptionSettings } })((theme) => ({
  settingSection: {
    padding: theme.spacing(2),
  },
  tabs: {
    padding: "0",
  },
  bannerText: {
    color: "white",
  },
  extensionButtonWrapper: {
    marginBottom: theme.spacing(5),
  },
  button: {
    marginTop: theme.spacing(3),
    padding: `${theme.spacing(1)}px ${theme.spacing(2) + 2}px`,
    fontSize: "13px",
  },
}));

export default SubscriptionSettings;
