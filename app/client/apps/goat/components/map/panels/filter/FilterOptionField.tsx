import type { ComparerMode } from "@/types/map/filtering";
import React, { useState, useEffect, useCallback } from "react";
import { useDispatch } from "react-redux";
import { addFilter } from "@/lib/store/mapFilters/slice";
import {
  is,
  is_not, // includes,
  excludes,
  starts_with,
  ends_with,
  contains_the_text,
  does_not_contains_the_text,
  is_blank,
  is_not_blank,
  is_empty_string,
  is_not_empty_string,
  is_at_least,
  is_at_most,
  is_less_than,
  is_greater_than,
  is_between,
} from "@/lib/utils/filtering_cql";
import { NumberOption, TextOption } from "./FilterOption";
import { debounce } from "@mui/material/utils";

interface FilterResultProps {
  comparer: ComparerMode | null;
  prop: string;
  expression: string;
}

const FilterOptionField = (props: FilterResultProps) => {
  const { comparer, prop, expression } = props;
  const [firstInput, setFirstInput] = useState<string>("");
  const [secondInput, setSecondInput] = useState<string>("");

  const dispatch = useDispatch();

  const handleFilter = useCallback(
    (value: string, value2?: string) => {
      if (!comparer) return;
      let query;
      if (value) {
        switch (comparer.value) {
          case "is":
            query = is(
              prop,
              comparer.type === "number" ? parseInt(value) : value,
            );
            break;
          case "is_not":
            query = is_not(prop, value);
            break;
          case "includes":
          case "excludes":
            query = excludes(prop, ["playground", "bus_stop"]);
            break;
          case "starts_with":
            if (typeof value === "string") {
              query = starts_with(prop, value);
            }
            break;
          case "ends_with":
            if (typeof value === "string") {
              query = ends_with(prop, value);
            }
            break;
          case "contains_the_text":
            if (typeof value === "string") {
              query = contains_the_text(prop, value);
            }
            break;
          case "does_not_contains_the_text":
            if (typeof value === "string") {
              query = does_not_contains_the_text(prop, value);
            }
            break;
          case "is_blank":
            query = is_blank(prop);
            break;
          case "is_not_blank":
            query = is_not_blank(prop);
            break;
          case "is_empty_string":
            query = is_empty_string(prop);
            break;
          case "is_not_empty_string":
            query = is_not_empty_string(prop);
            break;
          case "is_at_least":
            query = is_at_least(prop, parseInt(value));
            break;
          case "is_at_most":
            query = is_at_most(prop, parseInt(value));
            break;
          case "is_less_than":
            query = is_less_than(prop, parseInt(value));
            break;
          case "is_greater_than":
            query = is_greater_than(prop, parseInt(value));
            break;
          case "is_between":
            query = is_between(
              prop,
              parseInt(value),
              parseInt(value2 ? value2 : "0"),
            );
            break;
          default:
            return;
        }
      } else {
        query = "";
      }

      dispatch(addFilter({ query, expression }));
    },
    [comparer, dispatch, expression, prop],
  );

  const sendQuery = React.useMemo(
    () =>
      debounce((request: { input: string; input2?: string }) => {
        if (
          request.input ||
          (comparer &&
            [
              "is_blank",
              "is_not_blank",
              "is_empty_string",
              "is_not_empty_string",
            ].includes(comparer.value))
        ) {
          setFirstInput(request.input);
          if (request.input2) {
            setSecondInput(request.input2);
          }

          handleFilter(request.input, request.input2);
        } else {
          handleFilter("");
        }
      }, 1000),
    [comparer, handleFilter],
  );

  useEffect(() => {
    if (secondInput) {
      sendQuery({ input: firstInput, input2: secondInput });
    } else {
      sendQuery({ input: firstInput });
    }
  }, [firstInput, secondInput, sendQuery, comparer]);

  function handleInputChange(newValue: string) {
    setFirstInput(newValue);
  }

  function handleSecondInputChange(newValue: string) {
    setSecondInput(newValue);
  }

  if (!comparer) return null;

  let inputComponent: React.ReactNode | null = null;

  switch (comparer.value) {
    case "is":
    case "is_not":
      inputComponent =
        comparer.type === "number" ? (
          <>
            <NumberOption value={firstInput} setChange={handleInputChange} />
          </>
        ) : (
          <TextOption value={firstInput} setChange={handleInputChange} />
        );
      break;
    case "includes":
      break;
    case "excludes":
      break;
    case "starts_with":
      inputComponent = (
        <TextOption value={firstInput} setChange={handleInputChange} />
      );
      break;
    case "ends_with":
      inputComponent = (
        <TextOption value={firstInput} setChange={handleInputChange} />
      );
      break;
    case "contains_the_text":
      inputComponent = (
        <TextOption value={firstInput} setChange={handleInputChange} />
      );
      break;
    case "does_not_contains_the_text":
      inputComponent = (
        <TextOption value={firstInput} setChange={handleInputChange} />
      );
      break;
    case "is_blank":
    case "is_not_blank":
    case "is_empty_string":
    case "is_not_empty_string":
      break;
    case "is_at_least":
      inputComponent = (
        <NumberOption value={firstInput} setChange={handleInputChange} />
      );
      break;
    case "is_at_most":
      inputComponent = (
        <NumberOption value={firstInput} setChange={handleInputChange} />
      );
      break;
    case "is_less_than":
      inputComponent = (
        <NumberOption value={firstInput} setChange={handleInputChange} />
      );
      break;
    case "is_greater_than":
      inputComponent = (
        <NumberOption value={firstInput} setChange={handleInputChange} />
      );
      break;
    case "is_between":
      inputComponent = (
        <>
          <NumberOption value={firstInput} setChange={handleInputChange} />
          <NumberOption
            value={secondInput}
            setChange={handleSecondInputChange}
          />
        </>
      );
      break;
    default:
      inputComponent = null;
      break;
  }

  return <div>{inputComponent}</div>;
};

export default FilterOptionField;
