import { Box, Card, CardMedia, Tooltip, useTheme } from "@mui/material";
import { useState } from "react";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

export interface EmptyCardProps {
  tooltip: string;
  backgroundImage: string;
  onClick?: () => void;
}

interface EmptyCardActionButtonProps {
  tooltip?: string;
}

const EmptyCardActionButton = (props: EmptyCardActionButtonProps) => {
  const theme = useTheme();
  const [tooltipOpen, setTooltipOpen] = useState(false);
  return (
    <Box
      onMouseEnter={() => setTooltipOpen(true)}
      onMouseLeave={() => setTooltipOpen(false)}
      sx={{
        position: "absolute",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "transparent",
      }}>
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          flexDirection: "column",
          minHeight: "100%",
          color: theme.palette.grey[500],
          transition: theme.transitions.create(["color", "transform"], {
            duration: theme.transitions.duration.standard,
          }),
          "&:hover": {
            color: theme.palette.primary.main,
          },
        }}>
        <Tooltip open={tooltipOpen} disableHoverListener title={props.tooltip} placement="top">
          <div>
            <Icon iconName={ICON_NAME.CIRCLE_PLUS} fontSize="large" htmlColor="inherit" />
          </div>
        </Tooltip>
      </Box>
    </Box>
  );
};

export default function EmptyCard(props: EmptyCardProps) {
  return (
    <Card
      elevation={1}
      onClick={props.onClick}
      sx={{
        position: "relative",
        height: "100%",
        display: "flex",
        "&:hover": {
          cursor: "pointer",
          boxShadow: 10,
        },
      }}>
      <Box
        sx={{
          overflow: "hidden",
        }}>
        <CardMedia
          component="img"
          sx={{
            height: "100%",
            width: "100%",
            transition: "transform 300ms cubic-bezier(0.4, 0, 0.2, 1) 0ms",
            transformOrigin: "center center",
            objectFit: "cover",
            backgroundSize: "cover",
          }}
          image={props.backgroundImage}
        />
        <EmptyCardActionButton tooltip={props.tooltip} />
      </Box>
    </Card>
  );
}
