import React from "react";
import { Tabs } from "@p4b/ui/components/Navigation/Tabs";

const tabsData = [
  {
    child: "Overview",
    name: "Overview",
  },
  {
    child: "ManageUsers",
    name: "Manage users",
  },
  {
    child: "Teams",
    name: "Teams",
  },
  {
    child: "Settings",
    name: "Settings",
  },
];

const Organization = () => {
  const tabs = tabsData.map(({ child, name }) => {
    const Component = React.lazy(() => import(`@/app/[lng]/(dashboard)/settings/organization/${child}`));

    return {
      child: <Component />,
      name,
    };
  });

  return <Tabs tabs={tabs} />;
};

export default Organization;
