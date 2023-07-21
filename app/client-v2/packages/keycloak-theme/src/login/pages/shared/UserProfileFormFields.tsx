import { Box, Link } from "@mui/material";
import { Stepper, Step, StepLabel } from "@mui/material";
import FormControlLabel from "@mui/material/FormControlLabel";
import type { Attribute } from "keycloakify/login/kcContext/KcContext";
import { useFormValidation } from "keycloakify/login/lib/useFormValidation";
import { useMemo, useEffect, Fragment } from "react";
import { capitalize } from "tsafe/capitalize";

import { Checkbox } from "@p4b/ui/components/Checkbox";
import type { AttributeOptions } from "@p4b/ui/components/Inputs";
import { TextField } from "@p4b/ui/components/Inputs";

import { Text, makeStyles } from "../../../theme";
import { regExpStrToEmailDomains } from "../../emailDomainAcceptListHelper";
import type { I18n } from "../../i18n";
import { getCountries } from "../../i18n";

interface Steps {
  [key: number]: string[];
}

export type UserProfileFormFieldsProps = {
  kcContext: Parameters<typeof useFormValidation>[0]["kcContext"];
  i18n: I18n;
  onIsFormSubmittableValueChange: (isFormSubmittable: boolean) => void;
  activeStep?: number;
  steps?: Steps;
  BeforeField?: (props: { attribute: Attribute }) => JSX.Element | null;
  AfterField?: (props: { attribute: Attribute }) => JSX.Element | null;
  getIncrementedTabIndex: () => number;
};

export function UserProfileFormFields(props: UserProfileFormFieldsProps) {
  const { kcContext, onIsFormSubmittableValueChange, i18n, activeStep, steps, getIncrementedTabIndex } =
    props;

  const { advancedMsg } = i18n;

  const {
    formValidationState: { fieldStateByAttributeName, isFormSubmittable },
    formValidationDispatch,
    attributesWithPassword,
  } = useFormValidation({
    kcContext,
    i18n,
  });
  const { msg, advancedMsgStr } = i18n;

  const { classes } = useStyles();
  const attributesWithPasswordOrdered = useMemo(() => {
    if (steps === undefined) {
      return attributesWithPassword;
    }
    const attributesWithPasswordOrdered: Attribute[] = [];
    for (const step of Object.values(steps)) {
      for (const attributeName of step) {
        const attribute = attributesWithPassword.find(({ name }) => name === attributeName);
        if (attribute !== undefined) {
          attributesWithPasswordOrdered.push(attribute);
        }
      }
    }
    return attributesWithPasswordOrdered;
  }, [attributesWithPassword, steps]);

  useEffect(() => {
    onIsFormSubmittableValueChange(isFormSubmittable);
  }, [isFormSubmittable, onIsFormSubmittableValueChange]);

  const areAllFieldsRequired = useMemo(
    () => attributesWithPasswordOrdered.every(({ required }) => required),
    [attributesWithPasswordOrdered]
  );

  // Terms and conditions checkbox
  const termsAndConditions = attributesWithPasswordOrdered.find(
    ({ name }) => name === "terms_and_conditions"
  );
  if (termsAndConditions !== undefined) {
    attributesWithPasswordOrdered.splice(attributesWithPasswordOrdered.indexOf(termsAndConditions), 1);
  }
  const handleTermsAndConditionChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    let newValue = "";
    if (event.target.checked) {
      newValue = Date.now().toString();
    }
    formValidationDispatch({
      action: "update value",
      name: "terms_and_conditions",
      newValue,
    });
  };

  // Subscribe to newsletter checkbox
  const subscribeToNewsletter = attributesWithPasswordOrdered.find(
    ({ name }) => name === "subscribe_to_newsletter"
  );
  if (subscribeToNewsletter !== undefined) {
    attributesWithPasswordOrdered.splice(attributesWithPasswordOrdered.indexOf(subscribeToNewsletter), 1);
  }
  const handleSubscribeToNewsletterChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    let newValue = "";
    if (event.target.checked) {
      newValue = Date.now().toString();
    }
    formValidationDispatch({
      action: "update value",
      name: "subscribe_to_newsletter",
      newValue,
    });
  };

  // Options Dropdown for all fields that have a predefined list of values
  const attributeOptions = useMemo(() => {
    const options: { [key: string]: AttributeOptions } = {};
    attributesWithPasswordOrdered.forEach((attribute) => {
      if (attribute.validators.options !== undefined) {
        // EdgeCase: Check if attributes.name is country
        // For country attributes we are getting the options from library
        if (attribute.name === "country") {
          const countries = getCountries(i18n.currentLanguageTag);
          options[attribute.name] = countries;
        } else {
          // translate options
          const options_i18n: AttributeOptions = [];
          attribute.validators.options.options.forEach((element: string) => {
            const option = advancedMsgStr(element);
            options_i18n.push({
              value: element,
              label: option,
            });
          });
          options[attribute.name] = options_i18n;
        }
      }
    });
    return options;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [i18n.currentLanguageTag]);

  // // Steps
  // // eslint-disable-next-line @typescript-eslint/no-unused-vars
  // const [isStep1Valid, setIsStep1Valid] = useState(false);

  // const handleStep1Validation = () => {
  //   if (activeStep === 0) {
  //     const fieldStates: boolean[] = [];
  //     steps[1].forEach((attributeName: string) => {
  //       const attribute = kcContext.profile.attributes.find(
  //         ({ name }: { name: string }) => name === attributeName
  //       );
  //       const value = fieldStateByAttributeName[attributeName]?.value;
  //       if (!fieldStateByAttributeName.hasOwnProperty(attributeName)) {
  //         fieldStates.push(true);
  //         return;
  //       }
  //       const isRequired = attribute?.required;
  //       const displayableErrors = fieldStateByAttributeName[attributeName].displayableErrors;

  //       if ((isRequired && value === "") || displayableErrors.length > 0) {
  //         fieldStates.push(false);
  //       } else {
  //         fieldStates.push(true);
  //       }
  //     });
  //     if (fieldStates.every((state) => state === true)) {
  //       setIsStep1Valid(true);
  //     } else {
  //       setIsStep1Valid(false);
  //     }
  //   }
  // };

  return (
    <>
      {activeStep !== undefined && steps !== undefined && (
        <Stepper activeStep={activeStep}>
          {Object.keys(steps).map((label) => (
            <Step sx={{ paddingRight: 0 }} key={label}>
              <StepLabel> </StepLabel>
            </Step>
          ))}
        </Stepper>
      )}

      {attributesWithPasswordOrdered.map((attribute, i) => {
        const { value, displayableErrors } = fieldStateByAttributeName[attribute.name];

        // find which step is attribute.name
        let isVisible = false;
        if (
          activeStep !== undefined &&
          steps !== undefined &&
          steps[activeStep + 1].includes(attribute.name) &&
          attribute.name !== "username"
        ) {
          isVisible = true;
        } else if ((activeStep === undefined || steps === undefined) && attribute.name !== "username") {
          isVisible = true;
        }

        return (
          <Fragment key={i}>
            <TextField
              type={(() => {
                switch (attribute.name) {
                  case "password-confirm":
                  case "password":
                    return "password";
                  default:
                    return "text";
                }
              })()}
              // show or hide if attribute.name is in steps
              id={attribute.name}
              name={attribute.name}
              defaultValue={value}
              className={isVisible ? classes.show : classes.hide}
              aria-invalid={displayableErrors.length !== 0}
              disabled={attribute.readOnly}
              autoComplete={attribute.autocomplete}
              onBlur={() => {
                if (attribute.name === "username")
                  // don't validate username onBlur
                  return;
                if (attribute.name === "email") {
                  formValidationDispatch({
                    action: "focus lost",
                    name: "username",
                  });
                }
                formValidationDispatch({
                  action: "focus lost",
                  name: attribute.name,
                });
              }}
              options={(() => {
                // check if attribute.name is in attributeOptions
                if (attribute.name in attributeOptions) {
                  return attributeOptions[attribute.name];
                }
                return undefined;
              })()}
              inputProps_aria-label={attribute.name}
              inputProps_tabIndex={attribute.name === "username" ? -1 : getIncrementedTabIndex()}
              onValueBeingTypedChange={({ value }) => {
                console.log("onValueBeingTypedChange", value);
                if (attribute.name === "username")
                  // don't validate username while typing
                  return;
                if (attribute.name === "email") {
                  formValidationDispatch({
                    action: "update value",
                    name: "username",
                    newValue: value,
                  });
                }
                formValidationDispatch({
                  action: "update value",
                  name: attribute.name,
                  newValue: value,
                });
              }}
              inputProps_autoFocus={i === 0}
              inputProps_spellCheck={false}
              transformValueBeingTyped={(() => {
                switch (attribute.name) {
                  case "firstName":
                  case "lastName":
                    return capitalize;
                  default:
                    return undefined;
                }
              })()}
              label={
                <>
                  {advancedMsg(attribute.displayName ?? "")}
                  &nbsp;
                  {!areAllFieldsRequired && attribute.required && "*"}
                </>
              }
              helperText={(() => {
                const displayableErrors = fieldStateByAttributeName[attribute.name].displayableErrors.filter(
                  ({ validatorName }) => !(validatorName === "pattern" && attribute.name === "email")
                );

                if (displayableErrors.length !== 0) {
                  return displayableErrors.map(({ errorMessage }, i) => (
                    <span key={i}>{errorMessage}&nbsp;</span>
                  ));
                }

                switch (attribute.name) {
                  case "email":
                    return msg("allowedEmailDomains");
                  case "password": {
                    // prettier-ignore
                    const { min } = attribute.validators.length ?? {};
                    if (min === undefined) {
                      break;
                    }

                    // prettier-ignore
                    return msg("minimumLength", `${parseInt(min)}`);
                  }
                }

                {
                  // prettier-ignore
                  const { pattern } = attribute.validators;

                  if (pattern !== undefined) {
                    const { "error-message": errorMessageKey } = pattern;

                    // prettier-ignore
                    return errorMessageKey !== undefined ?
                                            advancedMsg(errorMessageKey) :
                                            msg("mustRespectPattern");
                  }
                }

                return undefined;
              })()}
              // prettier-ignore
              questionMarkHelperText={(() => {
                                const { pattern } = attribute.validators.pattern ?? {};

                                // prettier-ignore
                                return pattern === undefined ?
                                    undefined :
                                    attribute.name === "email" ?
                                        (() => {

                                            try {
                                                return regExpStrToEmailDomains(pattern).join(", ");
                                            } catch {
                                                return pattern;
                                            }

                                        })() :
                                        fieldStateByAttributeName[attribute.name].displayableErrors.length === 0 ?
                                            pattern :
                                            undefined;
                            })()}
              // prettier-ignore
              inputProps_aria-invalid={fieldStateByAttributeName[attribute.name].displayableErrors.length !== 0}
            />
          </Fragment>
        );
      })}
      {/* Terms and Conditions */}
      {termsAndConditions && (activeStep == 1 || activeStep === undefined) && (
        <div className={classes.acceptTermsWrapper}>
          <div className="checkbox">
            <FormControlLabel
              control={
                <Checkbox
                  id="terms_and_conditions"
                  name="terms_and_conditions"
                  tabIndex={3}
                  color="primary"
                  onChange={handleTermsAndConditionChange}
                />
              }
              label={
                <Box
                  sx={{
                    display: "flex",
                  }}>
                  <Text typo="body 2" color="secondary">
                    {msg("accept")}
                    <Link
                      sx={{
                        marginLeft: "2px",
                      }}
                      href="https://plan4better.de/en/privacy/"
                      target="_blank">
                      {msg("terms")}
                    </Link>
                  </Text>
                </Box>
              }
            />
          </div>
        </div>
      )}
      {/* Subscribe To Newsletter */}
      {subscribeToNewsletter && (activeStep == 1 || activeStep === undefined) && (
        <div className={classes.subscribeToNewsletterWrapper}>
          <div className="checkbox">
            <FormControlLabel
              control={
                <Checkbox
                  id="subscribe_to_newsletter"
                  name="subscribe_to_newsletter"
                  tabIndex={3}
                  color="primary"
                  onChange={handleSubscribeToNewsletterChange}
                />
              }
              label={
                <Box
                  sx={{
                    display: "flex",
                  }}>
                  <Text typo="body 2" color="secondary">
                    {msg("subscribeToNewsletter")}
                  </Text>
                </Box>
              }
            />
          </div>
        </div>
      )}
    </>
  );
}

const useStyles = makeStyles({ name: { UserProfileFormFields } })((theme) => ({
  acceptTermsWrapper: {
    display: "flex",
    marginTop: theme.spacing(2),
  },
  subscribeToNewsletterWrapper: {
    display: "flex",
    marginTop: theme.spacing(0),
  },
  // We use show/hide to avoid the "jumping" effect when the component is mounted/unmounted
  show: {},
  hide: {
    display: "none",
  },
}));
