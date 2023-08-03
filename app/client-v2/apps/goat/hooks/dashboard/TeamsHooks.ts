import type { Option } from "@/app/[lng]/(dashboard)/settings/organization/AddTeamModal";
import type { Team } from "@/app/[lng]/(dashboard)/settings/organization/Teams";
import { filterSearch } from "@/lib/utils/helpers";
import { useEffect } from "react";

interface UseUserDialogProps {
  rawRows: Team[];
  userInDialog: Team | boolean;
  setUserInDialog: React.Dispatch<React.SetStateAction<Team | boolean>>;
  selectedOption: Option[] | null;
  searchText?: string;
  editTeam: (value: Team) => void;
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
  }, [userInDialog, selectedOption, searchText, rawRows]);

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

export function useTeamSearch(rawRows: Team[], searchText: string | undefined) {
  return filterSearch(rawRows, "name", searchText || "");
}
