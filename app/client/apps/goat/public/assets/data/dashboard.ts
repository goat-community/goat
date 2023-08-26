import { ICON_NAME } from "@p4b/ui/components/Icon";
import type {IUser} from "@/types/dashboard/organization";
import type {ISubscriptionCard} from "@/types/dashboard/subscription";

export const manageUsersStatic: IUser[] = [
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

export const dummyOrganization: ISubscriptionCard = {
  icon: ICON_NAME.ORGANIZATION,
  title: "Coorperation Name",
  listItems: [
    "Next payment: 23 July 2024",
    "Annual payment cycle: 23 July 2023 - 23 July 2024",
    "2 of 12 editors seat available",
    "Region: Greater Munich",
  ],
};

export const dummySubscription: ISubscriptionCard = {
  icon: ICON_NAME.ROCKET,
  title: "Starter",
  listItems: [
    "Next payment: 23 July 2024",
    "Annual payment cycle: 23 July 2023 - 23 July 2024",
    "2 of 12 editors seat available",
    "Region: Greater Munich",
  ],
};

export const extensionSubscriptions: ISubscriptionCard[] = [
  {
    icon: ICON_NAME.RUN,
    title: "Active mobility",
    listItems: [
      "Next payment: 23 July 2024",
      "Annual payment cycle: 23 July 2023 - 23 July 2024",
      "2 of 12 editors seat available",
      "Region: Greater Munich",
    ],
  },
  {
    icon: ICON_NAME.BUS,
    title: "Motorised mobility",
    listItems: [
      "Next payment: 23 July 2024",
      "Annual payment cycle: 23 July 2023 - 23 July 2024",
      "2 of 12 editors seat available",
      "Region: Greater Munich",
    ],
  },
];
