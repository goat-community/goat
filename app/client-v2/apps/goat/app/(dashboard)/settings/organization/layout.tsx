import { Tabs } from "@p4b/ui/components/Navigation/Tabs";

import ManageUsers from "./ManageUsers";
import Overview from "./Overview";
import Teams from "./Teams";

const Organization = () => {
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
      <Tabs tabs={tabs} />
    </>
  );
};

export default Organization;
