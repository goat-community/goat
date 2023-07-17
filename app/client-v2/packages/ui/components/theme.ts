import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import CloseIcon from "@mui/icons-material/Close";
import CorporateFareIcon from "@mui/icons-material/CorporateFare";
import DirectionsBusIcon from "@mui/icons-material/DirectionsBus";
import DirectionsRunIcon from "@mui/icons-material/DirectionsRun";
import EmailIcon from "@mui/icons-material/Email";
import ErrorIcon from "@mui/icons-material/Error";
import ErrorOutlineIcon from "@mui/icons-material/ErrorOutline";
import FilterListIcon from "@mui/icons-material/FilterList";
import FolderIcon from "@mui/icons-material/Folder";
import HelpIcon from "@mui/icons-material/Help";
import HomeIcon from "@mui/icons-material/Home";
import InsertDriveFileIcon from "@mui/icons-material/InsertDriveFile";
import LocalPhoneIcon from "@mui/icons-material/LocalPhone";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import PersonIcon from "@mui/icons-material/Person";
import PowerSettingsNewIcon from "@mui/icons-material/PowerSettingsNew";
import RocketLaunchIcon from "@mui/icons-material/RocketLaunch";
import RoomIcon from "@mui/icons-material/Room";
import SearchIcon from "@mui/icons-material/Search";
import SettingsIcon from "@mui/icons-material/Settings";
import SettingsSuggestIcon from "@mui/icons-material/SettingsSuggest";
import type { Param0 } from "tsafe";

import "../assets/fonts/mulish/font.css";
import { createButton } from "../components/Button";
import { createIcon } from "../components/Icon/Icon";
import { createIconButton } from "../components/Icon/IconButton";
import { createText } from "../components/Text";
import { createThemeProvider, defaultGetTypographyDesc } from "../lib";

export const { ThemeProvider, StoryProvider, useTheme } = createThemeProvider({
  isReactStrictModeEnabled: false,
  getTypographyDesc: () => ({
    ...defaultGetTypographyDesc(),
    fontFamily: "'Mulish', sans-serif",
    rootFontSizePx: 16,
  }),
});

export const { Icon } = createIcon({
  help: HelpIcon,
  home: HomeIcon,
  coorperate: CorporateFareIcon,
  powerOff: PowerSettingsNewIcon,
  rocketLaunch: RocketLaunchIcon,
  run: DirectionsRunIcon,
  bus: DirectionsBusIcon,
  file: InsertDriveFileIcon,
  close: CloseIcon,
  user: PersonIcon,
  filter: FilterListIcon,
  folder: FolderIcon,
  settings: SettingsIcon,
  moreVert: MoreVertIcon,
  warn: ErrorIcon,
  warnOutlined: ErrorOutlineIcon,
  check: CheckCircleIcon,
  email: EmailIcon,
  search: SearchIcon,
  settingsSuggested: SettingsSuggestIcon,
  phone: LocalPhoneIcon,
  marker: RoomIcon,
});

export type IconId = Param0<typeof Icon>["iconId"];

export const { IconButton } = createIconButton({ Icon });

export const { Button } = createButton({ Icon });

export const { Text } = createText({ useTheme });
