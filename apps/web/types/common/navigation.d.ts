export interface NavItem {
  link: string;
  icon?: ICON_NAME;
  label: string;
  current: boolean;
  auth?: boolean;
}
