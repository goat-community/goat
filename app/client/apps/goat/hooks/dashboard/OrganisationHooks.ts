import { ORGANIZATION_API_URL } from "@/lib/api/apiConstants";
import { filterSearch, makeArrayUnique } from "@/lib/utils/helpers";
import axios from "axios";
import { useState, useEffect } from "react";
import useSWR from "swr";
import type {IUser} from "@/types/dashboard/organization";

// Get all users in order to manage them
export const useUsersData = (searchWord?: string) => {
  const UsersFetcher = (url: string) => {
    return axios(url).then((res: { data: IUser[] } ) => res.data);
  };

  const { data, error, isLoading } = useSWR(ORGANIZATION_API_URL, UsersFetcher);
  const [rawRows, setRawRows] = useState<IUser[]>([]);
  const [rows, setRows] = useState<IUser[]>([]);

  useEffect(() => {
    if (data) {
      setRawRows(data);
    }
  }, [data]);

  useEffect(() => {
    if (searchWord && searchWord !== "") {
      let newArr = [
        ...filterSearch(rawRows, "name", searchWord),
        ...filterSearch(rawRows, "email", searchWord),
      ];
      newArr = makeArrayUnique(newArr, "email");
      setRows(newArr);
    } else {
      setRows(rawRows);
    }
  }, [searchWord, rawRows]);

  return { rawRows, setRawRows, setRows, rows, isLoading, error };
};

// Invite a user dialog
export const useInviteUserDialog = () => {
  const [isAddUser, setAddUser] = useState(false);
  const [email, setEmail] = useState("");

  const openInviteDialog = () => setAddUser(true);
  const closeInviteDialog = () => setAddUser(false);

  return { isAddUser, openInviteDialog, closeInviteDialog, email, setEmail };
};

// Remove user dialog
export const useUserRemovalDialog = () => {
  const [userInDialog, setUserInDialog] = useState<IUser | undefined>(undefined);
  const [isModalVisible, setModalVisible] = useState<boolean>(false);

  const openUserRemovalDialog = (user: IUser) => {
    setModalVisible(true);
    setUserInDialog(user);
  };

  const closeUserRemovalDialog = () => {
    setModalVisible(false);
    setUserInDialog(undefined);
  };

  const setTheUserInDialog = (user: IUser | undefined) => {
    setUserInDialog(user);
  };

  return { userInDialog, isModalVisible, openUserRemovalDialog, closeUserRemovalDialog, setTheUserInDialog };
};
