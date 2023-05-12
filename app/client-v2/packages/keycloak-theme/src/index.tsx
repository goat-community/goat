import { createPageStory as createPageStoryLogin } from "login/createPageStory";
import { StrictMode, lazy, Suspense } from "react";
import React from "react";
import { createRoot } from "react-dom/client";

import { kcContext as kcLoginThemeContext } from "./login/kcContext";

const KcLoginThemeApp = lazy(() => import("./login/KcApp"));
const { PageStory } = createPageStoryLogin({
  pageId: "login.ftl",
});

// eslint-disable-next-line @typescript-eslint/no-non-null-assertion
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <Suspense>
      {(() => {
        if (kcLoginThemeContext !== undefined) {
          return <KcLoginThemeApp kcContext={kcLoginThemeContext} />;
        }
        return <PageStory />;
      })()}
    </Suspense>
  </StrictMode>
);
