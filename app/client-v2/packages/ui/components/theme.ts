import CheckIcon from "@mui/icons-material/Check";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import CloseIcon from "@mui/icons-material/Close";
import CorporateFareIcon from "@mui/icons-material/CorporateFare";
import CreateNewFolderIcon from "@mui/icons-material/CreateNewFolder";
import DeleteIcon from "@mui/icons-material/Delete";
import DirectionsBusIcon from "@mui/icons-material/DirectionsBus";
import DirectionsRunIcon from "@mui/icons-material/DirectionsRun";
import DownloadIcon from "@mui/icons-material/Download";
import DriveFileMoveIcon from "@mui/icons-material/DriveFileMove";
import EditIcon from "@mui/icons-material/Edit";
import EmailIcon from "@mui/icons-material/Email";
import ErrorIcon from "@mui/icons-material/Error";
import ErrorOutlineIcon from "@mui/icons-material/ErrorOutline";
import FileCopyIcon from "@mui/icons-material/FileCopy";
import FilterListIcon from "@mui/icons-material/FilterList";
import FolderIcon from "@mui/icons-material/Folder";
import FormatAlignLeftIcon from "@mui/icons-material/FormatAlignLeft";
import GroupsIcon from "@mui/icons-material/Groups";
import HelpIcon from "@mui/icons-material/Help";
import HomeIcon from "@mui/icons-material/Home";
import InfoIcon from "@mui/icons-material/Info";
import InsertDriveFileIcon from "@mui/icons-material/InsertDriveFile";
import LocalPhoneIcon from "@mui/icons-material/LocalPhone";
import LockIcon from "@mui/icons-material/Lock";
import MoreHorizIcon from "@mui/icons-material/MoreHoriz";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import NoteAddIcon from "@mui/icons-material/NoteAdd";
import OpenInNewIcon from "@mui/icons-material/OpenInNew";
import PersonIcon from "@mui/icons-material/Person";
import PowerSettingsNewIcon from "@mui/icons-material/PowerSettingsNew";
import ReplyIcon from "@mui/icons-material/Reply";
import RocketLaunchIcon from "@mui/icons-material/RocketLaunch";
import RoomIcon from "@mui/icons-material/Room";
import SearchIcon from "@mui/icons-material/Search";
import SettingsIcon from "@mui/icons-material/Settings";
import SettingsSuggestIcon from "@mui/icons-material/SettingsSuggest";
import ViewModuleIcon from "@mui/icons-material/ViewModule";
import VisibilityIcon from "@mui/icons-material/Visibility";
import LayersIcon from '@mui/icons-material/Layers';
import FormatListBulletedIcon from '@mui/icons-material/FormatListBulleted';
import AssessmentIcon from '@mui/icons-material/Assessment';
import type { Param0 } from "tsafe";

import { createButton } from "../components/Button";
import { createThemeProvider, defaultGetTypographyDesc } from "../lib";
import { createIcon } from "./DataDisplay/Icon";
import { createIconButton } from "./DataDisplay/IconButton";
import { createText } from "./DataDisplay/Text";

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
  moreHorizontal: MoreHorizIcon,
  warn: ErrorIcon,
  warnOutlined: ErrorOutlineIcon,
  check: CheckCircleIcon,
  checkOutlined: CheckCircleOutlineIcon,
  email: EmailIcon,
  search: SearchIcon,
  settingsSuggested: SettingsSuggestIcon,
  phone: LocalPhoneIcon,
  marker: RoomIcon,
  viewModul: ViewModuleIcon,
  formatLeft: FormatAlignLeftIcon,
  newFolder: CreateNewFolderIcon,
  newFile: NoteAddIcon,
  edit: EditIcon,
  open: OpenInNewIcon,
  noBgCheck: CheckIcon,
  view: VisibilityIcon,
  info: InfoIcon,
  duplicate: FileCopyIcon,
  moveFile: DriveFileMoveIcon,
  delete: DeleteIcon,
  reply: ReplyIcon,
  download: DownloadIcon,
  lock: LockIcon,
  team: GroupsIcon,
  layers: LayersIcon, 
  list: FormatListBulletedIcon,
  report: AssessmentIcon,
});

export type IconId = Param0<typeof Icon>["iconId"];

export const { IconButton } = createIconButton({ Icon });

export const { Button } = createButton({ Icon });

export const { Text } = createText({ useTheme });
