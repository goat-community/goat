import { Link } from "@mui/material";
import type { PageProps } from "keycloakify/login/pages/PageProps";

import { makeStyles, Text } from "../../theme";
import type { I18n } from "../i18n";
import type { KcContext } from "../kcContext";

export default function Error(props: PageProps<Extract<KcContext, { pageId: "error.ftl" }>, I18n>) {
  const { kcContext, i18n, doUseDefaultCss, Template } = props;

  const { message, client } = kcContext;

  const { msg } = i18n;
  const { classes } = useStyles();
  return (
    <Template {...{ kcContext, i18n, doUseDefaultCss }} displayMessage={false} headerNode={msg("errorTitle")}>
      <div id="kc-error-message">
        <Text typo="body 2" color="primary">
          {message.summary}
        </Text>
        {client !== undefined && client.baseUrl !== undefined && (
          <div className={classes.linkWrapper}>
            <Link id="backToApplication" href={client.baseUrl}>
              {msg("backToApplication")}
            </Link>
          </div>
        )}
      </div>
    </Template>
  );
}

const useStyles = makeStyles({ name: { Error } })((theme) => ({
  linkWrapper: {
    marginTop: theme.spacing(5),
    textAlign: "left",
  },
}));
