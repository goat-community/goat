/* eslint-disable @typescript-eslint/no-explicit-any */
import Autocomplete from "@mui/material/Autocomplete";
import parse from "@/lib/utils/parse";
import { useEffect, useMemo, useState } from "react";
import Typography from "@mui/material/Typography";
import { useMap } from "react-map-gl";
import { makeStyles } from "@/lib/theme";
import Paper from "@mui/material/Paper";
import InputBase from "@mui/material/InputBase";
import {
  Divider,
  Fab,
  IconButton,
  ListItemButton,
  ListItemText,
  Popper,
  Tooltip,
  debounce,
} from "@mui/material";
import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";
import search from "@/lib/services/geocoder";
import type { FeatureCollection } from "geojson";
import { match } from "@/lib/utils/match";

type Props = {
  endpoint?: string;
  source?: string;
  accessToken: string;
  proximity?: { longitude: number; latitude: number };
  country?: string;
  bbox?: number[];
  types?: string;
  limit?: number;
  autocomplete?: boolean;
  language?: string;
  pointZoom?: number;
};

export interface Result {
  feature: Feature;
  label: string;
}

interface Feature {
  id: string;
  type: string;
  place_type: string[];
  relevance: number;
  properties: Properties;
  text: string;
  place_name: string;
  center: [number, number];
  geometry: Geometry;
  address: string;
  context: Context[];
}

interface Context {
  id: string;
  text: string;
  wikidata?: string;
  short_code?: string;
}

interface Geometry {
  type: string;
  coordinates: [number, number];
  interpolated: boolean;
}

interface Properties {
  accuracy: string;
}

const COORDINATE_REGEX_STRING =
  "^[-+]?([1-8]?\\d(\\.\\d+)?|90(\\.0+)?),\\s*[-+]?(180(\\.0+)?|((1[0-7]\\d)|([1-9]?\\d))(\\.\\d+)?)";
const COORDINATE_REGEX = RegExp(COORDINATE_REGEX_STRING);
export const testForCoordinates = (query: string): [true, number, number] | [false, string] => {
  const isValid = COORDINATE_REGEX.test(query.trim());

  if (!isValid) {
    return [isValid, query];
  }

  const tokens = query.trim().split(",");

  return [isValid, Number(tokens[0]), Number(tokens[1])];
};

export default function Geocoder({
  endpoint = "https://api.mapbox.com",
  source = "mapbox.places",
  pointZoom = 15,
  accessToken,
  proximity,
  country,
  bbox,
  types,
  limit,
  autocomplete,
  language,
}: Props) {
  const [value, setValue] = useState<Result | null>(null);
  const [options, setOptions] = useState<readonly Result[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [focused, setFocused] = useState(false);
  const [collapsed, setCollapsed] = useState(true);
  const { map } = useMap();
  const { classes } = useStyles({ focused });

  const fetch = useMemo(
    () =>
      debounce((request: { value: string }, onresult: (_error: Error, fc: FeatureCollection) => void) => {
        search(
          endpoint,
          source,
          accessToken,
          request.value,
          onresult,
          proximity,
          country,
          bbox,
          types,
          limit,
          autocomplete,
          language
        );
      }, 400),
    [accessToken, autocomplete, bbox, country, endpoint, language, limit, proximity, source, types]
  );

  useEffect(() => {
    let active = true;
    if (inputValue === "") {
      setOptions(value ? [value] : []);
      return undefined;
    }
    const resultCoordinates = testForCoordinates(inputValue);
    if (resultCoordinates[0]) {
      const [_, latitude, longitude] = resultCoordinates;
      setOptions([
        {
          feature: {
            id: "",
            type: "Feature",
            place_type: ["coordinate"],
            relevance: 1,
            properties: {
              accuracy: "point",
            },
            text: "",
            place_name: "",
            center: [longitude, latitude],
            geometry: {
              type: "Point",
              coordinates: [longitude, latitude],
              interpolated: false,
            },
            address: "",
            context: [],
          },
          label: `${latitude}, ${longitude}`,
        },
      ]);
      return undefined;
    }
    fetch({ value: inputValue }, (error: Error, fc: FeatureCollection) => {
      if (active) {
        if (!error && fc && fc.features) {
          setOptions(
            fc.features
              .map((feature) => ({
                feature: feature,
                label: feature.place_name,
              }))
              .filter((feature) => feature.label)
          );
        }
      }
    });

    return () => {
      active = false;
    };
  }, [value, inputValue, fetch]);
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
              filterOptions={(x) => x}
              options={options}
              autoComplete
              includeInputInList
              filterSelectedOptions
              value={value}
              inputValue={inputValue}
              PopperComponent={({ style, ...props }) => (
                <Popper
                  {...props}
                  modifiers={[
                    {
                      name: "flip",
                      options: {
                        fallbackPlacements: [],
                      },
                    },
                    {
                      name: "offset",
                      options: {
                        offset: [0, 15],
                      },
                    },
                  ]}
                  sx={{
                    boxShadow: 2,
                  }}
                  className={classes.popper}
                  style={{ ...style, width: 350 }}
                />
              )}
              ListboxProps={{ className: classes.listBox }}
              clearIcon={null}
              onChange={(_event: any, newValue: Result | null) => {
                setOptions(newValue ? [newValue, ...options] : options);
                setValue(newValue);
                if (newValue?.feature?.center)
                  map.flyTo({
                    center: newValue?.feature.center,
                    zoom: pointZoom,
                  });
              }}
              onInputChange={(_event, newInputValue) => {
                setInputValue(newInputValue);
              }}
              renderInput={(params) => {
                const { InputLabelProps: _, InputProps: __, ...rest } = params;
                return (
                  <Paper elevation={2} className={classes.paper}>
                    <Icon iconName={ICON_NAME.SEARCH} fontSize="small" className={classes.icon} />
                    <Divider className={classes.divider} orientation="vertical" />
                    <InputBase
                      {...params.InputProps}
                      {...rest}
                      className={classes.inputBase}
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
                        className={classes.iconButton}
                        onClick={() => {
                          setInputValue("");
                          setValue(null);
                          setOptions([]);
                        }}>
                        <Icon iconName={ICON_NAME.CLOSE} fontSize="small" className={classes.icon} />
                      </IconButton>
                    )}
                    {!inputValue && (
                      <IconButton
                        type="button"
                        className={classes.iconButton}
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
                const matches = match(option.label, inputValue);
                const parts = parse(option.label, matches);
                const { className: _, style: __, ...rest } = props;
                return (
                  <li {...rest} key={option.label}>
                    <ListItemButton className={classes.listButton}>
                      <ListItemText
                        primary={
                          <Typography noWrap className={classes.listItemTypography} variant="body2">
                            {parts.map((part: { highlight: boolean; text: string }, index: number) => (
                              <Typography
                                key={index}
                                component="span"
                                variant="inherit"
                                sx={{ fontWeight: part.highlight ? 600 : 300 }}>
                                {part.text}
                              </Typography>
                            ))}
                          </Typography>
                        }
                      />
                    </ListItemButton>
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
  paper: {
    padding: theme.spacing(0.5),
    display: "flex",
    alignItems: "center",
    width: 350,
  },
  listBox: {
    maxHeight: "176px",
    overflow: "hidden",
  },
  divider: {
    height: 28,
    margin: theme.spacing(0.5),
  },
  inputBase: {
    marginLeft: theme.spacing(1),
    flex: 1,
    padding: 0,
  },
  iconButton: {
    padding: theme.spacing(1),
  },
  popper: {},
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
  listItemTypography: {
    textOverflow: "ellipsis",
    overflow: "hidden",
    width: "270px",
  },
  listButton: {
    paddingLeft: theme.spacing(3),
    "&:hover": {
      backgroundColor: theme.colors.useCases.surfaces.surface2,
    },
  },
}));
