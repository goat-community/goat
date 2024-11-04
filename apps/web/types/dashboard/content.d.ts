export interface ContentDialogBaseProps extends DialogBaseProps {
  open: boolean;
  onClose?: () => void;
  type: "project" | "layer";
  content: Project | Layer;
}
