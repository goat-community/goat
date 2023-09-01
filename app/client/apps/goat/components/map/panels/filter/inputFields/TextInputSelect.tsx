import React, { useRef } from "react";
import { makeStyles } from "@/lib/theme";
import { MenuItem, Select, InputBase, TextField } from "@mui/material";
import type { Option } from "@p4b/types/atomicComponents";
import { v4 } from "uuid";
import { Icon } from "@p4b/ui/components/Icon";
import { ICON_NAME } from "@p4b/ui/components/Icon";
import { useTheme } from "@/lib/theme";

interface TextInputSelectProps {
  setInputValue: (value: string | number) => void;
  inputValue: string | number;
  options: Option[];
  type?: "number" | "text";
}

const TextInputSelect = (props: TextInputSelectProps) => {
  const { inputValue, setInputValue, options, type = "text" } = props;
  const input = useRef<HTMLInputElement | null>(null);
  const { classes } = useStyles();
  const theme = useTheme();

  const handleInputChange = (event) => {
    setInputValue(event.target.value);
  };

  const handleSelectChange = (event) => {
    setInputValue(event.target.value);
  };

  const increaseNumber = () => {
    if(input.current){
      input.current.stepUp()
      setInputValue(input.current.value);
    }
  }

  const decreaseNumber = () => {
    if(input.current){
      input.current.stepDown()
      setInputValue(input.current.value);
    }
  }


  return (
    <div className={classes.container}>
      <TextField
        className={classes.input}
        size="small"
        inputRef={input}
        value={inputValue}
        onChange={handleInputChange}
        type={type}
      />
      {type === "number" ? (
        <div className={classes.numberArrows}>
          <Icon iconName={ICON_NAME.STEPUP} viewBox="0 0 10 5" htmlColor={theme.colors.palette.focus.main} style={{ height: "13px", cursor: "pointer"}} onClick={increaseNumber}/>
          <Icon iconName={ICON_NAME.STEPDOWN} viewBox="0 0 45 24" htmlColor={theme.colors.palette.focus.main} style={{ height: "13px", cursor: "pointer" }} onClick={decreaseNumber}/>
        </div>
      ) : null}
      <div className={classes.select}>
        {options ? (
          <Select
            size="small"
            value=""
            onChange={handleSelectChange}
            input={<InputBase />}
            MenuProps={{
              classes: {
                paper: classes.selectDropdown,
              },
              anchorOrigin: {
                vertical: "bottom",
                horizontal: "right",
              },
              transformOrigin: {
                vertical: "top",
                horizontal: "right",
              },
            }}>
            {options.map((option) => (
              <MenuItem key={v4()} value={option.value}>
                {option.label}
              </MenuItem>
            ))}
          </Select>
        ) : null}
      </div>
    </div>
  );
};

const useStyles = makeStyles({ name: { TextInputSelect } })((theme) => ({
  inputWrapper: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    border: `1px solid ${theme.colors.palette.light.greyVariant2}`,
    borderRadius: "4px",
    "&:hover": {
      borderColor: theme.colors.palette.dark.main,
    },
  },
  container: {
    display: "flex",
    border: `1px solid ${theme.colors.palette.light.greyVariant2}`,
    borderRadius: 4,
    overflow: "hidden",
    position: "relative",
  },
  input: {
    flex: 9,
    "& .mui-1d3z3hw-MuiOutlinedInput-notchedOutline": {
      border: "none",
    },
  },
  select: {
    flex: 1,
    backgroundColor: "transparent",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    paddingLeft: "7px",
    borderLeft: `1px solid ${theme.colors.palette.light.greyVariant2}`,
  },
  selectDropdown: {
    position: "absolute",
    width: "265px",
    marginTop: "6px",
    zIndex: 1000,
  },
  numberArrows: {
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    padding: "0 8px",
    borderLeft: `1px solid ${theme.colors.palette.light.greyVariant2}`
  },
}));

export default TextInputSelect;
