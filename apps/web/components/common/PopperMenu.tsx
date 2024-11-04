import { List, ListItemButton, ListItemIcon, ListItemText, Paper, useTheme } from "@mui/material";
import { useState } from "react";

import type { ICON_NAME } from "@p4b/ui/components/Icon";
import { Icon } from "@p4b/ui/components/Icon";

import { ArrowPopper } from "@/components/ArrowPoper";

export interface PopperMenuItem {
  id: string;
  label: string;
  icon?: ICON_NAME;
  color?: string;
  disabled?: boolean;
}

export interface PopperMenuProps {
  menuItems: PopperMenuItem[];
  selectedItem?: PopperMenuItem;
  menuButton: React.ReactNode;
  onSelect: (item: PopperMenuItem) => void;
  disablePortal?: boolean;
}

export default function PopperMenu(props: PopperMenuProps) {
  const { menuItems, menuButton, selectedItem, disablePortal = true } = props;
  const theme = useTheme();
  const [popperMenuOpen, setPopperMenuOpen] = useState<boolean>(false);
  return (
    <ArrowPopper
      open={popperMenuOpen}
      placement="bottom"
      onClose={() => setPopperMenuOpen(false)}
      disablePortal={disablePortal}
      arrow={false}
      content={
        <Paper
          elevation={8}
          sx={{
            minWidth: 220,
            maxWidth: 340,
            overflow: "auto",
            py: theme.spacing(2),
          }}>
          <List dense={true} disablePadding>
            {menuItems.map((item, index) => (
              <ListItemButton
                disabled={item.disabled}
                selected={selectedItem?.label === item.label}
                key={index}
                onClick={(event) => {
                  props.onSelect(item);
                  setPopperMenuOpen(false);
                  event.stopPropagation();
                }}
                sx={{
                  ...(item.color && {
                    color: item.color,
                  }),
                }}>
                {item.icon && (
                  <ListItemIcon
                    sx={{
                      color: item.color || "inherit",
                      pr: 4,
                      minWidth: 0,
                    }}>
                    <Icon style={{ fontSize: 15 }} iconName={item.icon} htmlColor={item.color || "inherit"} />
                  </ListItemIcon>
                )}
                <ListItemText
                  primary={item.label}
                  sx={{
                    "& .MuiTypography-root": {
                      ...(item.color && {
                        color: item.color,
                      }),
                    },
                  }}
                />
              </ListItemButton>
            ))}
          </List>
        </Paper>
      }>
      <div
        onClick={(event) => {
          event.stopPropagation();
          setPopperMenuOpen(!popperMenuOpen);
        }}>
        {menuButton}
      </div>
    </ArrowPopper>
  );
}
