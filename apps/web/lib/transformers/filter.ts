import { v4 } from "uuid";

import { type Expression, FilterType } from "@/lib/validations/filter";

export const comparisonAndInclussionOpperators = {
  is: "=",
  is_not: "!=",
  includes: "in",
  excludes: "not",
  is_at_least: ">=",
  is_at_most: "<=",
  is_less_than: "<",
  is_greater_than: ">",
  is_empty_string: "=",
  is_not_empty_string: "!=",
};

function createComparisonCondition(op: string, key: string, value: string | number) {
  return `{"op":"${op}","args":[{"property":"${key}"},${typeof value === "string" ? `"${value}"` : value}]}`;
}

function createNestedCondition(outerOp: string, key: string, value: string, innerOp?: string) {
  return `{"op": "${outerOp}","args": [
      ${innerOp
      ? `{"op":"${innerOp}","args":[{"property":"${key}"},"${value}"]}`
      : `{ "property":"${key}"},
      "${value}"`
    }]}`;
}

export function is(key: string, value: string | number) {
  return createComparisonCondition("=", key, value);
}

export function is_not(key: string, value: string | number) {
  return createComparisonCondition("!=", key, value);
}

export function includes(key: string, values: (string | number)[]) {
  const args = typeof values === "string" ? [] : values.map((value) => is(key, value));
  return or_operator(args);
}

export function excludes(key: string, values: (string | number)[]) {
  const args = typeof values === "string" ? [] : values.map((value) => is_not(key, value));
  return and_operator(args);
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
    "args": { "property": "${key}" }
  }`;
}

export function is_not_blank(key: string) {
  return `{
    "op": "not",
    "args": [
      {
        "op": "isNull",
        "args": { "property": "${key}" }
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
  return `{"op":"and","args":[{"op":">=","args":[{"property":"${key}"},${value1}]},{"op":"<=","args":[{"property":"${key}"},${value2}]}]}`;
}

export function s_intersects(geom: string, geomProperty: string = "geom") {
  return `{"op":"s_intersects","args":[{"property":"${geomProperty}"},${geom}]}`;
}

export function and_operator(args: string[]) {
  return `{"op":"and","args": [${args.map((arg) => `${arg}`)}]}`;
}

export function or_operator(args: string[]) {
  return `{"op":"or","args": [${args.map((arg) => `${arg}`)}]}`;
}


export function createTheCQLBasedOnExpression(
  expressions,
  layerFields: { name: string; type: string }[],
  logicalOperator?: "and" | "or"
) {
  const queries = expressions
    .filter((exp) => exp.expression && exp.attribute)
    .map((expression) => {
      const attributeType = layerFields.filter((field) => field.name === expression.attribute).length
        ? layerFields.filter((field) => field.name === expression.attribute)[0].type
        : undefined;

      switch (expression.expression) {
        case "is":
          return is(expression.attribute, expression.value);
        case "is_not":
          return is_not(expression.attribute, expression.value);
        case "is_empty_string":
          return is_empty_string(expression.attribute);
        case "is_not_empty_string":
          return is_not_empty_string(expression.attribute);
        case "is_at_least":
          return is_at_least(expression.attribute, expression.value);
        case "is_less_than":
          return is_less_than(expression.attribute, expression.value);
        case "is_greater_than":
          return is_greater_than(expression.attribute, expression.value);
        case "is_at_most":
          return is_at_most(expression.attribute, expression.value);
        case "includes":
          if (attributeType === "string") {
            return includes(expression.attribute, expression.value);
          } else {
            return includes(expression.attribute, expression.value.map(Number));
          }
        case "excludes":
          if (attributeType === "string") {
            return excludes(expression.attribute, expression.value);
          } else {
            return excludes(expression.attribute, expression.value.map(Number));
          }
        case "is_blank":
          return is_blank(expression.attribute);
        case "is_not_blank":
          return is_not_blank(expression.attribute);
        case "starts_with":
          return starts_with(expression.attribute, expression.value);
        case "ends_with":
          return ends_with(expression.attribute, expression.value);
        case "contains_the_text":
          return contains_the_text(expression.attribute, expression.value);
        case "does_not_contains_the_text":
          return does_not_contains_the_text(expression.attribute, expression.value);
        case "is_between":
          return is_between(
            expression.attribute,
            parseInt(expression.value.split("-")[0]),
            parseInt(expression.value.split("-")[1])
          );
        case "s_intersects":
          return s_intersects(expression.value, expression.attribute);
      }
    });

  if (logicalOperator === "and") {
    return JSON.parse(and_operator(queries));
  } else {
    return JSON.parse(or_operator(queries));
  }
}

function toExpressionObject(expressionsInsideLogicalOperator): Expression[] {
  return expressionsInsideLogicalOperator.map((expressionToBeProcessed) => {
    const expression: Expression = {
      expression: "",
      attribute: "",
      value: "",
      id: v4(),
      type: FilterType.Logical,
    };

    const value = expressionToBeProcessed.args.length > 0 ? expressionToBeProcessed.args[1] : "";

    if (expressionToBeProcessed.op === "like") {
      switch (true) {
        case value.startsWith("%") && value.endsWith("%"):
          expression.expression = "contains_the_text";
          break;
        case value.endsWith("%"):
          expression.expression = "starts_with";
          break;
        case value.startsWith("%"):
          expression.expression = "ends_with";
          break;
        default:
          expression.expression = "does_not_contains_the_text";
          break;
      }
      expression.attribute = expressionToBeProcessed.args[0].property;
      expression.value = value.replace(/%/g, "");
    } else if (expressionToBeProcessed.op === "isNull") {
      expression.expression = "is_blank";
      expression.attribute = expressionToBeProcessed.args?.property;
    } else if (expressionToBeProcessed.op === "not" && expressionToBeProcessed.args[0].op === "isNull") {
      expression.expression = "is_not_blank";
      expression.attribute = expressionToBeProcessed.args[0].args.property;
    } else if (expressionToBeProcessed.op === "=" && value === "") {
      expression.expression = "is_empty_string";
      expression.attribute = expressionToBeProcessed.args[0].property;
    } else if (expressionToBeProcessed.op === "!=" && value === "") {
      expression.expression = "is_not_empty_string";
      expression.attribute = expressionToBeProcessed.args[0].property;
    } else if (["and", "or"].includes(expressionToBeProcessed.op)) {
      switch (expressionToBeProcessed.op) {
        case "and":
          expression.expression = "excludes";
        case "or":
          expression.expression = "includes";
      }
      expression.attribute = expressionToBeProcessed.args[0].args[0].property;
      expression.value = expressionToBeProcessed.args.map((arg) => arg.args[1]);
    } else if (expressionToBeProcessed.op === "s_intersects") {
      expression.expression = "s_intersects";
      expression.attribute = expressionToBeProcessed.args[0].property;
      expression.value = JSON.stringify(expressionToBeProcessed.args[1]);
    } else {
      expression.expression = Object.keys(comparisonAndInclussionOpperators).filter(
        (comp) => comparisonAndInclussionOpperators[comp] === expressionToBeProcessed.op
      )[0];
      expression.attribute = expressionToBeProcessed.args[0].property;
      expression.value = value;
    }

    if (expressionToBeProcessed.op === "s_intersects") {
      expression.type = FilterType.Spatial;
    } else {
      expression.type = FilterType.Logical;
    }

    return expression;
  });
}

export function parseCQLQueryToObject(condition?: { op: string; args: unknown[] }) {
  if (condition && Object.keys(condition).length) {
    let expressions: Expression[] = [];
    const expressionsInsideLogicalOperator = condition.args;
    expressions = toExpressionObject(expressionsInsideLogicalOperator);

    return expressions;
  }

  return [];
}
