import DownloadModal from "@/components/modals/DownloadModal";
import MoveModal from "@/components/modals/MoveModal";
import ShareModal from "@/components/modals/ShareModal";
import { useRouter } from "next/navigation";
import React, { useState } from "react";
import { v4 } from "uuid";

import Modal from "@p4b/ui/components/Modal";
import { Icon, Text, IconButton } from "@p4b/ui/components/theme";
import { makeStyles } from "@p4b/ui/lib/ThemeProvider";
import type {IDashboardTableRowInfo} from "@/types/dashboard/content";

interface MoreMenuProps {
  rowInfo: IDashboardTableRowInfo | null;
  handleDeleteItem: (object: IDashboardTableRowInfo | null) => void;
}

interface IComponentOptions {
  [key: string]: React.ReactElement;
}

const MoreMenu = (props: MoreMenuProps) => {
  const { rowInfo, handleDeleteItem } = props;

  // Component States
  const [selectedOption, setSelectedOption] = useState<{
    name: string;
    icon: React.ReactNode;
    value: string;
  } | null>(null);

  const { classes } = useStyles();
  const router = useRouter();

  const defaultOptions = [
    [
      {
        value: "Info",
        name: "Info",
        icon: <Icon size="small" iconId="info" className={classes.icon} />,
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

  if (rowInfo?.label === "layer") {
    defaultOptions[0].push({
      value: "View",
      name: "View",
      icon: <Icon size="small" iconId="view" className={classes.icon} />,
    });
  }

  const componentOptions: IComponentOptions = {
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

  const handleSelectOption = (item) => {
    setSelectedOption(item);

    if (item.name === "View") {
      router.push(`/content/preview/${rowInfo?.id}`);
    }

    if (item.name === "Delete") {
      handleDeleteItem(rowInfo);
    }
  };

  const handleCloseModal = () => {
    setSelectedOption(null);
  };

  return (
    <div>
      {defaultOptions.map((options) => (
        <div key={v4()} className={classes.section}>
          {options.map((option) => (
            <div key={v4()} className={classes.option} onClick={() => handleSelectOption(option)}>
              {option.icon}
              <Text typo="body 1">{option.name}</Text>
            </div>
          ))}
        </div>
      ))}
      <Modal
        width="444px"
        header={
          <div className={classes.modalHeader}>
            <Text typo="subtitle" className={classes.headerText}>
              {selectedOption?.name || ""}
            </Text>
            <IconButton onClick={handleCloseModal} iconId="close" />
          </div>
        }
        open={selectedOption?.name === "Download"}
        changeOpen={handleCloseModal}>
        {selectedOption ? componentOptions[selectedOption.value] : "Download"}
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
