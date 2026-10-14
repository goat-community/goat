import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import OrganizationWaiting from "@/app/onboarding/organization/waiting/page";

const INVITATION_ID = "7a1c2e9b-3f4d-4b5a-8c6d-0e1f2a3b4c5d";

const { useOrganizationMock, useOrganizationCreationMock, useInvitationsMock, replaceMock } = vi.hoisted(
  () => ({
    useOrganizationMock: vi.fn(),
    useOrganizationCreationMock: vi.fn(),
    useInvitationsMock: vi.fn(),
    replaceMock: vi.fn(),
  })
);

vi.mock("react-i18next", () => ({
  useTranslation: () => ({
    t: (key: string, options?: { email?: string }) => (options?.email ? `${key} ${options.email}` : key),
  }),
}));
vi.mock("next/navigation", () => ({ useRouter: () => ({ replace: replaceMock, push: vi.fn() }) }));
vi.mock("next-auth/react", () => ({
  useSession: () => ({ status: "authenticated", data: { user: { email: "newcomer@example.org" } } }),
  signOut: vi.fn(),
}));
vi.mock("@/lib/api/users", () => ({
  useOrganization: (...args: unknown[]) => useOrganizationMock(...args),
  useOrganizationCreation: () => useOrganizationCreationMock(),
  useInvitations: (...args: unknown[]) => useInvitationsMock(...args),
}));

/** The organization lookup: none (core answers 404), or one. */
const organization = (id?: string) => ({
  organization: id ? { id } : undefined,
  isError: id ? undefined : new Error("User has no organization"),
  mutate: vi.fn(),
  isValidating: false,
});
const creation = (allowed: boolean | undefined, isError?: Error) => ({
  organizationCreation: allowed === undefined ? undefined : { allowed },
  isError,
  mutate: vi.fn(),
  isValidating: false,
});
const invitations = (...ids: string[]) => ({
  invitations: { items: ids.map((id) => ({ id })), total: ids.length, page: 1, size: 50, pages: 1 },
  mutate: vi.fn(),
  isValidating: false,
});

const expectTheWaitingMessage = () => {
  expect(screen.getByText("waiting_for_invitation")).toBeInTheDocument();
  expect(screen.getByText("waiting_for_invitation_message newcomer@example.org")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "check_again" })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "logout" })).toBeInTheDocument();
};

beforeEach(() => {
  replaceMock.mockReset();
  useOrganizationMock.mockReset().mockReturnValue(organization());
  useOrganizationCreationMock.mockReset().mockReturnValue(creation(false));
  useInvitationsMock.mockReset().mockReturnValue(invitations());
});

describe("OrganizationWaiting", () => {
  it("asks the user to get invited with the email they signed in with", () => {
    render(<OrganizationWaiting />);

    expectTheWaitingMessage();
    expect(replaceMock).not.toHaveBeenCalled();
    expect(useInvitationsMock).toHaveBeenCalledWith({ type: "organization", status: "pending" });
  });

  it("sends a user who has an organization by now home", () => {
    useOrganizationMock.mockReturnValue(organization("org-1"));

    render(<OrganizationWaiting />);

    expect(replaceMock).toHaveBeenCalledWith("/");
    expect(screen.queryByText("waiting_for_invitation")).not.toBeInTheDocument();
  });

  it("opens an invitation as soon as there is one", () => {
    useInvitationsMock.mockReturnValue(invitations(INVITATION_ID));

    render(<OrganizationWaiting />);

    expect(replaceMock).toHaveBeenCalledWith(`/onboarding/organization/invite/${INVITATION_ID}`);
    expect(screen.queryByText("waiting_for_invitation")).not.toBeInTheDocument();
  });

  it("sends a user who may create an organization to the setup form", () => {
    useOrganizationCreationMock.mockReturnValue(creation(true));

    render(<OrganizationWaiting />);

    expect(replaceMock).toHaveBeenCalledWith("/onboarding/organization/create");
    expect(screen.queryByText("waiting_for_invitation")).not.toBeInTheDocument();
  });

  it("shows nothing until core has answered", () => {
    useOrganizationCreationMock.mockReturnValue(creation(undefined));

    render(<OrganizationWaiting />);

    expect(screen.queryByText("waiting_for_invitation")).not.toBeInTheDocument();
    expect(replaceMock).not.toHaveBeenCalled();
  });

  it("still offers Check again and Logout when core cannot answer", () => {
    useOrganizationCreationMock.mockReturnValue(creation(undefined, new Error("Bad gateway")));

    render(<OrganizationWaiting />);

    expectTheWaitingMessage();
    expect(replaceMock).not.toHaveBeenCalled();
  });

  it("asks core again on Check again", async () => {
    const none = organization();
    const waiting = creation(false);
    const noInvitation = invitations();
    useOrganizationMock.mockReturnValue(none);
    useOrganizationCreationMock.mockReturnValue(waiting);
    useInvitationsMock.mockReturnValue(noInvitation);

    render(<OrganizationWaiting />);
    await userEvent.click(screen.getByRole("button", { name: "check_again" }));

    expect(none.mutate).toHaveBeenCalled();
    expect(noInvitation.mutate).toHaveBeenCalled();
    expect(waiting.mutate).toHaveBeenCalled();
  });
});
