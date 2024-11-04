import { useState } from "react";

import { ICON_NAME } from "@p4b/ui/components/Icon";

import { useTranslation } from "@/i18n/client";

import type { Layer } from "@/lib/validations/layer";
import type { Project } from "@/lib/validations/project";

import { ContentActions } from "@/types/common";

import type { PopperMenuItem } from "@/components/common/PopperMenu";

export const useContentMoreMenu = () => {
  const { t } = useTranslation("common");
  const getMoreMenuOptions = function (contentType: "project" | "layer") {
    if (contentType === "layer") {
      const layerMoreMenuOptions: PopperMenuItem[] = [
        {
          id: ContentActions.EDIT_METADATA,
          label: t("edit_metadata"),
          icon: ICON_NAME.EDIT,
        },
        {
          id: ContentActions.MOVE_TO_FOLDER,
          label: t("move_to_folder"),
          icon: ICON_NAME.FOLDER,
        },
        {
          id: ContentActions.DOWNLOAD,
          label: t("download"),
          icon: ICON_NAME.DOWNLOAD,
        },
        {
          id: ContentActions.SHARE,
          label: t("share"),
          icon: ICON_NAME.SHARE,
        },
        {
          id: ContentActions.DELETE,
          label: t("delete"),
          icon: ICON_NAME.TRASH,
          color: "error.main",
        },
      ];
      return layerMoreMenuOptions;
    }
    if (contentType === "project") {
      const projectMoreMenuOptions: PopperMenuItem[] = [
        {
          id: ContentActions.EDIT_METADATA,
          label: t("edit_metadata"),
          icon: ICON_NAME.EDIT,
        },
        {
          id: ContentActions.MOVE_TO_FOLDER,
          label: t("move_to_folder"),
          icon: ICON_NAME.FOLDER,
        },
        {
          id: ContentActions.SHARE,
          label: t("share"),
          icon: ICON_NAME.SHARE,
        },
        {
          id: ContentActions.DELETE,
          label: t("delete"),
          icon: ICON_NAME.TRASH,
          color: "error.main",
        },
      ];
      return projectMoreMenuOptions;
    }
    return [];
  };

  const [activeContent, setActiveContent] = useState<Project | Layer>();
  const [moreMenuState, setMoreMenuState] = useState<PopperMenuItem>();

  const closeMoreMenu = () => {
    setActiveContent(undefined);
    setMoreMenuState(undefined);
  };

  const openMoreMenu = (menuItem: PopperMenuItem, contentItem: Project | Layer) => {
    setActiveContent(contentItem);
    setMoreMenuState(menuItem);
  };

  return {
    getMoreMenuOptions,
    activeContent,
    moreMenuState,
    closeMoreMenu,
    openMoreMenu,
  };
};
