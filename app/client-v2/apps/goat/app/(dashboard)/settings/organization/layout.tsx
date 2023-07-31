import ManageUsers from "@/app/(dashboard)/settings/organization/ManageUsers";
import Overview from "@/app/(dashboard)/settings/organization/Overview";
import Teams from "@/app/(dashboard)/settings/organization/Teams";

import { Tabs } from "@p4b/ui/components/Navigation/Tabs";

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

  return <Tabs tabs={tabs} />;
};

export default Organization;
