import type React from "react";

export interface ISelectedFolder {
  id: string;
  name: string;
  user_id: string
}


export interface IDashboardTableRowInfo {
  id: string
  name: React.ReactNode;
  type: React.ReactNode;
  modified: string;
  size: string;
  label?: string;
}
