import React, { useState, useEffect } from "react";
import { v4 } from "uuid";

import { makeStyles } from "../../../../lib/ThemeProvider";
import Modal from "../../../Modal";
import { Icon, Text, IconButton } from "../../../theme";
import DownloadModal from "./DownloadModal";
import MoveModal from "./MoveModal";
import ShareModal from "./ShareModal";

interface MoreMenuProps {
  rowInfo: { name: React.ReactNode; type: React.ReactNode; modified: string; size: string } | null;
}

const MoreMenu = (props: MoreMenuProps) => {
  const { rowInfo } = props;

  const { classes, cx } = useStyles();

  // Component States
  const [selectedOption, setSelectedOption] = useState<{
    name: string;
    icon: React.ReactNode;
    value: string;
  } | null>(null);

  // Options to show in the More Menu
  const defaultOptions = [
    [
      {
        value: "Info",
        name: "Info",
        icon: <Icon size="small" iconId="info" className={classes.icon} />,
      },
      {
        value: "View",
        name: "View",
        icon: <Icon size="small" iconId="view" className={classes.icon} />,
      },
    ],
    [
      {
        value: "Duplicate",
        name: "Duplicate",
        icon: <Icon size="small" iconId="duplicate" className={classes.icon} />,
      },
      {
        value: "Move",
        name: "Move",
        icon: <Icon size="small" iconId="moveFile" className={classes.icon} />,
      },
      {
        value: "Delete",
        name: "Delete",
        icon: <Icon size="small" iconId="delete" className={classes.icon} />,
      },
    ],
    [
      {
        value: "Share",
        name: "Share",
        icon: <Icon size="small" iconId="reply" className={classes.icon} />,
      },
      {
        value: "Download",
        name: "Download",
        icon: <Icon size="small" iconId="download" className={classes.icon} />,
      },
    ],
  ];

  useEffect(() => {
    console.log(selectedOption);
  }, [selectedOption]);

  interface ComponentOptions {
    [key: string]: React.ReactElement<any, any>;
  }

  /**
   * Defines a componentOptions object that contains different modals for various actions.
   * @param {ComponentOptions} componentOptions - The options for different modals.
   * @returns None
   */
  const componentOptions: ComponentOptions = {
    Download: <DownloadModal name={rowInfo ? rowInfo.name : ""} changeState={setSelectedOption} />,
    Share: (
      <ShareModal
        name={rowInfo ? rowInfo.name : ""}
        changeState={setSelectedOption}
        modalState={selectedOption}
      />
    ),
    Move: <MoveModal changeState={setSelectedOption} />,
  };

  return (
    <div>
      {defaultOptions.map((options) => (
        <div key={v4()} className={classes.section}>
          {options.map((option) => (
            <div key={v4()} className={classes.option} onClick={() => setSelectedOption(option)}>
              {/* <span className={classes.icon}>{option.icon}</span> */}
              {option.icon}
              <Text typo="label 2">{option.name}</Text>
            </div>
          ))}
        </div>
      ))}
      <Modal
        width="444px"
        header={
          <div className={classes.modalHeader}>
            <Text typo="section heading" className={classes.headerText}>
              {selectedOption ? selectedOption.name : ""}
            </Text>
            <IconButton onClick={() => setSelectedOption(null)} iconId="close" />
          </div>
        }
        open={selectedOption ? true : false}
        changeOpen={() => setSelectedOption(null)}>
        {
          componentOptions[
            selectedOption !== null && ["Download", "Share", "Move"].includes(selectedOption.value)
              ? selectedOption.value
              : "Download"
          ]
        }
      </Modal>
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
  modalHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  headerText: {
    fontWeight: "normal",
  },
}));

export default MoreMenu;
