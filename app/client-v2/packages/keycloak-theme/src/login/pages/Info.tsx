import { Link } from "@mui/material";
import type { PageProps } from "keycloakify/login/pages/PageProps";
import { assert } from "keycloakify/tools/assert";

import { Text, Button, makeStyles } from "../../theme";
import type { I18n } from "../i18n";
import type { KcContext } from "../kcContext";

export default function Info(props: PageProps<Extract<KcContext, { pageId: "info.ftl" }>, I18n>) {
  const { kcContext, i18n, doUseDefaultCss, Template, classes: classes_props } = props;

  const { msgStr, msg } = i18n;

  assert(kcContext.message !== undefined);
  const { classes } = useStyles();

  const { messageHeader, message, requiredActions, skipLink, pageRedirectUri, actionUri, client } = kcContext;

  return (
    <Template
      {...{ kcContext, i18n, doUseDefaultCss }}
      classes={classes_props}
      displayMessage={false}
      headerNode={messageHeader !== undefined ? <>{messageHeader}</> : <>{message.summary}</>}>
      <div id="kc-info-message">
        <Text typo="body 2" color="primary">
          <p>
            {message.summary}

            {requiredActions !== undefined && (
              <b>
                {requiredActions
                  .map((requiredAction) => msgStr(`requiredAction.${requiredAction}` as const))
                  .join(",")}
              </b>
            )}
          </p>
        </Text>
        {!skipLink && pageRedirectUri !== undefined ? (
          <Link href={pageRedirectUri}>
            <Button className={classes.buttonSubmit} type="submit" variant="ternary">
              {msg("backToApplication")}
            </Button>
          </Link>
        ) : actionUri !== undefined ? (
          <Link underline="hover" href={actionUri}>
            <Button className={classes.buttonSubmit} type="submit" variant="primary">
              {msg("proceedWithAction")}
            </Button>
          </Link>
        ) : (
          client.baseUrl !== undefined && (
            <Link underline="hover" href={client.baseUrl}>
              <Button className={classes.buttonSubmit} type="submit" variant="ternary">
                {msg("backToApplication")}
              </Button>
            </Link>
          )
        )}
      </div>
    </Template>
  );
}

const useStyles = makeStyles({ name: { Info } })((theme) => ({
  buttonSubmit: {
    width: "100%",
    marginTop: theme.spacing(4),
    marginLeft: theme.spacing(0),
  },
}));
