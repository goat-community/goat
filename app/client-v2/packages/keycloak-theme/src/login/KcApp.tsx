import Fallback, { type PageProps } from "keycloakify/login";
import { lazy, Suspense } from "react";
import React from "react";

import "./KcApp.css";
import { useI18n } from "./i18n";
import type { KcContext } from "./kcContext";

const Template = lazy(() => import("./Template"));

// You can uncomment this to see the values passed by the main app before redirecting.
//import { foo, bar } from "./valuesTransferredOverUrl";
//console.log(`Values passed by the main app in the URL parameter:`, { foo, bar });

const Login = lazy(() => import("./pages/Login"));

// This is like adding classes to theme.properties
// https://github.com/keycloak/keycloak/blob/11.0.3/themes/src/main/resources/theme/keycloak/login/theme.properties
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const classes: PageProps<any, any>["classes"] = {
  // NOTE: The classes are defined in ./KcApp.css
  kcHtmlClass: "my-root-class",
  kcHeaderWrapperClass: "my-color my-font",
};

export default function KcApp(props: { kcContext: KcContext }) {
  const { kcContext } = props;

  const i18n = useI18n({ kcContext });

  if (i18n === null) {
    //NOTE: Text resources for the current language are still being downloaded, we can't display anything yet.
    //We could display a loading progress but it's usually a matter of milliseconds.
    return null;
  }

  /*
   * Examples assuming i18n.currentLanguageTag === "en":
   * i18n.msg("access-denied") === <span>Access denied</span>
   * i18n.msg("foo") === <span>foo in English</span>
   */

  return (
    <Suspense>
      {(() => {
        switch (kcContext.pageId) {
          case "login.ftl":
            return <Login {...{ kcContext, i18n, Template, classes }} doUseDefaultCss={true} />;
          default:
            return <Fallback {...{ kcContext, i18n, classes }} Template={Template} doUseDefaultCss={true} />;
        }
      })()}
    </Suspense>
  );
}
