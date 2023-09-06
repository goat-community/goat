import BasicAccordion from "@p4b/ui/components/BasicAccordion";
import { makeStyles } from "@/lib/theme";
import type { SelectChangeEvent } from "@mui/material";
import {
  Divider,
  FormControl,
  MenuItem,
  Select,
  Typography,
} from "@mui/material";
import { Icon, ICON_NAME } from "@p4b/ui/components/Icon";
import { useTheme } from "@p4b/ui/components/theme";
import { useDispatch } from "react-redux";
import {
  deleteLayerFillOutLineColor,
  setLayerFillOutLineColor,
} from "@/lib/store/styling/slice";

const SelectStrokeOptionFill = () => {
  const { classes } = useStyles();
  const theme = useTheme();
  const dispatch = useDispatch();

  const handleSelectChange = (event: SelectChangeEvent<string>) => {
    if (event.target.value === "line") {
      dispatch(setLayerFillOutLineColor("#000"));
    } else if (event.target.value === "empty") {
      dispatch(deleteLayerFillOutLineColor());
    }
  };

  return (
    <div>
      <BasicAccordion title="Stroke" variant="secondary">
        <FormControl sx={{ m: 1, width: "100%" }}>
          <Select
            size="small"
            className={classes.select}
            defaultValue="line"
            onChange={handleSelectChange}
          >
            <MenuItem value="empty" className={classes.menuItem}>
              <Icon
                iconName={ICON_NAME.CLOSE}
                htmlColor={theme.colors.palette.redError.main}
                fontSize="small"
              />
              <Typography variant="body2">Hide stroke</Typography>
            </MenuItem>
            <MenuItem value="line" className={classes.menuItem}>
              <Divider className={classes.divider} />
            </MenuItem>
          </Select>
        </FormControl>
      </BasicAccordion>
    </div>
  );
};

const useStyles = makeStyles({ name: { SelectStrokeOptionFill } })(() => ({
  select: {
    "& .MuiSelect-select": {
      display: "flex",
      columnGap: "8px",
      alignItems: "center",
    },
  },
  menuItem: {
    display: "flex",
    columnGap: "8px",
    alignItems: "center",
    height: "32px",
  },
  divider: {
    width: "100%",
    borderTop: "none",
    borderBottom: "1px solid black",
  },
}));

export default SelectStrokeOptionFill;
