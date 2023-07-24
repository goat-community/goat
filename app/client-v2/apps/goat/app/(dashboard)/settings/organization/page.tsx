import ManageUsers from "@/app/(dashboard)/settings/organization/ManageUsers";
import Overview from "@/app/(dashboard)/settings/organization/Overview";
import Teams from "@/app/(dashboard)/settings/organization/Teams";

import { Tabs } from "@p4b/ui/components/Navigation/Tabs";
import { makeStyles } from "@p4b/ui/lib/ThemeProvider";

const Organization = () => {
  const { classes, cx } = useStyles();

  const tabs = [
    {
      child: <Overview />,
      name: "Overview",
    },
    {
      child: <ManageUsers />,
      name: "Manage users",
    },
    {
      child: <Teams />,
      name: "Teams",
    },
    {
      child: <div>overview</div>,
      name: "Settings",
    },
  ];

  return (
    <>
      <Tabs tabs={tabs} className={classes.tabs} />
    </>
  );
};

const useStyles = makeStyles({ name: { Organization } })((theme) => ({
  settingSection: {
    padding: theme.spacing(2),
  },
  tabs: {
    padding: "0",
    "& .mui-prpvj4": {
      borderColor: `${theme.colors.palette.light.greyVariant2}80`,
    },
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

export default Organization;
