import Autocomplete from "@mui/material/Autocomplete";
import parse from "@/lib/utils/parse";
import { useRef, useState } from "react";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import LocationOnIcon from "@mui/icons-material/LocationOn";
import { useMap } from "react-map-gl";
import { makeStyles } from "@/lib/theme";
import Paper from "@mui/material/Paper";
import InputBase from "@mui/material/InputBase";
import { Divider, Fab, IconButton, Popper, Tooltip } from "@mui/material";
import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

const GOOGLE_MAPS_API_KEY = "AIzaSyC3aviU6KHXAjoSnxcw6qbOhjnFctbxPkE";

function loadScript(src: string, position: HTMLElement | null, id: string) {
  if (!position) {
    return;
  }

  const script = document.createElement("script");
  script.setAttribute("async", "");
  script.setAttribute("id", id);
  script.src = src;
  position.appendChild(script);
}

const autocompleteService = { current: null };
interface MainTextMatchedSubstrings {
  offset: number;
  length: number;
}
interface StructuredFormatting {
  main_text: string;
  secondary_text: string;
  main_text_matched_substrings?: readonly MainTextMatchedSubstrings[];
}
interface PlaceType {
  description: string;
  structured_formatting: StructuredFormatting;
}
const CustomPopper = (props) => {
  return (
    <Popper
      {...props}
      placement="bottom"
      sx={{
        height: "10px",
      }}
      style={{ width: "300px", height: "10px" }}
    />
  );
};

export default function Geocoder() {
  const [value, setValue] = useState<PlaceType | null>(null);
  const [inputValue, setInputValue] = useState("");
  const [options, setOptions] = useState<readonly PlaceType[]>([]);
  const [focused, setFocused] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const { map } = useMap();
  const { classes } = useStyles({ focused });

  //   if (typeof window !== "undefined" && !loaded.current) {
  //     if (!document.querySelector("#google-maps")) {
  //       loadScript(
  //         `https://maps.googleapis.com/maps/api/js?key=${GOOGLE_MAPS_API_KEY}&libraries=places`,
  //         document.querySelector("head"),
  //         "google-maps"
  //       );
  //     }

  //     loaded.current = true;
  //   }

  //   const fetch = useMemo(
  //     () =>
  //       debounce((request: { input: string }, callback: (results?: readonly PlaceType[]) => void) => {
  //         (autocompleteService.current as any).getPlacePredictions(request, callback);
  //       }, 400),
  //     []
  //   );

  //   useEffect(() => {
  //     let active = true;

  //     if (!autocompleteService.current && (window as any).google) {
  //       autocompleteService.current = new (window as any).google.maps.places.AutocompleteService();
  //     }
  //     if (!autocompleteService.current) {
  //       return undefined;
  //     }

  //     if (inputValue === "") {
  //       setOptions(value ? [value] : []);
  //       return undefined;
  //     }

  //     fetch({ input: inputValue }, (results?: readonly PlaceType[]) => {
  //       if (active) {
  //         let newOptions: readonly PlaceType[] = [];

  //         if (value) {
  //           newOptions = [value];
  //         }

  //         if (results) {
  //           newOptions = [...newOptions, ...results];
  //         }

  //         setOptions(newOptions);
  //       }
  //     });

  //     return () => {
  //       active = false;
  //     };
  //   }, [value, inputValue, fetch]);
  return (
    <>
      {map && (
        <>
          {collapsed && (
            <Tooltip title="Search" arrow placement="right">
              <Fab
                onClick={() => {
                  setCollapsed(false);
                  setFocused(false);
                }}
                size="small"
                className={classes.btn}>
                <Icon iconName={ICON_NAME.SEARCH} fontSize="small" />
              </Fab>
            </Tooltip>
          )}
          {!collapsed && (
            <Autocomplete
              className={classes.root}
              id="geocoder"
              freeSolo
              sx={{ width: 300 }}
              getOptionLabel={(option) => (typeof option === "string" ? option : option.description)}
              filterOptions={(x) => x}
              options={options}
              autoComplete
              includeInputInList
              filterSelectedOptions
              value={value}
              inputValue={inputValue}
              noOptionsText="No locations"
              PopperComponent={CustomPopper}
              clearOnBlur={false}
              clearIcon={null}
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              onChange={(_event: any, newValue: PlaceType | null) => {
                setOptions(newValue ? [newValue, ...options] : options);
                setValue(newValue);
              }}
              onInputChange={(_event, newInputValue) => {
                setInputValue(newInputValue);
              }}
              renderInput={(params) => {
                // eslint-disable-next-line @typescript-eslint/no-unused-vars
                const { InputLabelProps, InputProps, ...rest } = params;
                return (
                  <Paper
                    elevation={4}
                    sx={{ p: "2px 4px", display: "flex", alignItems: "center", width: 300 }}>
                    <Icon iconName={ICON_NAME.SEARCH} fontSize="small" className={classes.icon} />
                    <Divider sx={{ height: 28, m: 0.5 }} orientation="vertical" />
                    <InputBase
                      sx={{ ml: 1, flex: 1, padding: "0px" }}
                      {...params.InputProps}
                      {...rest}
                      placeholder="Enter an address or coordinates"
                      onBlur={() => {
                        setFocused(false);
                      }}
                      onFocus={() => {
                        setFocused(true);
                      }}
                      fullWidth
                    />
                    {inputValue && (
                      <IconButton
                        type="button"
                        sx={{ p: "5px" }}
                        onClick={() => {
                          setInputValue("");
                        }}>
                        <Icon iconName={ICON_NAME.CLOSE} fontSize="small" className={classes.icon} />
                      </IconButton>
                    )}
                    {!inputValue && (
                      <IconButton
                        type="button"
                        sx={{ p: "5px" }}
                        onClick={() => {
                          setCollapsed(true);
                        }}>
                        <Icon iconName={ICON_NAME.CHEVRON_LEFT} fontSize="small" className={classes.icon} />
                      </IconButton>
                    )}
                  </Paper>
                );
              }}
              renderOption={(props, option) => {
                const matches = option.structured_formatting.main_text_matched_substrings || [];

                const parts = parse(
                  option.structured_formatting.main_text,
                  // eslint-disable-next-line @typescript-eslint/no-explicit-any
                  matches.map((match: any) => [match.offset, match.offset + match.length])
                );

                return (
                  <li {...props}>
                    <Grid container alignItems="center">
                      <Grid item sx={{ display: "flex", width: 44 }}>
                        <LocationOnIcon sx={{ color: "text.secondary" }} />
                      </Grid>
                      <Grid item sx={{ width: "calc(100% - 44px)", wordWrap: "break-word" }}>
                        {parts.map((part, index) => (
                          <Box
                            key={index}
                            component="span"
                            sx={{ fontWeight: part.highlight ? "bold" : "regular" }}>
                            {part.text}
                          </Box>
                        ))}
                        <Typography variant="body2" color="text.secondary">
                          {option.structured_formatting.secondary_text}
                        </Typography>
                      </Grid>
                    </Grid>
                  </li>
                );
              }}
            />
          )}
        </>
      )}
    </>
  );
}

const useStyles = makeStyles<{ focused: boolean }>()((theme, { focused }) => ({
  root: {
    alignItems: "flex-start",
    marginTop: theme.spacing(1),
    marginBottom: theme.spacing(1),
  },
  icon: {
    color: focused
      ? theme.colors.palette.focus.main
      : theme.isDarkModeEnabled
      ? "white"
      : theme.colors.palette.light.greyVariant4,
    margin: theme.spacing(2),
  },
  btn: {
    backgroundColor: theme.colors.useCases.surfaces.surface2,
    color: theme.isDarkModeEnabled ? "white" : theme.colors.palette.light.greyVariant4,
  },
}));
