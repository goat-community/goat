import type { ComparerMode } from "@/types/map/filtering";

export const comparerModes: { number: ComparerMode[]; date: ComparerMode[]; text: ComparerMode[] } = {
  number: [
    // Number Comparers
    {
      label: "is",
      value: "is",
      type: "number",
      select: true,
    },
    {
      label: "is not",
      value: "is_not",
      type: "number",
      select: true,
    },
    {
      label: "includes",
      value: "includes",
      type: "select",
      select: true,
    },
    {
      label: "excludes",
      value: "excludes",
      type: "select",
      select: true,
    },
    {
      label: "is at least",
      value: "is_at_least",
      type: "number",
      select: true,
    },
    {
      label: "is less than",
      value: "is_less_than",
      type: "number",
      select: true,
    },
    {
      label: "is at most",
      value: "is_at_most",
      type: "number",
      select: true,
    },
    {
      label: "is greater than",
      value: "is_greater_than",
      type: "number",
      select: true,
    },
    {
      label: "is between",
      value: "is_between",
      type: "dual_number",
      select: true,
    },
    // we can enable them when the problem is solved
    // {
    //   label: "is blank",
    //   value: "is_blank",
    //   type: "none",
    //   select: false,
    // },
    // {
    //   label: "is not blank",
    //   value: "is_not_blank",
    //   type: "none",
    //   select: false,
    // },
  ],
  date: [
    // Date Comparers
    {
      label: "is on",
      value: "is_on",
      type: "date",
      select: true,
    },
    {
      label: "is not on",
      value: "is_not_on",
      type: "date",
      select: true,
    },
    {
      label: "is before",
      value: "is_before",
      type: "date",
      select: true,
    },
    {
      label: "is after",
      value: "is_after",
      type: "date",
      select: true,
    },
    {
      label: "in the last",
      value: "in_the_last",
      type: "year_filter",
      select: false,
    },
    {
      label: "not in the last",
      value: "not_in_the_last",
      type: "year_filter",
      select: false,
    },
    {
      label: "is between",
      value: "is_between",
      type: "dualDate",
      select: false,
    },
    {
      label: "is not between",
      value: "is_not_between",
      type: "dualDate",
      select: false,
    },
    // we can enable them when the problem is solved
    // {
    //   label: "is blank",
    //   value: "is_blank",
    //   type: "none",
    //   select: false,
    // },
    // {
    //   label: "is not blank",
    //   value: "is_not_blank",
    //   type: "none",
    //   select: false,
    // },
  ],
  text: [
    // Text Comparers
    {
      label: "is",
      value: "is",
      type: "text",
      select: true,
    },
    {
      label: "is not",
      value: "is_not",
      type: "text",
      select: true,
    },
    {
      label: "includes",
      value: "includes",
      type: "select",
      select: true,
    },
    {
      label: "excludes",
      value: "excludes",
      type: "select",
      select: true,
    },
    {
      label: "starts with",
      value: "starts_with",
      type: "text",
      select: false,
    },
    {
      label: "ends with",
      value: "ends_with",
      type: "text",
      select: false,
    },
    {
      label: "contains the text",
      value: "contains_the_text",
      type: "text",
      select: false,
    },
    {
      label: "doesn't contains the text",
      value: "does_not_contains_the_text",
      type: "text",
      select: false,
    },
    // we can enable them when the problem is solved

    // {
    //   label: "is blank",
    //   value: "is_blank",
    //   type: "none",
    //   select: false,
    // },
    // {
    //   label: "is not blank",
    //   value: "is_not_blank",
    //   type: "none",
    //   select: false,
    // },
    {
      label: "is empty string",
      value: "is_empty_string",
      type: "none",
      select: false,
    },
    {
      label: "is not empty string",
      value: "is_not_empty_string",
      type: "none",
      select: false,
    },
  ],
};
