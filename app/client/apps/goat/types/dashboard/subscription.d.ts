import type { ICON_NAME } from "@p4b/ui/components/Icon";
import type React from "react";

export interface ISubscriptionCard {
  icon: ICON_NAME;
  title: string;
  listItems: string[];
}

export interface ISubscriptionStatusCardDataType {
  icon: ICON_NAME;
  title: string;
  listItems: React.ReactNode[];
  action: React.ReactNode;
}
