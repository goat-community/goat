import { IconName, library } from "@fortawesome/fontawesome-svg-core";
import {
  faLayerGroup,
  faList,
  faChartSimple,
  faFileInvoice,
  faQuestionCircle,
  faToolbox,
  faFilter,
  faCompassDrafting,
  faPalette,
  IconDefinition,
  faSignOut,
  faBuildingUser,
  faBuilding,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { SvgIcon, SvgIconProps } from "@mui/material";

export enum ICON_NAME {
  LAYERS = "layers",
  LEGEND = "legend",
  CHART = "chart",
  REPORT = "report",
  HELP = "help",
  TOOLBOX = "toolbox",
  FILTER = "filter",
  SCENARIO = "scenario",
  STYLE = "style",
  SIGNOUT = "signout",
  ORGANIZATION = "organization",
}

const nameToIcon: { [k in ICON_NAME]: IconDefinition } = {
  [ICON_NAME.LAYERS]: faLayerGroup,
  [ICON_NAME.LEGEND]: faList,
  [ICON_NAME.CHART]: faChartSimple,
  [ICON_NAME.REPORT]: faFileInvoice,
  [ICON_NAME.HELP]: faQuestionCircle,
  [ICON_NAME.TOOLBOX]: faToolbox,
  [ICON_NAME.FILTER]: faFilter,
  [ICON_NAME.SCENARIO]: faCompassDrafting,
  [ICON_NAME.STYLE]: faPalette,
  [ICON_NAME.SIGNOUT]: faSignOut,
  [ICON_NAME.ORGANIZATION]: faBuilding,
};

library.add(...Object.values(nameToIcon));

export function FaIcon({ iconName, ...rest }: SvgIconProps & { iconName: ICON_NAME }) {
  if (!(iconName in nameToIcon)) {
    throw new Error(`Invalid icon name: ${iconName}`);
  }
  return (
    <SvgIcon {...rest}>
      <FontAwesomeIcon icon={nameToIcon[iconName]} />
    </SvgIcon>
  );
}
