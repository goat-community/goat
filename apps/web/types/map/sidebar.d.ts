import type { ICON_NAME } from "@p4b/ui/components/Icon";

import type { MapSidebarItemID } from "@/types/map/common";

export type MapSidebarItem = {
  id: MapSidebarItemID;
  icon: ICON_NAME;
  name: string;
  component?: JSX.Element;
  link?: string;
  disabled?: boolean;
};

export type PanelProps = {
  onCollapse?: () => void;
  projectId: string;
};
