import DescriptionIcon from "@mui/icons-material/Description";
import HelpIcon from "@mui/icons-material/Help";
import HomeIcon from "@mui/icons-material/Home";

import { createIcon } from "./Icon";

export const { Icon } = createIcon({
  help: HelpIcon,
  home: HomeIcon,
  file: DescriptionIcon,
});
