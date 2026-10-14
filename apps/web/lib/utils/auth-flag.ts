import { publicEnv } from "@/lib/utils/public-env";

/**
 * Values that turn authentication off, matching pydantic's bool parsing so the
 * frontend and the Python services can never disagree on the same AUTH value.
 */
const FALSY_AUTH_VALUES = new Set(["false", "0", "off", "f", "no", "n"]);

/**
 * Whether the AUTH flag explicitly disables authentication.
 *
 * Accepts the raw value of `AUTH` (server runtime) or `NEXT_PUBLIC_AUTH`
 * (inlined into the client bundle). Unset, empty, unrecognized values and the
 * unsubstituted Docker placeholder all keep auth enabled — auth only turns off
 * on an explicit falsy value. The placeholder is recognized by its prefix
 * (`publicEnv`): the Docker entrypoint rewrites every full placeholder name in
 * the bundle, so a comparison with the full name would be rewritten to the
 * value it is meant to tell apart.
 */
export const isAuthDisabled = (rawAuth: string | undefined): boolean => {
  const value = publicEnv(rawAuth);
  if (!value) return false;
  return FALSY_AUTH_VALUES.has(value.toLowerCase());
};
