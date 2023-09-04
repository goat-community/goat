// general queries

function createComparisonCondition(op: string, key: string, value: string | number) {
  return `{"op":"${op}","args":[{"property":"${key}"},${typeof value === "string" ? `"${value}"` : value}]}`;
}

function createInclusionCondition(op: string, key: string, values: (string | number)[]) {
  return `{"op":"${op}","args":[{"property":"${key}"},${JSON.stringify(values)}]}`;
}

function createNestedCondition(outerOp: string, key: string, value: string, innerOp?: string) {
  return `{"op": "${outerOp}","args": [
      ${
        innerOp
          ? `{"op":"${innerOp}","args":[{"property":"${key}"},"${value}"]}`
          : `{ "property":"${key}"},
      "${value}"`
      }]}`;
}

// all the queries

export function is(key: string, value: string | number) {
  return createComparisonCondition("=", key, value);
}

export function is_not(key: string, value: string | number) {
  return createComparisonCondition("!=", key, value);
}

export function includes(key: string, values: (string | number)[]) {
  return createInclusionCondition("in", key, values);
}

export function excludes(key: string, values: (string | number)[]) {
  return createInclusionCondition("not", key, values);
}

export function starts_with(key: string, value: string) {
  return createNestedCondition("like", key, `${value}%`);
}

export function ends_with(key: string, value: string) {
  return createNestedCondition("like", key, `%${value}`);
}

export function contains_the_text(key: string, value: string) {
  return createNestedCondition("like", key, `%${value}%`);
}

export function does_not_contains_the_text(key: string, value: string) {
  return createNestedCondition("not", key, `%${value}%`, "like");
}

export function is_blank(key: string) {
  return `{
    "op": "isNull",
    "args": [
      { "property": "${key}" }
    ]
  }`;
}

export function is_not_blank(key: string) {
  return `{
    "op": "not",
    "args": [
      {
        "op": "isNull",
        "args": [
          { "property": "${key}" }
        ]
      }
    ]
  }`;
}

export function is_empty_string(key: string) {
  return createComparisonCondition("=", key, "");
}

export function is_not_empty_string(key: string) {
  return createComparisonCondition("!=", key, "");
}

export function is_at_least(key: string, value: number) {
  return createComparisonCondition(">=", key, value);
}

export function is_at_most(key: string, value: number) {
  return createComparisonCondition("<=", key, value);
}

export function is_less_than(key: string, value: number) {
  return createComparisonCondition("<", key, value);
}

export function is_greater_than(key: string, value: number) {
  return createComparisonCondition(">", key, value);
}

export function is_between(key: string, value1: number, value2: number) {
  // other props (valueA: number, valueB: number)
  return `{"op":"and","args":[{"op":">=","args":[{"property":"${key}"},${value1}]},{"op":"<=","args":[{"property":"${key}"},${value2}]}]}`;
}

export function and_operator(args: string[]) {
  return `{"op":"and","args": [${args.map((arg) => `${arg}`)}]}`;
}

export function or_operator(args: string[]) {
  return `{"op":"or","args": [${args.map((arg) => `${arg}`)}]}`;
}
