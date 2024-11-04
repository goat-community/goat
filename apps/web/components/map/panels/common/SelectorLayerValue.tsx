import SearchIcon from "@mui/icons-material/Search";
import {
  Box,
  Checkbox,
  FormControl,
  InputAdornment,
  ListSubheader,
  MenuItem,
  Select,
  TextField,
  Typography,
  useTheme,
} from "@mui/material";
import { useState } from "react";

import { Loading } from "@p4b/ui/components/Loading";

import { useTranslation } from "@/i18n/client";

import { useDatasetValueSelectorMethods } from "@/hooks/map/DatasetHooks";

import FormLabelHelper from "@/components/common/FormLabelHelper";
import NoValuesFound from "@/components/map/common/NoValuesFound";

export type SelectorProps = {
  selectedValues: string[] | string | null;
  onSelectedValuesChange: (values: string[] | string | null) => void;
  layerId: string;
  fieldName: string;
  label?: string;
  tooltip?: string;
  disabled?: boolean;
  multiple?: boolean;
  onFocus?: () => void;
  onClose?: () => void;
};

const SelectorLayerValue = (props: SelectorProps) => {
  const theme = useTheme();
  const [focused, setFocused] = useState(false);
  const { t } = useTranslation("common");
  const { data, isLoading, searchText, setSearchText, debouncedSetSearchText } =
    useDatasetValueSelectorMethods({
      selectedValues: props.multiple ? (props.selectedValues as string[]) : [props.selectedValues as string],
      onSelectedValuesChange: props.onSelectedValuesChange,
      fieldName: props.fieldName,
      datasetId: props.layerId,
    });

  return (
    <FormControl size="small" fullWidth>
      {props.label && (
        <FormLabelHelper
          label={props.label}
          color={
            props.disabled ? theme.palette.secondary.main : focused ? theme.palette.primary.main : "inherit"
          }
          tooltip={props.tooltip}
        />
      )}
      <Select
        fullWidth
        MenuProps={{
          autoFocus: false,
          sx: { width: "120px" },
          slotProps: {
            paper: {
              sx: {
                maxHeight: "350px",
                overflowY: "auto",
              },
            },
          },
        }}
        multiple={props.multiple ? true : false}
        disabled={props.disabled}
        IconComponent={() => null}
        sx={{ pr: 1 }}
        displayEmpty
        value={props.selectedValues as unknown}
        defaultValue={props.multiple ? [] : ""}
        onChange={(e) => {
          props.onSelectedValuesChange(e.target.value as string[] | string | null);
        }}
        onClose={() => {
          setFocused(false);
          if (props.onClose) {
            props.onClose();
          }
        }}
        onFocus={() => {
          setFocused(true);
          if (props.onFocus) {
            props.onFocus();
          }
        }}
        onBlur={() => setFocused(false)}
        renderValue={() => {
          if (!props.selectedValues && !props.multiple)
            return <Typography variant="body2">{t("select_value")}</Typography>;
          if (props.multiple && Array.isArray(props.selectedValues) && props.selectedValues.length === 0)
            return <Typography variant="body2">{t("select_values")}</Typography>;
          return (
            <>
              {props.selectedValues && (
                <Typography variant="body2" fontWeight="bold">
                  {props.multiple && Array.isArray(props.selectedValues)
                    ? props.selectedValues.filter((v) => !!v).join(", ")
                    : props.selectedValues}
                </Typography>
              )}
            </>
          );
        }}>
        <ListSubheader sx={{ px: 2, pt: 1 }}>
          <TextField
            size="small"
            autoFocus
            placeholder={t("search")}
            value={searchText}
            onChange={(e) => {
              setSearchText(e.target.value);
              debouncedSetSearchText(e.target.value);
            }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            onKeyDown={(e) => {
              if (e.key !== "Escape") {
                e.stopPropagation();
              }
            }}
          />
        </ListSubheader>
        {isLoading && (
          <Box
            sx={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
            }}>
            <Loading size={40} />
          </Box>
        )}
        {!isLoading && data?.items?.length === 0 && <NoValuesFound />}

        {data?.items.map((value) => (
          <MenuItem sx={{ px: 2 }} key={value.value} value={value.value}>
            {props.multiple && Array.isArray(props.selectedValues) && (
              <Checkbox
                sx={{ mr: 2, p: 0 }}
                size="small"
                checked={props.selectedValues ? props.selectedValues.some((v) => v === value.value) : false}
              />
            )}

            <Typography variant="body2" fontWeight="bold">
              {value.value}
            </Typography>
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};

export default SelectorLayerValue;
