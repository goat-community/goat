declare module "manage-users-dashboard" {
  interface User {
    name: string,
    email: string,
    role: "Admin" | "Editor" | "User",
    status: "Active" | "Invite sent" | "Expired" | React.ReactNode,
    Added: string,
  }
}