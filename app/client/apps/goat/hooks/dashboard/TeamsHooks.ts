import type { Option } from "@p4b/types/atomicComponents";
import { filterSearch } from "@/lib/utils/helpers";
import type React from "react";
import { useEffect } from "react";
import type {ITeam} from "@/types/dashboard/organization";

interface UseUserDialogProps {
  rawRows: ITeam[];
  userInDialog: ITeam | boolean;
  setUserInDialog: React.Dispatch<React.SetStateAction<ITeam | boolean>>;
  selectedOption: Option[] | null;
  searchText?: string;
  editTeam: (value: ITeam) => void;
  teamName: string | null;
  setTeamName: React.Dispatch<React.SetStateAction<string | null>>;
  setSelectedOption: React.Dispatch<React.SetStateAction<Option[] | null>>;
}

export function useUserDialog({
  rawRows,
  userInDialog,
  setUserInDialog,
  selectedOption,
  searchText,
  editTeam,
  teamName,
  setTeamName,
  setSelectedOption,
}: UseUserDialogProps) {
  useEffect(() => {
    if (userInDialog && typeof userInDialog !== "boolean") {
      const team = rawRows.find((row) => row.name === userInDialog.name);

      if (team) {
        const selectedOptions = selectedOption
          ? selectedOption.filter((teams) => teams.selected)
          : team.participants.filter((teams) => teams.selected);
        if (JSON.stringify(selectedOptions) !== JSON.stringify(selectedOption)) {
          setSelectedOption(selectedOptions);
        }
        setTeamName(team.name);
      }
    }
  }, [setSelectedOption, setTeamName, userInDialog, selectedOption, searchText, rawRows]);

  function saveEditTeam() {
    if (userInDialog && typeof userInDialog !== "boolean") {
      const team = rawRows.find((row) => row.name === userInDialog.name);
      if (team) {
        const selectedOptions = selectedOption
          ? selectedOption.filter((teams) => teams.selected)
          : team.participants.filter((teams) => teams.selected);
        team.participants = selectedOptions;
        team.name = teamName ? teamName : "";
        editTeam(team);
        setUserInDialog(false);
      }
    }
  }

  return { saveEditTeam };
}

export function useTeamSearch(rawRows: ITeam[], searchText: string | undefined) {
  return filterSearch(rawRows, "name", searchText || "");
}
