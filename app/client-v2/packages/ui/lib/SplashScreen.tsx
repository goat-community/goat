// Copyright (c) 2020 GitHub user u/garronej
import Color from "color";
import { Evt } from "evt";
import { useRerenderOnStateChange } from "evt/hooks";
import { useViewPortState } from "powerhooks/ViewPortAdapter";
import { statefulObservableToStatefulEvt } from "powerhooks/tools/StatefulObservable/statefulObservableToStatefulEvt";
import { useConst } from "powerhooks/useConst";
import { useConstCallback } from "powerhooks/useConstCallback";
import { createUseGlobalState } from "powerhooks/useGlobalState";
import { useGuaranteedMemo } from "powerhooks/useGuaranteedMemo";
import { useState, useEffect, useRef, useContext, createContext, memo } from "react";
import type { ReactNode } from "react";
import React from "react";
import * as runExclusive from "run-exclusive";
import { id } from "tsafe/id";
import { createMakeStyles, keyframes } from "tss-react";

import { GOATLogoSvg } from "../assets/svg/GOATLogo";
import type { ReactComponent } from "../tools/ReactComponent";
import type { Theme } from "./ThemeProvider";

let fadeOutDuration = 700;
let minimumDisplayDuration = 1000;

const { useSplashScreen, useSplashScreenStatus } = (() => {
  const evtDisplayState = Evt.create({
    count: 1,
    isTransparencyEnabled: false,
    prevTime: 0,
    onHiddens: id<(() => void)[]>([]),
  });

  const { globalHideSplashScreen } = (() => {
    const { getDoUseDelay } = (() => {
      const { $lastDelayedTime } = createUseGlobalState({
        name: "lastDelayedTime",
        initialState: 0,
        doPersistAcrossReloads: true,
      });

      const evtLastDelayedTime = statefulObservableToStatefulEvt<number>({
        statefulObservable: $lastDelayedTime,
      });

      function getDoUseDelay() {
        const doUseDelay = Date.now() - evtLastDelayedTime.state > 30000;

        if (doUseDelay) {
          evtLastDelayedTime.state = Date.now();
        }

        return doUseDelay;
      }

      return { getDoUseDelay };
    })();

    const next = runExclusive.build(async () => {
      if (getDoUseDelay()) {
        await new Promise((resolve) => setTimeout(resolve, minimumDisplayDuration));
      }

      evtDisplayState.state = {
        ...evtDisplayState.state,
        prevTime: Date.now(),
      };
    });

    async function globalHideSplashScreen() {
      evtDisplayState.state.count = Math.max(evtDisplayState.state.count - 1, 0);

      if (runExclusive.isRunning(next)) {
        return;
      }

      next();
    }

    return { globalHideSplashScreen };
  })();

  function globalShowSplashScreen(params: { enableTransparency: boolean }) {
    evtDisplayState.state = {
      count: evtDisplayState.state.count + 1,
      isTransparencyEnabled: params.enableTransparency,
      prevTime: Date.now(),
      onHiddens: [],
    };
  }

  function useSplashScreenStatusInternal() {
    useRerenderOnStateChange(evtDisplayState);

    const { isSplashScreenShown, isTransparencyEnabled } = useGuaranteedMemo(
      () => ({
        isSplashScreenShown: evtDisplayState.state.count > 0,
        isTransparencyEnabled: evtDisplayState.state.isTransparencyEnabled,
      }),
      [evtDisplayState.state]
    );

    return {
      isSplashScreenShown,
      isTransparencyEnabled,
    };
  }

  function useSplashScreen(params?: {
    onHidden?(): void;
    fadeOutDuration?: number;
    minimumDisplayDuration?: number;
  }) {
    if (params?.fadeOutDuration !== undefined) {
      fadeOutDuration = params.fadeOutDuration;
    }

    if (params?.minimumDisplayDuration !== undefined) {
      minimumDisplayDuration = params.minimumDisplayDuration;
    }

    const isUsingSplashScreen = useContext(context);

    useEffect(() => {
      const { onHidden } = params ?? {};

      if (onHidden === undefined) {
        return;
      }

      if (!isUsingSplashScreen) {
        onHidden();
        return;
      }

      evtDisplayState.state.onHiddens.push(onHidden);
    }, []);

    const { showSplashScreen, hideSplashScreen } = (function useClosure() {
      const countRef = useRef<number>(0);

      const showSplashScreen = useConstCallback<typeof globalShowSplashScreen>(({ enableTransparency }) => {
        countRef.current++;

        globalShowSplashScreen({ enableTransparency });
      });

      const hideSplashScreen = useConstCallback<typeof globalHideSplashScreen>(async () => {
        if (countRef.current === 0) {
          return;
        }

        countRef.current--;

        await globalHideSplashScreen();
      });

      return { showSplashScreen, hideSplashScreen };
    })();

    const { isSplashScreenShown, isTransparencyEnabled } = useSplashScreenStatusInternal();

    return {
      isSplashScreenShown,
      isTransparencyEnabled,
      hideRootSplashScreen: globalHideSplashScreen,
      showSplashScreen,
      hideSplashScreen,
    };
  }

  function useSplashScreenStatus() {
    const { isSplashScreenShown, isTransparencyEnabled } = useSplashScreenStatusInternal();

    useEffect(() => {
      if (isSplashScreenShown) {
        return;
      }

      const delayLeft =
        [fadeOutDuration - (Date.now() - evtDisplayState.state.prevTime)].filter((v) => v > 0)[0] ?? 0;

      let timer: ReturnType<typeof setTimeout>;

      (async () => {
        await new Promise((resolve) => (timer = setTimeout(resolve, delayLeft)));

        evtDisplayState.state.onHiddens.forEach((onHidden) => onHidden());

        evtDisplayState.state.onHiddens = [];
      })();

      return () => clearTimeout(timer);
    }, [isSplashScreenShown]);

    return { isSplashScreenShown, isTransparencyEnabled };
  }

  return { useSplashScreen, useSplashScreenStatus };
})();

export { useSplashScreen };

export type SplashScreenProps = {
  Logo: ReactComponent;
  /** Default 700ms */
  fadeOutDuration?: number;
  /** Default 1000 (1 second)*/
  minimumDisplayDuration?: number;
  children: ReactNode;
};

const context = createContext<boolean>(false);

export function createSplashScreen(params: { useTheme(): Theme }) {
  const { useTheme } = params;

  const { makeStyles } = createMakeStyles({ useTheme });

  function SplashScreen(props: SplashScreenProps) {
    const { children, Logo } = props;

    if (props?.fadeOutDuration !== undefined) {
      fadeOutDuration = props.fadeOutDuration;
    }

    if (props?.minimumDisplayDuration !== undefined) {
      minimumDisplayDuration = props.minimumDisplayDuration;
    }

    const { isSplashScreenShown, isTransparencyEnabled } = useSplashScreenStatus();

    {
      const defaultOverflow = useConst(() => document.body.style.overflow);

      useEffect(() => {
        document.body.style.overflow = isSplashScreenShown ? "hidden" : defaultOverflow;
      }, [isSplashScreenShown]);
    }

    const [isFadingOut, setIsFadingOut] = useState(false);
    const [isVisible, setIsVisible] = useState(true);

    const { isViewPortAdapterEnabled } = (function useClosure() {
      const { viewPortState } = useViewPortState();

      const isViewPortAdapterEnabled = viewPortState !== undefined;

      return { isViewPortAdapterEnabled };
    })();

    const { classes } = useStyles({
      isVisible,
      isFadingOut,
      isTransparencyEnabled,
      isViewPortAdapterEnabled,
    });

    useEffect(() => {
      let timer = setTimeout(() => {
        /* No action */
      }, 0);

      (async () => {
        if (isSplashScreenShown) {
          setIsFadingOut(false);
          setIsVisible(true);
        } else {
          setIsFadingOut(true);

          await new Promise((resolve) => (timer = setTimeout(resolve, fadeOutDuration)));

          setIsFadingOut(false);
          setIsVisible(false);
        }
      })();

      return () => clearTimeout(timer);
    }, [isSplashScreenShown]);

    return (
      <context.Provider value={true}>
        <div className={classes.root}>
          <Logo />
        </div>
        {children}
      </context.Provider>
    );
  }

  const useStyles = makeStyles<{
    isVisible: boolean;
    isFadingOut: boolean;
    isTransparencyEnabled: boolean;
    isViewPortAdapterEnabled: boolean;
  }>({ name: { SplashScreen } })(
    (theme, { isVisible, isFadingOut, isTransparencyEnabled, isViewPortAdapterEnabled }) => ({
      root: {
        width: "100%",
        height: isViewPortAdapterEnabled ? "100%" : "100vh",
        position: "fixed",
        top: 0,
        left: 0,
        zIndex: 10,
        backgroundColor: (() => {
          const color = new Color(theme.colors.useCases.surfaces.background).rgb();

          return color.alpha(isTransparencyEnabled ? 0.6 : (color as any).valpha).string();
        })(),
        backdropFilter: isTransparencyEnabled ? "blur(10px)" : undefined,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        visibility: isVisible ? "visible" : "hidden",
        opacity: isFadingOut ? 0 : 1,
        transition: `opacity ease-in-out ${fadeOutDuration}ms`,
      },
    })
  );

  return { SplashScreen };
}

/**
 * You have to create your own version of this component
 * you are expected to size it in percentage.
 */
export function createGOATSplashScreenLogo(params: { useTheme(): Theme }) {
  const { useTheme } = params;

  const { makeStyles } = createMakeStyles({ useTheme });

  // eslint-disable-next-line react/display-name
  const GOATSplashScreenLogo = memo(() => {
    const { classes } = useStyles();
    return <GOATLogoSvg className={classes.root} />;
  });

  const useStyles = makeStyles({ name: { GOATSplashScreenLogo } })((theme) => ({
    root: {
      height: "20%",
      fill: theme.colors.useCases.typography.textFocus,
      "& g": {
        opacity: 0,
        animation: `${keyframes`
                          60%, 100% {
                              opacity: 0;
                          }
                          0% {
                              opacity: 0;
                          }
                          40% {
                              opacity: 1;
                          }
                          `} 3.5s infinite ease-in-out`,
        "&:nth-of-type(1)": {
          animationDelay: ".4s",
        },
        "&:nth-of-type(2)": {
          animationDelay: ".8s",
        },
        "&:nth-of-type(3)": {
          animationDelay: "1.2s",
        },
      },
    },
  }));

  return { GOATSplashScreenLogo };
}
