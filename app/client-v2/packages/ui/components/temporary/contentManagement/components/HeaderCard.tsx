import { useState } from "react";

import { makeStyles } from "../../../../lib/ThemeProvider";
import { ToggleTabs } from "../../../Navigation/ToggleTabs";
import { Card } from "../../../Surfaces";
import { Button, Text, Icon } from "../../../theme";
import DashboardLayout from "../../DashboardLayout";

const HeaderCard = () => {
  const { classes } = useStyles();
  const [value, setValue] = useState<string | null>("formatLeft");

  return (
    <Card noHover={true} width="100%" className={classes.headerCard}>
      <div className={classes.headerContainer}>
        <div className={classes.headerPath}>
          <Text typo="section heading" className={classes.headerText}>
            Library
          </Text>
          <span style={{ display: "flex", alignItems: "center" }}>
            <Icon iconId="home" className={classes.icon} size="small" iconVariant="gray" />{" "}
            <Text typo="body 2">Home</Text> <Text typo="body 2">/</Text>
          </span>
        </div>
        <div className={classes.headerActions}>
          <span style={{ display: "flex", gap: "10px" }}>
            <Button variant="noBorder">
              <Icon iconId="newFolder" className={classes.icon} size="small" iconVariant="gray" /> New folder
            </Button>
            <Button variant="noBorder" className={classes.headerText}>
              <Icon iconId="newFile" className={classes.icon} size="small" iconVariant="gray" /> Add content
            </Button>
          </span>
          <ToggleTabs
            defaultValue={value}
            onResultChange={setValue}
            tabs={[
              {
                iconId: "formatLeft",
                value: "formatLeft",
              },
              {
                iconId: "viewModul",
                value: "viewModul",
              },
            ]}
          />
        </div>
      </div>
    </Card>
  );
};

const useStyles = makeStyles({ name: { DashboardLayout } })((theme) => ({
  headerCard: {
    marginBottom: theme.spacing(3),
  },
  headerContainer: {
    padding: `${theme.spacing(2)}px ${theme.spacing(3)}px`,
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    width: "100%",
  },
  headerText: {
    fontWeight: 800,
    width: "fit-content",
  },
  headerPath: {
    width: "30%",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
  },
  headerActions: {
    width: "30%",
    display: "flex",
    alignItems: "center",
    justifyContent: "end",
    gap: theme.spacing(5) + theme.spacing(3),
  },
  icon: {
    marginRight: "10px",
  },
}));

export default HeaderCard;
