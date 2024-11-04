import { IconButton, Stack, Switch, Typography, useTheme } from "@mui/material";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

const SectionHeader = ({
  label,
  active,
  onToggleChange,
  collapsed,
  setCollapsed,
  alwaysActive = false,
  disableAdvanceOptions = false,
  icon = ICON_NAME.CIRCLE,
}: {
  label: string;
  active: boolean;
  onToggleChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
  collapsed?: boolean;
  setCollapsed?: (collapsed: boolean) => void;
  alwaysActive?: boolean;
  disableAdvanceOptions?: boolean;
  icon?: ICON_NAME;
}) => {
  const theme = useTheme();
  return (
    <Stack direction="row" alignItems="center" justifyContent="space-between">
      <Stack direction="row" alignItems="center">
        <Icon
          iconName={icon}
          style={{
            fontSize: "17px",
            color: active ? theme.palette.text.secondary : theme.palette.text.disabled,
          }}
        />
        <Typography
          variant="body2"
          fontWeight="bold"
          sx={{ pl: 2 }}
          color={active ? theme.palette.text.secondary : theme.palette.text.disabled}>
          {label}
        </Typography>
      </Stack>
      <Stack direction="row" alignItems="center">
        {alwaysActive ? null : <Switch size="small" checked={!!active} onChange={onToggleChange} />}

        {!disableAdvanceOptions && (
          <IconButton
            disabled={!active}
            sx={{
              ...(!collapsed && {
                color: theme.palette.primary.main,
              }),
            }}
            onClick={() => {
              if (setCollapsed) {
                setCollapsed(!collapsed);
              }
            }}>
            <Icon htmlColor="inherit" iconName={ICON_NAME.SLIDERS} style={{ fontSize: "15px" }} />
          </IconButton>
        )}
      </Stack>
    </Stack>
  );
};

export default SectionHeader;
