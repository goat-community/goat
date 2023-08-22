export type Option = {
  label: string;
  value: string;
} & {
  [key: string]: string | number | boolean;
};
