import Tooltip, { type TooltipProps, tooltipClasses } from "@mui/material/Tooltip";
import { styled } from "@mui/material/styles";

export default function CustomizedTooltip(props: TooltipProps) {
  return <CustomizedTooltips {...props}>{props.children}</CustomizedTooltips>;
}

const CustomizedTooltips = styled(({ className, ...props }: TooltipProps) => (
  <Tooltip {...props} classes={{ popper: className }} />
))(({ theme }) => ({
  [`& .${tooltipClasses.arrow}`]: {
    color: theme.palette.grey[200],
  },
  [`& .${tooltipClasses.tooltip}`]: {
    backgroundColor: theme.palette.grey[200],
    color: theme.palette.text.secondary,
  },
}));
