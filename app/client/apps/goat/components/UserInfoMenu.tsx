import { ArrowPopper } from "@/components/ArrowPoper";
import { makeStyles, useTheme } from "@/lib/theme";
import {
  Avatar,
  Divider,
  IconButton,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Paper,
  Stack,
} from "@mui/material";
import { signOut, useSession } from "next-auth/react";
import { useState } from "react";

import { Icon, ICON_NAME } from "@p4b/ui/components/Icon";
import { Text } from "@p4b/ui/components/theme";

export default function UserInfoMenu() {
  const { status, data: session } = useSession();
  const { classes } = useStyles();
  const theme = useTheme();

  const [open, setOpen] = useState(false);
  if (status === "loading" || "unauthenticated") {
    return null;
  }

  return (
    <>
      <ArrowPopper
        content={
          <Paper className={classes.root}>
            <Stack spacing={2} className={classes.items}>
              <Stack sx={{ paddingLeft: 3 }} spacing={3}>
                <Stack direction="row" justifyContent="flex-start" alignItems="center" spacing={2}>
                  <Avatar
                    sx={{
                      bgcolor: `${theme.colors.palette.focus.main}20`,
                    }}>
                    <Icon
                      iconName={ICON_NAME.ORGANIZATION}
                      htmlColor={theme.colors.palette.focus.main}
                      fontSize="small"
                    />
                  </Avatar>
                  <Text typo="section heading">{session?.user?.organization || "No Organization"}</Text>
                </Stack>
                <Text typo="body 2">{session?.user?.name || "Username"}</Text>
                <Text typo="caption">
                  {session?.user?.user_roles && session.user.user_roles.length > 0
                    ? session.user.user_roles[0]
                    : "User"}
                </Text>
              </Stack>
              <Divider className={classes.divider} />
              <ListItemButton className={classes.listButton} onClick={() => signOut()}>
                <ListItemIcon
                  sx={{
                    minWidth: 35,
                  }}>
                  <Icon
                    iconName={ICON_NAME.SIGNOUT}
                    htmlColor={theme.colors.useCases.alertSeverity.error.main}
                    fontSize="small"
                  />
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Text className={classes.logoutText} typo="object heading">
                      Logout
                    </Text>
                  }
                />
              </ListItemButton>
            </Stack>
          </Paper>
        }
        open={open}
        placement="bottom"
        onClose={() => setOpen(false)}>
        <IconButton
          onClick={() => {
            setOpen(!open);
          }}
          size="small">
          <Avatar
            alt={session?.user?.name || "User"}
            src={session?.user?.image || "https://assets.plan4better.de/img/no-user-thumb.jpg"}
          />
        </IconButton>
      </ArrowPopper>
    </>
  );
}

const useStyles = makeStyles({ name: { UserInfoMenu } })((theme) => ({
  root: {
    maxWidth: 350,
    minWidth: 240,
    overflow: "auto",
    paddingBottom: theme.spacing(2),
  },
  items: {
    ".MuiStack-root": {
      paddingTop: theme.spacing(2),
      paddingBottom: theme.spacing(2),
    },
  },
  listButton: {
    paddingLeft: theme.spacing(3),
    "&:hover": {
      backgroundColor: theme.colors.useCases.surfaces.surface2,
    },
  },
  divider: {
    borderBottomWidth: 2,
  },
  logoutText: {
    color: theme.colors.useCases.alertSeverity.error.main,
  },
}));
