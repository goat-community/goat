/**
 * Reads a value of the login theme's theme.properties (package.json
 * "keycloakify.extraThemeProperties"). Keycloak resolves `${env.NAME:default}`
 * placeholders when it loads the theme and hands the properties to every page
 * as `kcContext.properties`, which keycloakify v8 leaves untyped. Blank values
 * count as unset.
 */
export function getThemeProperty(kcContext: object, name: string): string | undefined {
  const { properties } = kcContext as { properties?: Record<string, string | undefined> };
  const value = properties?.[name]?.trim();
  return value ? value : undefined;
}
