import React from "react";

import { GOATLogoIconOnlyGreen } from "../../../../assets/svg/GOATLogoIconOnlyGreen";
import { makeStyles } from "../../../../lib/ThemeProvider";
import { Icon, Text } from "../../../theme";

const MoreMenu = () => {
  const { classes, cx } = useStyles();

  const defaultOptions = [
    [
      {
        name: "Info",
        icon: <Icon size="small" iconId="info" className={classes.icon} />,
      },
      {
        name: "View",
        icon: <Icon size="small" iconId="view" className={classes.icon} />,
      },
      {
        name: "Info",
        icon: <GOATLogoIconOnlyGreen className={cx(classes.goatIconSize, classes.icon)} />,
      },
    ],
    [
      {
        name: "Duplicate",
        icon: <Icon size="small" iconId="duplicate" className={classes.icon} />,
      },
      {
        name: "Move",
        icon: <Icon size="small" iconId="moveFile" className={classes.icon} />,
      },
      {
        name: "Delete",
        icon: <Icon size="small" iconId="delete" className={classes.icon} />,
      },
    ],
    [
      {
        name: "Share",
        icon: <Icon size="small" iconId="reply" className={classes.icon} />,
      },
      {
        name: "Download",
        icon: <Icon size="small" iconId="download" className={classes.icon} />,
      },
    ],
  ];

  return (
    <div>
      {defaultOptions.map((options, index) => (
        <div key={index} className={classes.section}>
          {options.map((option, indx) => (
            <div key={indx} className={classes.option}>
              {/* <span className={classes.icon}>{option.icon}</span> */}
              {option.icon}
              <Text typo="label 2">{option.name}</Text>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};

const useStyles = makeStyles({ name: { MoreMenu } })((theme) => ({
  option: {
    display: "flex",
    alignItems: "center",
    gap: theme.spacing(2),
    padding: `${theme.spacing(1)}px ${theme.spacing(3)}px`,
    cursor: "pointer",
    "&:hover": {
      backgroundColor: `${theme.colors.palette[theme.isDarkModeEnabled ? "dark" : "light"].greyVariant1}80`,
    },
  },
  icon: {
    opacity: 0.5,
  },
  section: {
    margin: `${theme.spacing(2)}px 0px`,
  },
  goatIconSize: {
    width: "20px",
    height: "20px",
  },
}));

export default MoreMenu;
