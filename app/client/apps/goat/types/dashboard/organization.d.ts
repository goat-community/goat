import type {Option} from "@p4b/types/atomicComponents";
import type {IconId} from "@p4b/ui/components/theme";
import type React from "react";

export interface IUser {
  name: string;
  email: string;
  role: "Admin" | "Editor" | "User";
  status: "Active" | "Invite sent" | "Expired" | React.ReactNode;
  Added: string;
}

export interface IOrganization {
  title: string;
  icon: IconId;
  listItems: React.ReactNode[];
  action: React.ReactNode;
}

export interface ITeam {
  name: string;
  participants: Option[];
  createdAt: string;
}
