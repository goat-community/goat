import { Box, IconButton, Stack, Typography, useTheme } from "@mui/material";
import { alpha } from "@mui/material";
import { useState } from "react";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import { useTranslation } from "@/i18n/client";

import type { BuilderPanelSchema } from "@/lib/validations/project";

import WidgetWrapper from "@/components/builder/widgets/WidgetWrapper";

export interface BuilderPanelSchemaWithPosition extends BuilderPanelSchema {
  element: {
    top?: number;
    bottom?: number;
    left?: number;
    right?: number;
  };
}

interface PanelContainerProps {
  panel: BuilderPanelSchemaWithPosition; // A single panel
  selected?: boolean; // Whether the panel is selected
  onClick?: () => void;
  onChangeOrder?: (panelId: string, position: "top" | "bottom" | "left" | "right") => void;
}

const ChangeOrderButton: React.FC<{
  onClick?: () => void;
  position: "left" | "top" | "bottom" | "right";
  iconName: ICON_NAME;
  isVisible: boolean;
}> = ({ onClick, position, iconName, isVisible }) => {
  const styles = {
    left: { position: "absolute", left: 0, top: "50%", transform: "translateY(-50%)" },
    top: { position: "absolute", top: 0, left: "50%", transform: "translateX(-50%)" },
    bottom: { position: "absolute", bottom: 0, left: "50%", transform: "translateX(-50%)" },
    right: { position: "absolute", right: 0, top: "50%", transform: "translateY(-50%)" },
  };

  return (
    <IconButton
      onClick={(e) => {
        e.stopPropagation();
        onClick?.();
      }}
      sx={{
        ...styles[position],
        pointerEvents: isVisible ? "all" : "none",
        opacity: isVisible ? 1 : 0,
        backgroundColor: "background.default",
        transform: isVisible ? styles[position].transform : `${styles[position].transform} scale(0.9)`,
        transition: "opacity 0.3s, transform 0.3s",
        cursor: "pointer",
        "&:hover": {
          backgroundColor: "background.default",
          color: "primary.main",
        },
        zIndex: 2,
      }}>
      <Icon iconName={iconName} htmlColor="inherit" fontSize="small" />
    </IconButton>
  );
};

const PanelContainer: React.FC<PanelContainerProps> = ({ panel, selected, onClick, onChangeOrder }) => {
  const theme = useTheme();
  const { t } = useTranslation("common");
  const [isHovered, setIsHovered] = useState(false);
  const handleMouseEnter = () => setIsHovered(true);
  const handleMouseLeave = () => setIsHovered(false);
  return (
    // OUTER SECTION
    <Box
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      sx={{
        ...panel.element,
        position: "absolute",
        ...(isHovered && { outline: `1px solid ${theme.palette.primary.main}` }),
        ...(selected && { outline: `2px solid ${theme.palette.primary.main}` }),
        cursor: "pointer",
        display: "flex",
        overflow: "hidden",
        alignItems: "center",
        pointerEvents: "all",
        justifyContent: "center",
      }}>
      {/* Conditional Buttons */}
      {!!panel.element?.left && (
        <ChangeOrderButton
          onClick={() => onChangeOrder?.(panel.id, "left")}
          position="left"
          iconName={ICON_NAME.CHEVRON_LEFT}
          isVisible={isHovered}
        />
      )}
      {!!panel.element?.top && (
        <ChangeOrderButton
          onClick={() => onChangeOrder?.(panel.id, "top")}
          position="top"
          iconName={ICON_NAME.CHEVRON_UP}
          isVisible={isHovered}
        />
      )}
      {!!panel.element?.bottom && (
        <ChangeOrderButton
          onClick={() => onChangeOrder?.(panel.id, "bottom")}
          position="bottom"
          iconName={ICON_NAME.CHEVRON_DOWN}
          isVisible={isHovered}
        />
      )}
      {!!panel.element?.right && (
        <ChangeOrderButton
          onClick={() => onChangeOrder?.(panel.id, "right")}
          position="right"
          iconName={ICON_NAME.CHEVRON_RIGHT}
          isVisible={isHovered}
        />
      )}
      {/* INNER SECTION  */}
      <Box
        sx={{
          width: "100%",
          height: "100%",
          display: "flex",
          pointerEvents: "all",
          transition: "all 0.3s",
          backgroundColor: theme.palette.background.paper,
          ...(panel.config?.appearance?.opacity !== undefined && {
            backgroundColor: alpha(theme.palette.background.paper, panel.config?.appearance?.opacity),
          }),
          ...(panel.config?.appearance?.backgroundBlur !== undefined && {
            backdropFilter: `blur(${panel.config.appearance.backgroundBlur}px)`,
          }),
          ...(panel.config?.options?.style === "rounded" && {
            borderRadius: "1rem",
            margin: "0.5rem",
            width: "calc(100% - 1rem)",
            height: "calc(100% - 1rem)",
          }),
          ...(panel.config?.appearance?.shadow !== undefined && {
            boxShadow: `0px 0px 10px 0px rgba(58, 53, 65, ${panel.config.appearance.shadow})`,
          }),
        }}>
        <Box
          sx={{
            width: "100%",
            height: "100%",
            overflow: "auto hidden",
            display: "flex",
            flexDirection: "column",
          }}>
          {/* Show empty message if widgets array is empty */}
          {panel.widgets?.length === 0 ? (
            <Stack
              width="100%"
              height="100%"
              spacing={2}
              alignItems="center"
              direction="column"
              justifyContent="center">
              <Icon iconName={ICON_NAME.CUBE} htmlColor={theme.palette.text.secondary} fontSize="small" />
              <Typography variant="body2" fontWeight="bold" color="textSecondary">
                {t("drag_and_drop_widgets_here")}
              </Typography>
            </Stack>
          ) : (
            panel.widgets?.map((widget) => (
              <Box key={widget.id}>
                <WidgetWrapper widget={widget} />
              </Box>
            ))
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default PanelContainer;
