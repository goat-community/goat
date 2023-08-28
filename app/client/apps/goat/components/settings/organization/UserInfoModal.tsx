
import React, { useState } from "react";
import { v4 } from "uuid";

import { Switch } from "@p4b/ui/components/Inputs";
import { SelectField } from "@p4b/ui/components/Inputs";
import { Text } from "@p4b/ui/components/theme";
import { makeStyles } from "@p4b/ui/lib/ThemeProvider";
import type {IUser} from "@/types/dashboard/organization";

interface UserInfoModal {
  ismodalVisible: boolean;
  userInDialog: IUser | undefined;
  editUserRole: (role: "Admin" | "User" | "Editor", user: IUser | undefined) => void;
}

const UserInfoModal = (props: UserInfoModal) => {
  const { ismodalVisible, userInDialog, editUserRole } = props;

  const { classes } = useStyles();

  const [extensions, setExtensions] = useState<
    {
      id: string;
      extension: string;
      studyarea: string;
      maxPlaces: number;
      checked: boolean;
      placesLeft: number;
    }[]
  >([
    {
      id: "1",
      extension: "Active mobility",
      studyarea: "Greater Munich",
      maxPlaces: 3,
      placesLeft: 1,
      // available: "1 of 3 seats available",
      checked: false,
    },
    {
      id: "2",
      extension: "Motorised mobility",
      studyarea: "Greater Munich",
      maxPlaces: 3,
      placesLeft: 0,
      checked: false,
    },
    {
      id: "3",
      extension: "Active mobility",
      studyarea: "Berlin",
      maxPlaces: 3,
      placesLeft: 2,
      checked: false,
    },
    {
      id: "4",
      extension: "Active mobility",
      studyarea: "London",
      maxPlaces: 3,
      placesLeft: 3,
      checked: false,
    },
  ]);

  const organizationRoles = [
    {
      name: "User",
      value: "User",
    },
    {
      name: "Editor",
      value: "Editor",
    },
    {
      name: "Admin",
      value: "Admin",
    },
  ];

  // Function

  /**
   * Updates the state of the extensions array based on the provided element name and checked value
   * @param _
   * @param {boolean} checked - The new checked state of the switch.
   * @param {string | undefined} elementName - The name of the element associated with the switch.
   */

  function handleSwitch(
    _: React.ChangeEvent<HTMLInputElement>,
    checked: boolean,
    elementName: string | undefined
  ) {
    if (elementName) {
      extensions.forEach((ext, index) => {
        if (ext.id === elementName) {
          const newExtensionState = extensions;
          if (checked) {
            newExtensionState[index].placesLeft--;
          } else {
            newExtensionState[index].placesLeft++;
          }
          newExtensionState[index].checked = !ext.checked;
          setExtensions([...newExtensionState]);
        }
      });
    }
  }

  return (
    <>
      {ismodalVisible ? (
        <Text typo="body 1">
          By removing a user they won&apos;t be able to access any projects under your organisation
        </Text>
      ) : (
        <div>
          <div className={classes.userDataContainer}>
            <span className={classes.userDataText}>
              <Text typo="body 2" className={classes.userDataTitle}>
                Name:{" "}
              </Text>{" "}
              <Text typo="label 1" className={classes.userDataValue}>
                {userInDialog ? userInDialog?.name : ""}
              </Text>
            </span>
            <span className={classes.userDataText}>
              <Text typo="body 2" className={classes.userDataTitle}>
                E-mail:{" "}
              </Text>{" "}
              <Text typo="label 1" className={classes.userDataValue}>
                { userInDialog ? userInDialog?.email : ""}
              </Text>
            </span>
            <span className={classes.userDataText}>
              <Text typo="body 2" className={classes.userDataTitle}>
                Added in:{" "}
              </Text>{" "}
              <Text typo="label 1" className={classes.userDataValue}>
                { userInDialog  ? userInDialog?.Added : ""}
              </Text>
            </span>
            <span className={classes.userDataText}>
              <Text typo="body 2" className={classes.userDataTitle}>
                Last Active:{" "}
              </Text>{" "}
              <Text typo="label 1" className={classes.userDataValue}>
                3 days ago
              </Text>
            </span>
            <span className={classes.userDataText}>
              <Text typo="body 2" className={classes.userDataTitle}>
                Organisation role:{" "}
              </Text>{" "}
              <SelectField
                options={organizationRoles}
                label="Role"
                size="small"
                defaultValue={ userInDialog ? userInDialog?.role : ""}
                updateChange={(value: "Admin" | "Editor" | "User") =>
                  editUserRole(value, typeof userInDialog !== "boolean" ? userInDialog : undefined)
                }
              />
            </span>
            <span className={classes.userDataText}>
              <Text typo="body 2" className={classes.userDataTitle}>
                Status:{" "}
              </Text>{" "}
              <div className={classes.userDataValue}>
                { userInDialog  ? userInDialog?.status : ""}
              </div>
            </span>
          </div>
          <div className={classes.allSwitchers}>
            <Text typo="body 2" className={classes.name}>
              Extensions:
            </Text>
            {extensions.map((extension) => (
              <div key={v4()} className={classes.switcher}>
                <Switch
                  checked={extension.checked}
                  onChecked={handleSwitch}
                  elementName={extension.id}
                  disabled={!extension.placesLeft && !extension.checked}
                />
                <Text typo="body 1">
                  {extension.extension} - {extension.studyarea}
                </Text>
                <Text typo="caption" color="secondary">
                  {extension.placesLeft} of {extension.maxPlaces} seats available
                </Text>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
};

const useStyles = makeStyles({ name: { UserInfoModal } })((theme) => ({
  name: {
    fontWeight: "bold",
  },
  container: {
    padding: `0px ${theme.spacing(3)}px`,
    marginBottom: theme.spacing(2),
  },
  userDataContainer: {
    border: `1px solid ${theme.colors.palette[theme.isDarkModeEnabled ? "dark" : "light"].greyVariant1}`,
    padding: theme.spacing(3),
    borderRadius: 4,
  },
  userDataText: {
    display: "flex",
    gap: theme.spacing(2),
    alignItems: "center",
    marginBottom: theme.spacing(2),
  },
  userDataTitle: {
    fontWeight: "800",
  },
  switcher: {
    display: "flex",
    alignItems: "center",
    gap: theme.spacing(1),
    marginTop: theme.spacing(2),
  },
  allSwitchers: {
    margin: `${theme.spacing(5)}px 0px`,
  },
  userDataValue: {
    marginTop: "3px",
  },
}));

export default UserInfoModal;
