import type { IconId } from "@p4b/ui/components/theme";

declare module "subscriptions-dashboard" {
  interface SubscriptionCard {
    icon: IconId;
    title: string;
    listItems: string[];
  }

  interface SubscriptionStatusCardDataType {
    icon: IconId;
    title: string;
    listItems: React.ReactNode[];
    action: React.ReactNode;
  }
}
