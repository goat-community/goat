import { styled } from "@mui/material";

const StyledDragHandle = styled("div")(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  color: theme.palette.text.secondary,
  transition: theme.transitions.create(["opacity"], {
    duration: theme.transitions.duration.standard,
  }),
  opacity: 0,
  ":hover": {
    cursor: "move",
    color: theme.palette.text.primary,
  },
}));

export const DragHandle: React.FC<{
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  listeners?: any;
  children?: React.ReactNode;
}> = ({ listeners, children }) => (
  <StyledDragHandle {...(listeners ? listeners : {})}>{children}</StyledDragHandle>
);
