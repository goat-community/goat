declare module "manage-users-dashboard" {
  interface User {
    name: string;
    email: string;
    role: "Admin" | "Editor" | "User";
    status: "Active" | "Invite sent" | "Expired" | React.ReactNode;
    Added: string;
  }
}

declare module "overview-dashboard-organization" {
  interface Organization {
    title: string;
    icon: IconId;
    listItems: React.ReactNode[];
    action: React.ReactNode;
  }
}

declare module "team-organization-dashboard" {
  interface Team {
    name: string;
    participants: Option[];
    createdAt: string;
  }
}
