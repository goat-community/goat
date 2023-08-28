/* eslint-disable @typescript-eslint/no-non-null-assertion */

/* eslint-disable react/display-name */

/* eslint-disable jsx-a11y/anchor-is-valid */
import { Box, Card } from "@mui/material";
import Grid from "@mui/material/Unstable_Grid2";
import { usePrepareTemplate } from "keycloakify/lib/usePrepareTemplate";
import { type TemplateProps as GenericTemplateProps } from "keycloakify/login/TemplateProps";
import { useGetClassName } from "keycloakify/login/lib/useGetClassName";
import { useConstCallback } from "powerhooks/useConstCallback";
import { memo } from "react";
import { symToStr } from "tsafe/symToStr";

import { Alert } from "@p4b/ui/components/Alert";
import { useDomRect } from "@p4b/ui/lib";

import { ThemeProvider, makeStyles, Text } from "../theme";
import type { I18n } from "./i18n";
import type { KcContext } from "./kcContext";

type TemplateProps = GenericTemplateProps<KcContext, I18n>;

export default function Template(props: TemplateProps) {
  return (
    <ThemeProvider>
      <ContextualizedTemplate {...props} />
    </ThemeProvider>
  );
}

function ContextualizedTemplate(props: TemplateProps) {
  const { kcContext, doUseDefaultCss, classes: classes_props, children } = props;

  const { ref: rootRef } = useDomRect();

  const isDarkModeEnabled = false;

  const { classes } = useStyles();

  const { getClassName } = useGetClassName({
    doUseDefaultCss,
    classes: classes_props,
  });

  const { url } = kcContext;

  const { isReady } = usePrepareTemplate({
    doFetchDefaultThemeResources: doUseDefaultCss,
    url,
    styles: ["css/login.css"],
    htmlClassName: getClassName("kcHtmlClass"),
    bodyClassName: undefined,
  });

  if (!isReady) {
    return null;
  }

  return (
    <div ref={rootRef}>
      <Box component="main" className={classes.main}>
        <Grid container className={classes.gridContainer}>
          <Grid xs={12} lg={6} className={classes.gridLeft}>
            <Box
              component="header"
              sx={{
                left: 0,
                p: 3,
                position: "fixed",
                top: 0,
                width: "100%",
              }}>
              <Box
                component="a"
                href="https://www.plan4better.de/"
                target="_blank"
                sx={{
                  display: "inline-flex",
                  width: 160,
                }}>
                <img
                  width="100%"
                  src={`https://assets.plan4better.de/img/logo/plan4better_${
                    isDarkModeEnabled ? "white" : "standard"
                  }.svg`}
                  alt="Plan4Better Logo"
                />
              </Box>
            </Box>
            <Page {...props} className={classes.page}>
              {children}
            </Page>
          </Grid>
          <Grid xs={12} lg={6} className={classes.gridRight}>
            <Box sx={{ p: 3, width: 350 }} component="div">
              <img
                width="100%"
                src="https://assets.plan4better.de/img/logo/goat_white.svg"
                alt="Plan4Better Logo"
              />
            </Box>
          </Grid>
        </Grid>
      </Box>
    </div>
  );
}

const useStyles = makeStyles()((theme) => ({
  main: {
    display: "flex",
    flex: "1 1 auto",
  },
  gridContainer: {
    flex: "1 1 auto",
  },
  gridLeft: {
    height: "100vh",
    display: "flex",
    flexDirection: "column",
    backgroundColor: theme.colors.useCases.surfaces.background,
  },
  gridRight: {
    alignItems: "center",
    background:
      "radial-gradient(50% 50% at 50% 50%, rgba(40,54,72,0.8) 0%, rgba(40,54,72,0.9) 100%), url(https://assets.plan4better.de/img/login/artwork_1.png) no-repeat center",
    backgroundSize: "cover",
    color: "white",
    display: "flex",
    justifyContent: "center",
    "& img": {
      maxWidth: "100%",
    },
  },
  header: {
    left: 0,
    p: 3,
    position: "fixed",
    top: 0,
    width: "100%",
  },
  page: {
    height: "100%",
    overflow: "auto",
  },
}));

const { Page } = (() => {
  type Props = { className: string } & Pick<
    TemplateProps,
    | "displayInfo"
    | "displayMessage"
    | "displayRequiredFields"
    | "displayWide"
    | "showAnotherWayIfPresent"
    | "headerNode"
    | "showUsernameNode"
    | "infoNode"
    | "kcContext"
    | "i18n"
    | "children"
    | "doUseDefaultCss"
  >;

  const Page = memo((props: Props) => {
    const {
      className,
      displayInfo = false,
      displayMessage = true,
      displayRequiredFields = false,
      displayWide = false,
      showAnotherWayIfPresent = true,
      headerNode,
      showUsernameNode = null,
      infoNode = null,
      kcContext,
      doUseDefaultCss,
      i18n,
      children,
    } = props;

    const {
      ref: containerRef,
      domRect: { height: containerHeight },
    } = useDomRect();
    const {
      ref: paperRef,
      domRect: { height: paperHeight },
    } = useDomRect();

    const { classes, cx } = useStyles({
      isPaperBiggerThanContainer: paperHeight > containerHeight,
    });
    return (
      <div ref={containerRef} className={cx(classes.root, className)}>
        <Card ref={paperRef} className={classes.paper}>
          <Head
            kcContext={kcContext}
            displayRequiredFields={displayRequiredFields}
            headerNode={headerNode}
            showUsernameNode={showUsernameNode}
            i18n={i18n}
            doUseDefaultCss={doUseDefaultCss}
          />
          <Main
            kcContext={kcContext}
            displayMessage={displayMessage}
            showAnotherWayIfPresent={showAnotherWayIfPresent}
            displayWide={displayWide}
            displayInfo={displayInfo}
            infoNode={infoNode}
            i18n={i18n}
            doUseDefaultCss={doUseDefaultCss}>
            {children}
          </Main>
        </Card>
      </div>
    );
  });

  const useStyles = makeStyles<{ isPaperBiggerThanContainer: boolean }>({
    name: { Page },
  })((theme, { isPaperBiggerThanContainer }) => ({
    root: {
      display: "flex",
      justifyContent: "center",
      alignItems: isPaperBiggerThanContainer ? undefined : "center",
    },
    paper: {
      padding: theme.spacing(5),
      width: 490,
      height: "fit-content",
      marginBottom: theme.spacing(4),
      borderRadius: 4,
    },
    alert: {
      alignItems: "center",
    },
    crossButtonWrapper: {
      display: "flex",
    },
  }));

  const { Head } = (() => {
    type Props = Pick<
      TemplateProps,
      | "displayRequiredFields"
      | "headerNode"
      | "showUsernameNode"
      | "i18n"
      | "classes"
      | "doUseDefaultCss"
      | "kcContext"
    >;

    const Head = memo((props: Props) => {
      const {
        kcContext,
        displayRequiredFields,
        headerNode,
        showUsernameNode,
        i18n,
        classes: classes_props,
        doUseDefaultCss,
      } = props;

      const { msg } = i18n;

      const { classes, cx } = useStyles();

      const { getClassName } = useGetClassName({
        doUseDefaultCss,
        classes: classes_props,
      });

      return (
        <header>
          {!(
            kcContext.auth !== undefined &&
            kcContext.auth.showUsername &&
            !kcContext.auth.showResetCredentials
          ) ? (
            displayRequiredFields ? (
              <div className={getClassName("kcContentWrapperClass")}>
                <div className={cx(getClassName("kcLabelWrapperClass"), "subtitle")}>
                  <span className="subtitle">
                    <span className="required">*</span>
                    {msg("requiredFields")}
                  </span>
                </div>
                <div className="col-md-10">
                  <Text className={classes.root} typo="section heading">
                    {headerNode!}
                  </Text>
                </div>
              </div>
            ) : (
              <Text className={classes.root} typo="section heading">
                {headerNode!}
              </Text>
            )
          ) : displayRequiredFields ? (
            <div className={getClassName("kcContentWrapperClass")}>
              <div className={cx(getClassName("kcLabelWrapperClass"), "subtitle")}>
                <span className="subtitle">
                  <span className="required">*</span> {msg("requiredFields")}
                </span>
              </div>
              <div className="col-md-10">
                {showUsernameNode}
                <div className={getClassName("kcFormGroupClass")}>
                  <div id="kc-username">
                    <label id="kc-attempted-username">{kcContext.auth?.attemptedUsername}</label>
                    <a id="reset-login" href={kcContext.url.loginRestartFlowUrl}>
                      <div className="kc-login-tooltip">
                        <i className={getClassName("kcResetFlowIcon")} />
                        <span className="kc-tooltip-text">{msg("restartLoginTooltip")}</span>
                      </div>
                    </a>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <>
              {showUsernameNode}
              <div className={getClassName("kcFormGroupClass")}>
                <div id="kc-username">
                  <label id="kc-attempted-username">{kcContext.auth?.attemptedUsername}</label>
                  <a id="reset-login" href={kcContext.url.loginRestartFlowUrl}>
                    <div className="kc-login-tooltip">
                      <i className={getClassName("kcResetFlowIcon")} />
                      <span className="kc-tooltip-text">{msg("restartLoginTooltip")}</span>
                    </div>
                  </a>
                </div>
              </div>
            </>
          )}
        </header>
      );
    });

    const useStyles = makeStyles({
      name: `${symToStr({ Template })}${symToStr({ Head })}`,
    })((theme) => ({
      root: {
        textAlign: "left",
        marginTop: theme.spacing(3),
        marginBottom: theme.spacing(6),
      },
    }));

    return { Head };
  })();

  const { Main } = (() => {
    type Props = Pick<
      TemplateProps,
      | "displayMessage"
      | "children"
      | "showAnotherWayIfPresent"
      | "displayWide"
      | "displayInfo"
      | "infoNode"
      | "i18n"
      | "kcContext"
      | "doUseDefaultCss"
      | "classes"
    >;

    const Main = memo((props: Props) => {
      const {
        displayMessage,
        showAnotherWayIfPresent,
        displayInfo,
        displayWide,
        kcContext,
        children,
        infoNode,
        i18n,
        doUseDefaultCss,
        classes: classes_props,
      } = props;

      const onTryAnotherWayClick = useConstCallback(() => {
        document.forms["kc-select-try-another-way-form" as never].submit();
        return false;
      });

      const { getClassName } = useGetClassName({
        doUseDefaultCss,
        classes: classes_props,
      });

      const { msg } = i18n;

      const { classes, cx } = useStyles();

      return (
        <div id="kc-content">
          <div id="kc-content-wrapper">
            {/* App-initiated actions should not see warning messages about the need to complete the action during login.*/}
            {displayMessage &&
              kcContext.message !== undefined &&
              (kcContext.message.type !== "warning" || !kcContext.isAppInitiatedAction) && (
                <Alert className={classes.alert} severity={kcContext.message.type}>
                  <Text typo="label 2">
                    <span
                      dangerouslySetInnerHTML={{
                        __html: kcContext.message.summary,
                      }}
                    />
                  </Text>
                </Alert>
              )}
            {children}
            {kcContext.auth !== undefined &&
              kcContext.auth.showTryAnotherWayLink &&
              showAnotherWayIfPresent && (
                <form
                  id="kc-select-try-another-way-form"
                  action={kcContext.url.loginAction}
                  method="post"
                  className={cx(displayWide && getClassName("kcContentWrapperClass"))}>
                  <div
                    className={cx(
                      displayWide && [
                        getClassName("kcFormSocialAccountContentClass"),
                        getClassName("kcFormSocialAccountClass"),
                      ]
                    )}>
                    <div className={cx(getClassName("kcFormGroupClass"))}>
                      <input type="hidden" name="tryAnotherWay" value="on" />
                      <a href="#" id="try-another-way" onClick={onTryAnotherWayClick}>
                        {msg("doTryAnotherWay")}
                      </a>
                    </div>
                  </div>
                </form>
              )}
            {displayInfo && (
              <div id="kc-info">
                <div id="kc-info-wrapper" className={classes.infoNode}>
                  {infoNode}
                </div>
              </div>
            )}
          </div>
        </div>
      );
    });

    const useStyles = makeStyles({
      name: `${symToStr({ Template })}${symToStr({ Main })}`,
    })((theme) => ({
      alert: {
        alignItems: "center",
      },
      infoNode: {
        "& div": {
          marginTop: theme.spacing(3),
          textAlign: "left",
        },
      },
    }));

    return { Main };
  })();

  return { Page };
})();
