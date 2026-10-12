import { ICON_NAME } from "@p4b/ui/components/Icon";

import { useOnboardingFacts } from "@/lib/api/onboarding";
import { patchPreferences, usePreferences } from "@/lib/api/preferences";
import type { OnboardingFacts } from "@/lib/validations/home";
import type { TemplateKind } from "@/lib/validations/template";

import { addLayerSource } from "@/components/addLayer/sources";

export type HomeStage = "new" | "getting_started" | "established";
export type SetupStepId = "project" | "data" | "catalog" | "analysis" | "workflow" | "team";
export const SETUP_STEPS: SetupStepId[] = ["project", "data", "catalog", "analysis", "workflow", "team"];

/** Which onboarding fact each checklist step reads. T10's two template steps
 * both read `has_workflow` — "run a workflow" is the done-ness signal for
 * either "run your first analysis" or "build a workflow", since both end
 * with a workflow existing in a project the caller created. */
const FACT_FOR_STEP: Record<SetupStepId, keyof OnboardingFacts> = {
  project: "has_project",
  data: "has_uploaded_layer",
  catalog: "has_catalog_layer",
  analysis: "has_workflow",
  workflow: "has_workflow",
  team: "has_team",
};

/** Icon, copy and call-to-action label for each checklist step (H9), shared
 * by the inline `SetupChecklist` card and the header `OnboardingTray`. */
export const SETUP_STEP_META: Record<
  SetupStepId,
  { icon: ICON_NAME; titleKey: string; bodyKey: string; ctaKey: string }
> = {
  project: {
    icon: ICON_NAME.MAP,
    titleKey: "step_project_title",
    bodyKey: "step_project_body",
    ctaKey: "new_project",
  },
  // The Upload dataset action, labelled and drawn as in the Add layer menu.
  data: {
    icon: addLayerSource("upload").icon,
    titleKey: "step_data_title",
    bodyKey: "step_data_body",
    ctaKey: addLayerSource("upload").labelKey,
  },
  catalog: {
    icon: ICON_NAME.GLOBE,
    titleKey: "step_catalog_title",
    bodyKey: "step_catalog_body",
    ctaKey: "browse_catalog",
  },
  analysis: {
    icon: ICON_NAME.CHART,
    titleKey: "run_first_analysis_title",
    bodyKey: "run_first_analysis_body",
    ctaKey: "pick_a_template",
  },
  workflow: {
    icon: ICON_NAME.WORKFLOW,
    titleKey: "build_workflow_title",
    bodyKey: "build_workflow_body",
    ctaKey: "pick_a_workflow",
  },
  team: {
    icon: ICON_NAME.USERS,
    titleKey: "step_team_title",
    bodyKey: "step_team_body",
    ctaKey: "invite_people",
  },
};

/** The action a checklist step's call-to-action runs, resolved by the
 * caller (`SetupChecklist` on Home, `OnboardingTray` in the header) since
 * each mounts its own copy of `useHomeCreate` and router. `openTemplates`
 * covers both template steps: called with no kind for "analysis" (the
 * caller prefers a GOAT template with sample data), `"workflow"` for
 * "workflow" (the caller locks the browser to that kind). */
export const runSetupStep = (
  step: SetupStepId,
  actions: {
    newProject: () => void;
    addDataset: () => void;
    browseCatalog: () => void;
    goToTeam: () => void;
    openTemplates: (kind?: TemplateKind) => void;
  }
): void => {
  if (step === "project") actions.newProject();
  else if (step === "data") actions.addDataset();
  else if (step === "catalog") actions.browseCatalog();
  else if (step === "analysis") actions.openTemplates();
  else if (step === "workflow") actions.openTemplates("workflow");
  else actions.goToTeam();
};

/**
 * The three Home stages (H2): derived from the caller's onboarding facts and
 * stored preferences on every render, not from a progress flag that could
 * still say "done" after the content it was tracking is gone.
 *
 * - New: no project and no reachable dataset (uploaded or from the catalog).
 * - Established: onboarding skipped, or every checklist step already done.
 * - Getting started: anything in between.
 */
export const useHomeStage = (): {
  /** `undefined` until both requests are in — reading facts before they
   * arrive would say "new" for every caller for one render, flashing the
   * wrong hero before the real stage is known. */
  stage: HomeStage | undefined;
  isLoading: boolean;
  /** Raw facts, for callers that gate on one fact directly (e.g. "Get some
   * data in" hides once either kind of dataset exists) rather than on the
   * derived stage or step list. */
  facts: OnboardingFacts | undefined;
  done: SetupStepId[];
  skipped: boolean;
  skip: () => Promise<void>;
  refresh: () => void;
} => {
  const { facts, isLoading: factsLoading, isError: factsError, mutate: mutateFacts } = useOnboardingFacts();
  const { preferences, isLoading: preferencesLoading, mutate: mutatePreferences } = usePreferences();

  const isLoading = factsLoading || preferencesLoading;

  const done = SETUP_STEPS.filter((step) => Boolean(facts?.[FACT_FOR_STEP[step]]));
  const skipped = Boolean(preferences?.onboarding_skipped_at);

  let stage: HomeStage | undefined;
  if (!isLoading) {
    if (factsError) {
      // Facts failed to load: "established" is the superset stage (no
      // checklist, no setup nudges), so a broken onboarding endpoint doesn't
      // strand every caller on the "new" empty-state hero instead.
      stage = "established";
    } else {
      const nothingYet = !facts?.has_project && !facts?.has_uploaded_layer && !facts?.has_catalog_layer;
      if (nothingYet) {
        stage = "new";
      } else if (skipped || done.length === SETUP_STEPS.length) {
        stage = "established";
      } else {
        stage = "getting_started";
      }
    }
  }

  const skip = async () => {
    await patchPreferences({ onboarding_skipped_at: new Date().toISOString() });
    await mutatePreferences();
  };

  const refresh = () => {
    void mutateFacts();
    void mutatePreferences();
  };

  return { stage, isLoading, facts, done, skipped, skip, refresh };
};
