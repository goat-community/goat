import type { IconId } from "@p4b/ui/components/theme";
import type React from "react";

export interface ISubscriptionCard {
  icon: IconId;
  title: string;
  listItems: string[];
}

export interface ISubscriptionStatusCardDataType {
  icon: IconId;
  title: string;
  listItems: React.ReactNode[];
  action: React.ReactNode;
}
