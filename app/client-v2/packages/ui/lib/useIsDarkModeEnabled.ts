// Copyright (c) 2020 GitHub user u/garronej
import type { StatefulEvt } from "evt";
import { statefulObservableToStatefulEvt } from "powerhooks/tools/StatefulObservable/statefulObservableToStatefulEvt";
import { updateSearchBarUrl, retrieveParamFromUrl } from "powerhooks/tools/urlSearchParams";
import { createUseGlobalState } from "powerhooks/useGlobalState";

const { useIsDarkModeEnabled, $isDarkModeEnabled } = createUseGlobalState({
  name: "isDarkModeEnabled",
  initialState: window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches,
  doPersistAcrossReloads: true,
});

export { useIsDarkModeEnabled };

export const evtIsDarkModeEnabled: StatefulEvt<boolean> = statefulObservableToStatefulEvt({
  statefulObservable: $isDarkModeEnabled,
});

(() => {
  const result = retrieveParamFromUrl({
    url: window.location.href,
    name: "theme",
  });

  if (!result.wasPresent) {
    return;
  }

  updateSearchBarUrl(result.newUrl);

  const isDarkModeEnabled = (() => {
    switch (result.value) {
      case "dark":
        return true;
      case "light":
        return false;
      default:
        return undefined;
    }
  })();

  if (isDarkModeEnabled === undefined) {
    return;
  }

  evtIsDarkModeEnabled.state = isDarkModeEnabled;
})();

evtIsDarkModeEnabled.attach((isDarkModeEnabled) => {
  const id = "root-color-scheme";

  remove_existing_element: {
    const element = document.getElementById(id);

    if (element === null) {
      break remove_existing_element;
    }

    element.remove();
  }

  const element = document.createElement("style");

  element.id = id;

  element.innerHTML = `
				:root {
					color-scheme: ${isDarkModeEnabled ? "dark" : "light"}
				}
		`;

  document.getElementsByTagName("head")[0].appendChild(element);
});
