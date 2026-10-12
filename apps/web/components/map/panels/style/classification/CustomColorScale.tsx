import type { DragEndEvent } from "@dnd-kit/core";
import { arrayMove } from "@dnd-kit/sortable";
import { Box, Button, Chip, Divider, InputBase, MenuItem, Select, Stack, Tooltip, Typography, useTheme } from "@mui/material";
import React from "react";
import { useTranslation } from "react-i18next";
import { v4 } from "uuid";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import { formatNumber, isValidHex } from "@/lib/utils/helpers";
import type { ClassBreaks, ColorMap } from "@/lib/validations/layer";
import { classBreaks } from "@/lib/validations/layer";

import type { ColorItem, ColorLegends, ColorMapItem, ColorScaleSelectorProps, ValueItem } from "@/types/map/color";

import { OverflowTypograpy } from "@/components/common/OverflowTypography";
import NoDataRow from "@/components/map/panels/style/classification/NoDataRow";
import DropdownFooter from "@/components/map/panels/style/other/DropdownFooter";
import InputTextField from "@/components/map/panels/style/other/InputTextField";
import { LayerValueSelectorPopper } from "@/components/map/panels/style/other/LayerValueSelectorPopper";
import { SingleColorPopper } from "@/components/map/panels/style/other/SingleColorPopper";
import { SortableItem } from "@/components/map/panels/style/other/SortableItem";
import SortableWrapper from "@/components/map/panels/style/other/SortableWrapper";

type CustomColorScaleProps = ColorScaleSelectorProps & {
  setIsClickAwayEnabled: (isClickAwayEnabled: boolean) => void;
  onCancel?: () => void;
  onApply?: (colorMaps: ColorMap, colorLegends?: ColorLegends) => void;
};

const CustomBreaksRowItem = ({
  item,
  index,
  valueMaps,
  minAllowedValue,
  maxAllowedValue,
  onBlur,
}: {
  item: ColorMapItem;
  index: number;
  valueMaps: ColorMapItem[];
  minAllowedValue: number;
  maxAllowedValue: number;
  onBlur?: (newValue: number, index: number) => void;
}) => {
  const { t } = useTranslation("common");
  const [currentValue, setCurrentValue] = React.useState<number | null>(
    item.value?.[0] !== undefined ? Number(item.value[0]) : null
  );

  const [nextValue, setNextValue] = React.useState<number | null>(
    valueMaps[index + 1]?.value?.[0] !== undefined ? Number(valueMaps[index + 1].value?.[0]) : null
  );

  return (
    <Stack direction="row" spacing={0.5} alignItems="center" sx={{ minWidth: 0 }}>
      {item.value?.[0] !== undefined && (
        <>
          {currentValue !== null && (
            <Box sx={{ flex: 1, minWidth: 0, "& input": { width: "100% !important" } }}>
              <InputTextField
                error={currentValue < minAllowedValue || currentValue > maxAllowedValue}
                min={minAllowedValue}
                max={maxAllowedValue}
                value={currentValue}
                outlineInputSx={{ width: "100%" }}
                onChange={(e) => {
                  setCurrentValue(Number(e.target.value));
                }}
                onBlur={() => {
                  onBlur && onBlur(currentValue, index);
                }}
              />
            </Box>
          )}
          <Typography variant="body2" fontWeight="bold">
            –
          </Typography>
          {nextValue !== null && (
            <Box sx={{ flex: 1, minWidth: 0, "& input": { width: "100% !important" } }}>
              <InputTextField
                step={1}
                value={nextValue}
                error={nextValue < minAllowedValue || nextValue > maxAllowedValue}
                min={minAllowedValue}
                max={maxAllowedValue}
                outlineInputSx={{ width: "100%" }}
                onChange={(e) => {
                  setNextValue(Number(e.target.value));
                }}
                onBlur={() => {
                  onBlur && onBlur(nextValue, index + 1);
                }}
              />
            </Box>
          )}
          {index === valueMaps.length - 1 && (
            <Typography variant="body2" fontWeight="bold" noWrap sx={{ pl: 0.5 }}>
              {t("common:more")}
            </Typography>
          )}
        </>
      )}
    </Stack>
  );
};

const CustomOrdinalRowItem = ({
  item,
  editingValues,
  setEditingColorItem,
  handleValueSelector,
}: {
  item: ColorMapItem;
  editingValues: ValueItem | null;
  setEditingColorItem: (item: ColorItem | null) => void;
  handleValueSelector: (e: React.MouseEvent<HTMLElement, MouseEvent>, item: ColorMapItem) => void;
}) => {
  const { t } = useTranslation("common");
  const theme = useTheme();

  return (
    <Stack direction="row" alignItems="center" sx={{ minWidth: 0, overflow: "hidden" }}>
      <OverflowTypograpy
        variant="body2"
        fontWeight="bold"
        onClick={(e) => {
          setEditingColorItem(null);
          e.stopPropagation();
          handleValueSelector(e, item);
        }}
        sx={{
          ...(item.id === editingValues?.id && {
            color: theme.palette.primary.main,
          }),
          transition: theme.transitions.create(["color", "transform"], {
            duration: theme.transitions.duration.standard,
          }),
          "&:hover": {
            cursor: "pointer",
            color: theme.palette.primary.main,
          },
        }}
        tooltipProps={{
          placement: "top",
          arrow: true,
          enterDelay: 200,
        }}>
        <>{item.value?.length ? item.value[0] : t("assign_values")}</>
      </OverflowTypograpy>
      {item?.value?.length && item.value.length > 1 && (
        <Tooltip
          placement="top"
          arrow
          title={
            <div style={{ whiteSpace: "pre-line" }}>
              {item.value.slice(0, 4).join("\n")}
              {item.value.length > 4 && "\n ..."}
            </div>
          }>
          <Chip size="small" sx={{ ml: 2 }} label={`+${item.value.length - 1}`} />
        </Tooltip>
      )}
    </Stack>
  );
};

const CustomColorScale = (props: CustomColorScaleProps) => {
  const theme = useTheme();
  const { colorSet, activeLayerField, activeLayerId } = props;
  const { t } = useTranslation("common");

  // Every style change deep-clones the layer style, so the saved color map
  // arrives as a new array even when nothing in it changed. Keying on its
  // content keeps unsaved row edits across unrelated changes (e.g. No data).
  const savedColorMap = colorSet.selectedColor.color_map;
  const savedColorLegends = colorSet.selectedColor.color_legends;
  const savedColorMapKey = React.useMemo(
    () => JSON.stringify({ colorMap: savedColorMap ?? null, colorLegends: savedColorLegends ?? null }),
    [savedColorMap, savedColorLegends]
  );

  const getValueMaps = React.useCallback(() => {
    const saved = JSON.parse(savedColorMapKey) as {
      colorMap: ColorMap | null;
      colorLegends: ColorLegends | null;
    };
    const colorLegends = saved.colorLegends ?? undefined;
    const valueMaps =
      saved.colorMap?.map((colorMapEntry, index) => {
        const color = colorMapEntry[1] as string;
        const values = colorMapEntry[0] as string[] | null;
        // Look up label by category value first, fall back to color key for backward compat
        const valueKey = values ? values.join(",") : String(index);
        const label = colorLegends?.[valueKey] || colorLegends?.[color] || "";
        return {
          id: v4(),
          value: values,
          color,
          label,
        };
      }) || [];

    // Only sort for custom_breaks (numeric ranges must be ordered);
    // ordinal preserves the user's custom order from color_map
    if (props.selectedColorScaleMethod === "custom_breaks") {
      const sorted = [...valueMaps].sort(
        (a, b) => Number(a.value?.[0] ?? 0) - Number(b.value?.[0] ?? 0)
      );
      return sorted.map((item) => ({ ...item, id: v4() }));
    }
    return valueMaps;
  }, [savedColorMapKey, props.selectedColorScaleMethod]);

  const [valueMaps, setValueMaps] = React.useState<ColorMapItem[]>(getValueMaps());

  // Sync valueMaps when color_map changes from props
  React.useEffect(() => {
    setValueMaps(getValueMaps());
  }, [getValueMaps]);

  const classBreakOptions = React.useMemo(() => {
    return activeLayerField?.type === "number" ? classBreaks.options : [classBreaks.Enum.ordinal];
  }, [activeLayerField]);

  const [editingColorItem, setEditingColorItem] = React.useState<ColorItem | null>(null);
  const [editingValues, setEditingValues] = React.useState<ValueItem | null>(null);
  const [anchorEl, setAnchorEl] = React.useState<HTMLElement | null>(null);

  function onInputHexChange(item: ColorItem) {
    const index = valueMaps.findIndex((color: ColorMapItem) => color.id === item.id);
    if (index !== -1) {
      const newColorMaps = [...valueMaps];
      newColorMaps[index] = {
        ...newColorMaps[index],
        color: item.color,
      };
      setValueMaps(newColorMaps);
    }
  }

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;
    const oldIndex = valueMaps.findIndex((color) => color.id === active.id);
    const newIndex = valueMaps.findIndex((color) => color.id === over?.id);
    const newOrderArray = arrayMove(valueMaps, oldIndex, newIndex);
    if (props.selectedColorScaleMethod === "custom_breaks") {
      sortandSetValueMapsValues(newOrderArray);
    } else {
      setValueMaps(newOrderArray);
    }
  }

  function deleteStep(item: ColorItem) {
    // Breaks need two steps to form an interval; an ordinal map can style a single value.
    const minSteps = props.selectedColorScaleMethod === "custom_breaks" ? 2 : 1;
    if (valueMaps.length <= minSteps) {
      return;
    }
    const index = valueMaps.findIndex((color) => color.id === item.id);
    if (index !== -1) {
      const newColorMaps = [...valueMaps];
      newColorMaps.splice(index, 1);
      if (props.selectedColorScaleMethod === "custom_breaks") {
        sortandSetValueMapsValues(newColorMaps);
      } else {
        setValueMaps(newColorMaps);
      }
    }
  }

  const handleColorPicker = (event: React.MouseEvent<HTMLElement, MouseEvent>, item: ColorItem) => {
    setEditingColorItem(item);
    setAnchorEl(event.currentTarget);
  };

  const handleValueSelector = (event: React.MouseEvent<HTMLElement, MouseEvent>, item: ColorMapItem) => {
    const valueItem = {
      id: item.id,
      values: item.value,
    } as ValueItem;
    setEditingValues(valueItem);
    setAnchorEl(event.currentTarget);
  };

  const handleAddStep = () => {
    const newColorMaps = [...valueMaps];
    const lastColorMap = newColorMaps[newColorMaps.length - 1];
    newColorMaps.push({
      id: v4(),
      value: null,
      color: lastColorMap.color,
    });
    setValueMaps(newColorMaps);
  };

  const handleAddCustomBreak = (item: ColorMapItem, index: number) => {
    const operationIndex = index === valueMaps.length - 2 ? index : index + 1;
    const startValue = Number(valueMaps[operationIndex].value?.[0]);
    const endValue = Number(valueMaps[operationIndex + 1].value?.[0]);
    const difference = (endValue - startValue) / 2;
    const newColorMaps = [...valueMaps];
    newColorMaps.push({
      id: v4(),
      value: [String(startValue + difference)],
      color: item.color,
    });
    sortandSetValueMapsValues(newColorMaps);
  };

  const isValid = React.useMemo(() => {
    let isValid = true;
    valueMaps.forEach((item) => {
      if (!isValidHex(item.color)) {
        isValid = false;
      }
    });
    return isValid;
  }, [valueMaps]);

  const handleValueSelectorChange = (values: string[] | null) => {
    const updatedValues = [] as ColorMapItem[];
    valueMaps.forEach((value) => {
      if (value.id === editingValues?.id) {
        const updatedSelectedValue = {
          ...value,
          value: values,
        };
        updatedValues.push(updatedSelectedValue);
      } else {
        // check if the values are already in other valueMaps (not selected). If yes, remove it
        if (Array.isArray(value.value) && values?.length) {
          const updatedOtherValues = value.value.filter((item) => !values.includes(item));
          updatedValues.push({
            ...value,
            value: updatedOtherValues?.length ? updatedOtherValues : null,
          });
        } else {
          // already null
          updatedValues.push(value);
        }
      }
    });

    setValueMaps(updatedValues);
    editingValues && setEditingValues({ ...editingValues, values });
  };

  function onLabelChange(id: string, label: string) {
    const newColorMaps = valueMaps.map((item) => (item.id === id ? { ...item, label } : item));
    setValueMaps(newColorMaps);
  }

  function onCancel() {
    props.onCancel && props.onCancel();
  }

  function onApply() {
    const colorMaps = [] as ColorMap;
    const colorLegends: ColorLegends = {};
    valueMaps.forEach((item, index) => {
      colorMaps.push([item.value, item.color]);
      if (item.label) {
        // Key by category value (unique per entry) instead of color hex (can collide)
        const key = item.value ? item.value.join(",") : String(index);
        colorLegends[key] = item.label;
      }
    });
    props.onApply && props.onApply(colorMaps, Object.keys(colorLegends).length > 0 ? colorLegends : undefined);
  }

  function sortandSetValueMapsValues(valueMaps: ColorMapItem[]) {
    const sorted = [...valueMaps].sort(
      (a, b) => Number(a.value?.[0] ?? 0) - Number(b.value?.[0] ?? 0)
    );
    setValueMaps(sorted.map((item) => ({ ...item, id: v4() })));
  }

  return (
    <>
      <SingleColorPopper
        editingItem={editingColorItem}
        anchorEl={anchorEl}
        onInputHexChange={onInputHexChange}
        onClose={() => setEditingColorItem(null)}
      />
      {editingValues && props.selectedColorScaleMethod === "ordinal" && (
        <LayerValueSelectorPopper
          open={!!editingValues?.id}
          layerId={activeLayerId}
          selectedValues={editingValues.values}
          fieldName={activeLayerField?.name || ""}
          anchorEl={anchorEl}
          onSelectedValuesChange={handleValueSelectorChange}
          onDone={() => setEditingValues(null)}
        />
      )}
      <Box
        sx={{ py: 3, flex: 1, minHeight: 0, display: "flex", flexDirection: "column", overflow: "hidden" }}
        onClick={() => {
          setEditingValues(null);
          setEditingColorItem(null);
        }}>
        <Box sx={{ px: 3, pb: 3 }}>
          <Select
            fullWidth
            size="small"
            IconComponent={() => null}
            value={props.selectedColorScaleMethod}
            onOpen={() => {
              props.setIsClickAwayEnabled && props.setIsClickAwayEnabled(false);
            }}
            MenuProps={{
              TransitionProps: {
                onExited: () => {
                  props.setIsClickAwayEnabled && props.setIsClickAwayEnabled(true);
                },
              },
            }}
            onChange={(e) => {
              props.setSelectedColorScaleMethod(e.target.value as ClassBreaks);
            }}>
            {classBreakOptions.map((option, index) => (
              <MenuItem key={index} value={String(option)}>
                {t(`${option}`)}
              </MenuItem>
            ))}
          </Select>
          {props.selectedColorScaleMethod === "custom_breaks" && (
            <Stack direction="row" justifyContent="space-between" alignItems="center" pt={2}>
              <Typography variant="caption">
                Min: <b>{props.classBreaksValues?.min ? formatNumber(props.classBreaksValues.min) : ""}</b>
              </Typography>
              <Typography variant="caption">
                Max: <b>{props.classBreaksValues.max ? formatNumber(props.classBreaksValues?.max) : ""}</b>
              </Typography>
            </Stack>
          )}
        </Box>

        <Box sx={{ flex: 1, minHeight: 0, overflowY: "auto", overscrollBehavior: "contain" }}>
          <SortableWrapper handleDragEnd={handleDragEnd} items={valueMaps}>
            {valueMaps?.map((item: ColorMapItem, index: number) => (
              <SortableItem
                active={item.id === editingColorItem?.id || item.id === editingValues?.id}
                key={item.id}
                item={item}
                label={item.color}
                picker={
                  <Box
                    onClick={(e) => {
                      setEditingValues(null);
                      e.stopPropagation();
                      const colorItem = {
                        id: item.id,
                        color: item.color,
                      } as ColorItem;
                      handleColorPicker(e, colorItem);
                    }}
                    sx={{
                      height: "28px",
                      width: "32px",
                      minWidth: "32px",
                      borderRadius: "4px",
                      backgroundColor: item.color,
                      "&:hover": {
                        cursor: "pointer",
                      },
                    }}
                  />
                }
                actions={
                  <>
                    {props.selectedColorScaleMethod === "custom_breaks" && index < valueMaps.length - 1 && (
                      <Icon
                        sx={{
                          transition: theme.transitions.create(["color", "transform"], {
                            duration: theme.transitions.duration.standard,
                          }),
                          "&:hover": {
                            cursor: "pointer",
                            color: theme.palette.primary.main,
                          },
                        }}
                        onClick={() => {
                          handleAddCustomBreak(item, index);
                        }}
                        iconName={ICON_NAME.PLUS}
                        style={{
                          fontSize: 13,
                        }}
                        htmlColor="inherit"
                      />
                    )}
                    {((index < valueMaps.length - 1 && props.selectedColorScaleMethod === "custom_breaks") ||
                      props.selectedColorScaleMethod === "ordinal") && (
                      <Icon
                        sx={{
                          transition: theme.transitions.create(["color", "transform"], {
                            duration: theme.transitions.duration.standard,
                          }),
                          "&:hover": {
                            cursor: "pointer",
                            color: theme.palette.error.main,
                          },
                        }}
                        onClick={() => deleteStep(item)}
                        iconName={ICON_NAME.TRASH}
                        style={{
                          fontSize: 12,
                        }}
                        htmlColor="inherit"
                      />
                    )}
                  </>
                }
                subtitle={
                  <InputBase
                    value={item.label || ""}
                    placeholder={t("legend_label")}
                    onClick={(e) => e.stopPropagation()}
                    onChange={(e) => onLabelChange(item.id, e.target.value)}
                    sx={{
                      fontSize: 11,
                      color: "text.secondary",
                      "& .MuiInputBase-input": {
                        p: 0,
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        "&::placeholder": {
                          opacity: 0.5,
                          fontStyle: "italic",
                        },
                      },
                    }}
                  />
                }>
                  {props.selectedColorScaleMethod === "ordinal" && (
                    <CustomOrdinalRowItem
                      item={item}
                      editingValues={editingValues}
                      setEditingColorItem={setEditingColorItem}
                      handleValueSelector={handleValueSelector}
                    />
                  )}
                  {props.selectedColorScaleMethod === "custom_breaks" && (
                    <CustomBreaksRowItem
                      item={item}
                      index={index}
                      valueMaps={valueMaps}
                      minAllowedValue={props.classBreaksValues.min}
                      maxAllowedValue={props.classBreaksValues.max}
                      onBlur={(newValue, index) => {
                        const newColorMaps = [...valueMaps];
                        newColorMaps[index] = {
                          ...newColorMaps[index],
                          value: [newValue.toString()],
                        };
                        sortandSetValueMapsValues(newColorMaps);
                      }}
                    />
                  )}
              </SortableItem>
            ))}
          </SortableWrapper>
          {props.selectedColorScaleMethod === "ordinal" && (
            <Button
              onClick={handleAddStep}
              variant="text"
              sx={{ borderRadius: 0, ml: 4, mt: 2 }}
              size="small"
              startIcon={<Icon iconName={ICON_NAME.PLUS} style={{ fontSize: "15px" }} />}>
              <Typography variant="body2" fontWeight="bold" color="inherit">
                {t("common:add_step")}
              </Typography>
            </Button>
          )}
          {/* No data color */}
          <Divider sx={{ my: 1, mx: 4, borderStyle: "dashed" }} />
          <Box sx={{ pl: 4, pr: 3 }}>
            <NoDataRow
              noDataColor={props.noDataColor}
              onNoDataColorChange={props.onNoDataColorChange}
              setIsClickAwayEnabled={props.setIsClickAwayEnabled}
            />
          </Box>
        </Box>
        <Box sx={{ mt: 4 }}>
          <DropdownFooter isValid={isValid} onCancel={onCancel} onApply={onApply} />
        </Box>
      </Box>
    </>
  );
};

export default CustomColorScale;
