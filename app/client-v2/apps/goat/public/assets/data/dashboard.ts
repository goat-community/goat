import { User } from "manage-users-dashboard";
import type { Organization } from "overview-dashboard-organization";
import { SubscriptionCard } from "subscriptions-dashboard";

export const manageUsersStatic: User[] = [
  {
    name: "Luca William Silva",
    email: "john.wlsdasadm@gmail.com",
    role: "Admin",
    status: "Active",
    Added: "23 Jun 19",
  },
  {
    name: "Fenix William Silva",
    email: "john.werwxsam@gmail.com",
    role: "Admin",
    status: "Invite sent",
    Added: "23 Jun 19",
  },
  {
    name: "Adam William Silva",
    email: "john.ghjfgpsum@gmail.com",
    role: "Admin",
    status: "Expired",
    Added: "23 Jun 19",
  },
  {
    name: "John William Silva",
    email: "john.zxcsadum@gmail.com",
    role: "Admin",
    status: "Active",
    Added: "23 Jun 19",
  },
  {
    name: "John William Silva",
    email: "john.wawewdssum@gmail.com",
    role: "Admin",
    status: "Invite sent",
    Added: "23 Jun 19",
  },
  {
    name: "John William Silva",
    email: "john.wiuywefipsum@gmail.com",
    role: "Admin",
    status: "Invite sent",
    Added: "23 Jun 19",
  },
];

export const dummySubscription: SubscriptionCard = {
  icon: "rocketLaunch",
  title: "Starter",
  listItems: [
    "Next payment: 23 July 2024",
    "Annual payment cycle: 23 July 2023 - 23 July 2024",
    "2 of 12 editors seat available",
    "Region: Greater Munich",
  ],
};

export const extensionSubscriptions: SubscriptionCard[] = [
  {
    icon: "run",
    title: "Active mobility",
    listItems: [
      "Next payment: 23 July 2024",
      "Annual payment cycle: 23 July 2023 - 23 July 2024",
      "2 of 12 editors seat available",
      "Region: Greater Munich",
    ],
  },
  {
    icon: "bus",
    title: "Motorised mobility",
    listItems: [
      "Next payment: 23 July 2024",
      "Annual payment cycle: 23 July 2023 - 23 July 2024",
      "2 of 12 editors seat available",
      "Region: Greater Munich",
    ],
  },
];

export const organizationOverview: SubscriptionCard = {
  title: "Organisation name",
  icon: "coorperate",
  listItems: [
    "You are admin on this organisation",
    "12 active team members",
    "Active regions: Greater Munich, Greater London, Faux Valley, Stadtburg Burg",
  ],
};
