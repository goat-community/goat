import { filterUsingQuery } from "@/lib/services/filtering";
import type { ComparerMode } from "@/types/map/filtering";
import React, { useState } from "react";

// import useSWR from "swr";
import { FILTERING } from "../../../../lib/api/apiConstants";
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
} from "../../../../lib/utils/filtering_cql";
import {
  NumberOption, // DateOption,
  // SelectOption,
  TextOption,
} from "./FilterOption";

interface FilterResultProps {
  comparer: ComparerMode | null;
  prop: string;
  layer_id: string;
}

const FilterOptionField = (props: FilterResultProps) => {
  const { comparer, prop, layer_id } = props;
  const [firstInput, setFirstInput] = useState<string | number>("");

  // use it when we remove the button that we currently have
  // const { data, error } = useSWR(FILTERING, url => filterUsingQuery(query, layer_id, url));

  const handleFilter = () => {
    if (!comparer) return;

    let query;
    switch (comparer.value) {
      case "is":
        query = is(prop, firstInput);
        break;
      case "is_not":
        query = is_not(prop, firstInput);
        break;
      case "includes":
      case "excludes":
        query = excludes(prop, ["playground", "bus_stop"]);
        break;
      case "starts_with":
        query = starts_with(prop, "bu");
        break;
      case "ends_with":
        query = ends_with(prop, "bu");
        break;
      case "contains_the_text":
        query = contains_the_text(prop, "bu");
        break;
      case "does_not_contains_the_text":
        query = does_not_contains_the_text(prop, "bu");
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
        query = is_at_least(prop, 10);
        break;
      case "is_at_most":
        query = is_at_most(prop, 20);
        break;
      case "is_less_than":
        query = is_less_than(prop, 20);
        break;
      case "is_greater_than":
        query = is_greater_than(prop, 70);
        break;
      case "is_between":
        query = is_between(prop); //10, 20
        break;
      default:
        return;
    }

    filterUsingQuery(query, layer_id, FILTERING).then((data) => console.log(data));
  };

  if (!comparer) return null;

  let inputComponent: React.ReactNode | null = null;

  switch (comparer.value) {
    case "is":
    case "is_not":
      inputComponent =
        comparer.type === "number" ? (
          <NumberOption value={firstInput} setChange={setFirstInput} />
        ) : (
          <TextOption value={firstInput} setChange={setFirstInput} />
        );
      break;
    // Add more cases here as needed
    default:
      inputComponent = null;
      break;
  }

  return (
    <div>
      {inputComponent}
      <button onClick={handleFilter}>Filter</button>
    </div>
  );
};

export default FilterOptionField;
