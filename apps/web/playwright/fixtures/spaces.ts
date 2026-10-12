import { type APIRequestContext, expect } from "@playwright/test";

import { API_URL } from "./users";

/**
 * A team the owner creates once and keeps, with the given members, and the
 * root folder of its space. Teams are not deleted after a run: a team space
 * that still holds content refuses deletion, trashed content included.
 */
export const ensureTeamSpace = async (
  owner: APIRequestContext,
  name: string,
  memberIds: string[]
): Promise<{ teamId: string; spaceId: string; folderId: string }> => {
  const teams = await owner.get(`${API_URL}/api/v2/teams`);
  expect(teams.ok(), await teams.text()).toBeTruthy();
  let team = ((await teams.json()) as { id: string; name: string }[]).find((t) => t.name === name);
  if (!team) {
    const created = await owner.post(`${API_URL}/api/v2/teams`, { data: { name } });
    expect(created.ok(), await created.text()).toBeTruthy();
    team = (await created.json()) as { id: string; name: string };
  }
  const members = await owner.get(`${API_URL}/api/v2/teams/${team.id}/members`);
  const present = new Set(((await members.json()) as { id: string }[]).map((m) => m.id));
  for (const id of memberIds.filter((member) => !present.has(member))) {
    const added = await owner.post(`${API_URL}/api/v2/teams/${team.id}/users/${id}`);
    expect(added.ok(), await added.text()).toBeTruthy();
  }

  const spaces = await owner.get(`${API_URL}/api/v2/space`);
  expect(spaces.ok(), await spaces.text()).toBeTruthy();
  const space = ((await spaces.json()) as { id: string; kind: string; team_id: string | null }[]).find(
    (s) => s.kind === "team" && s.team_id === team!.id
  );
  expect(space, `no space for team ${name}`).toBeTruthy();
  const folders = await owner.get(`${API_URL}/api/v2/folder`);
  const root = ((await folders.json()) as { id: string; name: string; space_id: string | null }[]).find(
    (folder) => folder.space_id === space!.id && folder.name === "home"
  );
  expect(root, `no root folder in the space of team ${name}`).toBeTruthy();
  return { teamId: team.id, spaceId: space!.id, folderId: root!.id };
};

/** An item of a space's content by name, as the Content page lists it. */
export const spaceItem = async (
  api: APIRequestContext,
  spaceId: string,
  name: string
): Promise<{ id: string; type: string; folder_id: string | null } | undefined> => {
  const listed = await api.get(`${API_URL}/api/v2/content`, {
    params: { view: "space", space_id: spaceId, search: name },
  });
  expect(listed.ok(), await listed.text()).toBeTruthy();
  const body = (await listed.json()) as
    | { items: { id: string; name: string; type: string; folder_id: string | null }[] }
    | { id: string; name: string; type: string; folder_id: string | null }[];
  const items = Array.isArray(body) ? body : body.items;
  return items.find((item) => item.name === name);
};
