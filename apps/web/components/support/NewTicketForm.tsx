"use client";

import { LoadingButton } from "@mui/lab";
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  ButtonBase,
  Checkbox,
  Chip,
  CircularProgress,
  FormControl,
  FormControlLabel,
  Stack,
  TextField,
  Typography,
  alpha,
  useTheme,
} from "@mui/material";
import type { SxProps, Theme } from "@mui/material";
import { notFound, useRouter, useSearchParams } from "next/navigation";
import { type KeyboardEvent, useEffect, useId, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "react-toastify";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import { useContent, useSpaces } from "@/lib/api/content";
import {
  createSupportTicket,
  findSupportTicketByRequestId,
  useSupportColleagues,
  useSupportSummary,
} from "@/lib/api/support";
import { useUserProfile } from "@/lib/api/users";
import { EMPTY_DRAFT, type NewTicketDraft, sanitizeDraft, sanitizeFrom } from "@/lib/support/draft";
import { supportErrorMessage } from "@/lib/support/errors";
import { newRequestId } from "@/lib/support/requestId";
import { spaceDisplayName } from "@/lib/utils/content";
import type { ContentItem } from "@/lib/validations/content";
import { SUPPORT_CATEGORIES, SUPPORT_IMPACTS, type SupportCategory } from "@/lib/validations/support";

import { useDebouncedValue } from "@/hooks/dashboard/home/useDebouncedValue";
import { useDraft } from "@/hooks/support/useDraft";

import FormLabelHelper from "@/components/common/FormLabelHelper";
import PageHeader from "@/components/dashboard/common/PageHeader";
import SurfaceCard from "@/components/dashboard/common/SurfaceCard";
import UserAvatar from "@/components/dashboard/common/UserAvatar";
import TextFieldInput from "@/components/map/panels/common/TextFieldInput";
import FilePicker from "@/components/support/FilePicker";
import { BackLink, CATEGORY_ICON, SupportPage, useSupportMobile } from "@/components/support/SupportChrome";

export const SUBMIT_TIMEOUT_MS = 20_000;
/** Assumed worst-case upload speed (~0.8 Mbit/s) the request may need on top of the base timeout. */
export const UPLOAD_BYTES_PER_SECOND = 100_000;
/** Core's limits for the text fields. */
export const DESCRIPTION_MAX_LENGTH = 20_000;
export const MAX_COLLEAGUES = 20;
/** How many projects the picker fetches per search, last opened first (as in the Use template flow). */
const PROJECT_PICKER_PAGE_SIZE = 50;
/** The form keeps a readable line length instead of spanning the page's full `xl` measure. */
const FORM_MAX_WIDTH = 880;

/** The base timeout plus the time the files need to upload: 50 MB gets about 8.7 minutes in total. */
export const submitTimeoutMs = (files: File[]): number => {
  const bytes = files.reduce((sum, f) => sum + f.size, 0);
  return SUBMIT_TIMEOUT_MS + Math.ceil((bytes / UPLOAD_BYTES_PER_SECOND) * 1000);
};
export const CHECK_INTERVAL_MS = 10_000;
export const CHECK_ATTEMPTS = 12;

// "done": the ticket exists and the page is moving on to it.
type Phase = "editing" | "sending" | "checking" | "unconfirmed" | "done";

type RadioOption<T extends string> = { value: T; title: string; desc: string; icon?: ICON_NAME };

/** Single choice as a radiogroup of selectable `SurfaceCard` tiles: one tab stop (selected, else first), arrow keys move the selection. */
const RadioCards = <T extends string>({
  labelId,
  describedBy,
  options,
  value,
  onChange,
  invalid,
  indicator,
  sx,
}: {
  labelId: string;
  describedBy?: string;
  options: RadioOption<T>[];
  value: T | null;
  onChange: (value: T) => void;
  /** Tried to submit without a choice: the tiles take the error border. */
  invalid?: boolean;
  /** Leads each tile with a radio dot instead of the option's icon. */
  indicator?: boolean;
  sx: SxProps<Theme>;
}) => {
  const theme = useTheme();
  const group = useRef<HTMLDivElement>(null);
  const onKeyDown = (e: KeyboardEvent, index: number) => {
    const step = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key];
    if (!step) return;
    e.preventDefault();
    const next = (index + step + options.length) % options.length;
    onChange(options[next].value);
    group.current?.querySelectorAll<HTMLElement>('[role="radio"]')[next]?.focus();
  };
  const selectedIndex = options.findIndex((o) => o.value === value);
  return (
    <Box ref={group} role="radiogroup" aria-labelledby={labelId} aria-describedby={describedBy} sx={sx}>
      {options.map((o, i) => {
        const selected = o.value === value;
        const accent = selected ? theme.palette.primary.main : theme.palette.text.secondary;
        return (
          <SurfaceCard
            key={o.value}
            selected={selected}
            sx={{
              display: "flex",
              boxShadow: selected ? undefined : "none",
              ...(invalid && !selected && { borderColor: theme.palette.error.main }),
            }}>
            <ButtonBase
              role="radio"
              aria-checked={selected}
              tabIndex={selected || (selectedIndex < 0 && i === 0) ? 0 : -1}
              onClick={() => onChange(o.value)}
              onKeyDown={(e) => onKeyDown(e, i)}
              sx={{
                flex: 1,
                display: "flex",
                alignItems: "flex-start",
                justifyContent: "flex-start",
                gap: "10px",
                textAlign: "left",
                padding: "11px 12px",
                borderRadius: "11px",
                fontFamily: "inherit",
                "&.Mui-focusVisible": {
                  outline: `2px solid ${theme.palette.primary.main}`,
                  outlineOffset: 2,
                },
              }}>
              {indicator ? (
                <Box
                  aria-hidden
                  sx={{
                    width: 16,
                    height: 16,
                    mt: "1px",
                    flexShrink: 0,
                    borderRadius: "50%",
                    border: `2px solid ${selected ? accent : alpha(theme.palette.text.primary, 0.3)}`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}>
                  {selected && <Box sx={{ width: 8, height: 8, borderRadius: "50%", bgcolor: accent }} />}
                </Box>
              ) : (
                o.icon && (
                  <Icon
                    iconName={o.icon}
                    style={{ fontSize: 15, marginTop: 2, flexShrink: 0 }}
                    htmlColor={accent}
                  />
                )
              )}
              <Box sx={{ minWidth: 0 }}>
                <Typography
                  component="span"
                  sx={{
                    display: "block",
                    fontSize: 13.5,
                    fontWeight: 700,
                    lineHeight: 1.35,
                    color: selected ? "primary.main" : "text.primary",
                  }}>
                  {o.title}
                </Typography>
                <Typography
                  component="span"
                  sx={{
                    display: "block",
                    fontSize: 12,
                    lineHeight: 1.4,
                    color: "text.secondary",
                    mt: "2px",
                  }}>
                  {o.desc}
                </Typography>
              </Box>
            </ButtonBase>
          </SurfaceCard>
        );
      })}
    </Box>
  );
};

/** A section's heading in the dialogs' field style (`FormLabelHelper`, muted, above the field).
 * `id` names a group through `aria-labelledby`; an optional field says so in brackets. */
const FieldLabel = ({
  id,
  children,
  required,
  optional,
}: {
  id?: string;
  children: string;
  required?: boolean;
  optional?: string;
}) => {
  const theme = useTheme();
  return (
    <Box id={id}>
      <FormLabelHelper
        label={`${children}${required ? " *" : ""}${optional ? ` (${optional})` : ""}`}
        color={theme.palette.text.secondary}
      />
    </Box>
  );
};

/** A project's thumbnail in the compact size the project field's rows and value use. */
const ProjectThumbnail = ({ project }: { project: ContentItem }) => {
  const theme = useTheme();
  return (
    <Box
      aria-hidden
      sx={{
        width: 28,
        height: 20,
        flexShrink: 0,
        borderRadius: "4px",
        backgroundColor: alpha(theme.palette.text.primary, 0.08),
        backgroundImage: project.thumbnail_url ? `url(${project.thumbnail_url})` : undefined,
        backgroundSize: "cover",
        backgroundPosition: "center",
      }}
    />
  );
};

/** The small error line under a field, as the radio groups show it. */
const FieldError = ({ id, children }: { id: string; children: string }) => (
  <Typography id={id} variant="caption" color="error" component="div" sx={{ mt: "6px" }}>
    {children}
  </Typography>
);

/** Outlines a `TextFieldInput` in the error colour; it has no error prop of its own. */
const invalidOutline = (invalid: boolean): SxProps<Theme> => ({
  // TextFieldInput leaves its unfocused label colour to `inherit`, so this box sets the house secondary.
  color: "text.secondary",
  ...(invalid && {
    "& .MuiOutlinedInput-notchedOutline, & .MuiOutlinedInput-root:hover .MuiOutlinedInput-notchedOutline": {
      borderColor: "error.main",
    },
  }),
});

const NewTicketForm = () => {
  const { t } = useTranslation("common");
  const theme = useTheme();
  const mobile = useSupportMobile();
  const router = useRouter();
  const params = useSearchParams();
  const { colleagues } = useSupportColleagues();
  const { spaces } = useSpaces();
  const { userProfile } = useUserProfile();
  const { notConfigured } = useSupportSummary();
  // Per user, so a draft never shows up for someone else on a shared browser; no key until the user is known.
  const [stored, setDraft, clearDraft] = useDraft<NewTicketDraft>(
    userProfile?.id ? `new:${userProfile.id}` : null,
    EMPTY_DRAFT
  );
  const draft = useMemo(() => sanitizeDraft(stored), [stored]);
  const requestId = useRef("");
  const categoryLabelId = useId();
  const categoryErrorId = useId();
  const impactLabelId = useId();
  const impactHintId = useId();
  const subjectErrorId = useId();
  const descriptionErrorId = useId();
  const mounted = useRef(true);
  const [files, setFiles] = useState<File[]>([]);
  const [colleagueIds, setColleagueIds] = useState<string[]>([]);
  const [project, setProject] = useState<ContentItem | null>(null);
  // What is typed in the project field (shown as is) and the debounced text the server filters by.
  const [projectInput, setProjectInput] = useState("");
  const [projectFocused, setProjectFocused] = useState(false);
  const [projectQuery, setProjectQuery] = useState("");
  const debouncedProjectQuery = useDebouncedValue(projectQuery, 250);
  const [colleaguesFocused, setColleaguesFocused] = useState(false);
  const [technical, setTechnical] = useState(true);
  const [tried, setTried] = useState(false);
  const [phase, setPhase] = useState<Phase>("editing");
  const [error, setError] = useState<string | null>(null);
  const sending = useRef(false);

  const needsImpact = draft.category !== null && draft.category !== "feature_request";
  const errors = {
    category: !draft.category,
    subject: draft.subject.trim().length < 3,
    description: draft.description.trim().length < 1,
    impact: needsImpact && !draft.impact,
  };
  const valid = !Object.values(errors).some(Boolean);

  // The project is not asked for on account & billing tickets, so nothing is fetched there.
  const projectPicker = draft.category !== "account_billing";
  const {
    page: projectPage,
    isLoading: projectsLoading,
    isValidating: projectsValidating,
  } = useContent(
    projectPicker
      ? {
          view: "recent",
          types: "project",
          order_by: "last_opened_at",
          search: debouncedProjectQuery.trim() || undefined,
          size: PROJECT_PICKER_PAGE_SIZE,
        }
      : null
  );
  const projects = useMemo(() => projectPage?.items ?? [], [projectPage]);
  // The chosen project stays an option while a search filters it out of the list.
  const projectOptions = useMemo(
    () => (project && !projects.some((p) => p.id === project.id) ? [project, ...projects] : projects),
    [projects, project]
  );

  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
    };
  }, []);

  // A late success (the user left while the request was in flight) still clears the draft and tells them.
  const opened = (ref: string, failed: string[] = []) => {
    // Keep the fields on screen until the ticket page opens: clearing them here would show an
    // empty form, with every required field flagged, for the moment the navigation takes.
    clearDraft({ keepValue: true });
    if (mounted.current) setPhase("done");
    toast.success(t("support_created", { ref }));
    if (failed.length) toast.warning(t("support_failed_files", { files: failed.join(", ") }));
    if (mounted.current) router.push(`/support/${ref}`);
  };
  const openedRef = useRef(opened);
  openedRef.current = opened;

  // After a timeout: ask for the request id instead of offering a retry. One lookup at a time.
  useEffect(() => {
    if (phase !== "checking") return;
    const id = requestId.current;
    let cancelled = false;
    let attempts = 0;
    let timer: ReturnType<typeof setTimeout>;
    const poll = async () => {
      attempts += 1;
      try {
        const found = await findSupportTicketByRequestId(id);
        if (cancelled) return;
        if (found) {
          openedRef.current(found.ref);
          return;
        }
      } catch {
        // still unreachable; keep trying
      }
      if (cancelled) return;
      if (attempts >= CHECK_ATTEMPTS) {
        setPhase("unconfirmed");
        return;
      }
      timer = setTimeout(poll, CHECK_INTERVAL_MS);
    };
    timer = setTimeout(poll, CHECK_INTERVAL_MS);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [phase]);

  const submit = async () => {
    setTried(true);
    if (!valid || sending.current) return;
    sending.current = true;
    // Keep the id with the draft: after a timeout and a reload, the same submit is recognised by the server.
    requestId.current = draft.requestId || newRequestId();
    if (!draft.requestId) setDraft({ ...draft, requestId: requestId.current });
    setPhase("sending");
    setError(null);
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), submitTimeoutMs(files));
    const details: Record<string, string> = {};
    if (technical) {
      details["Page"] = sanitizeFrom(params.get("from"), window.location.origin);
      details["Browser"] = navigator.userAgent;
      details["Screen"] = `${window.innerWidth}×${window.innerHeight}`;
      details["Language"] = navigator.language;
    }
    if (project && projectPicker) details["Project"] = `${project.name} (${project.id})`;
    try {
      const result = await createSupportTicket(
        {
          subject: draft.subject,
          description: draft.description,
          category: draft.category as SupportCategory,
          impact: needsImpact ? draft.impact : null,
          requestId: requestId.current,
          colleagueIds,
          technical: details,
        },
        files,
        controller.signal
      );
      opened(result.ref, result.failed_files);
    } catch (e) {
      if (e instanceof DOMException && e.name === "AbortError") {
        setPhase("checking");
        return;
      }
      sending.current = false;
      setPhase("editing");
      setError(supportErrorMessage(t, e));
    } finally {
      clearTimeout(timeout);
    }
  };

  // Support is switched off on this installation: behave like a page that does not exist.
  if (notConfigured) notFound();

  const placeholder =
    draft.category === "bug" ? t("support_placeholder_bug") : t("support_placeholder_default");
  const required = (bad: boolean) => (tried && bad && phase !== "done" ? t("support_required") : undefined);

  const footerButtons = (
    <>
      <Button
        variant="text"
        onClick={() => router.push("/support")}
        disabled={phase === "checking"}
        sx={{ textTransform: "none", fontWeight: 700 }}>
        {t("support_cancel")}
      </Button>
      {(phase === "editing" || phase === "sending" || phase === "done") && (
        <LoadingButton
          variant="contained"
          onClick={submit}
          loading={phase === "sending" || phase === "done"}
          sx={{ textTransform: "none", fontWeight: 700, flex: mobile ? 1 : undefined }}>
          {t("support_submit")}
        </LoadingButton>
      )}
    </>
  );

  return (
    <SupportPage mobile={mobile} maxWidth={FORM_MAX_WIDTH}>
      <BackLink
        label={t("support_title")}
        onClick={() => router.push("/support")}
        disabled={phase === "checking"}
      />
      <Box sx={{ mt: "6px", mb: mobile ? "16px" : 6 }}>
        <PageHeader title={t("support_new_title")} subtitle={t("support_new_subtitle")} mobile={mobile} />
      </Box>

      <Box>
        {(phase === "checking" || phase === "unconfirmed" || error) && (
          <Stack spacing="12px" sx={{ mb: 4 }}>
            {phase === "checking" && (
              <Alert severity="info" icon={<CircularProgress size={18} />}>
                {t("support_checking")}
              </Alert>
            )}
            {phase === "unconfirmed" && (
              <Alert
                severity="warning"
                action={
                  <Button
                    color="inherit"
                    size="small"
                    sx={{ textTransform: "none", fontWeight: 700 }}
                    onClick={() => router.push("/support")}>
                    {t("support_tickets")}
                  </Button>
                }>
                {t("support_not_confirmed")}
              </Alert>
            )}
            {error && <Alert severity="error">{error}</Alert>}
          </Stack>
        )}

        <SurfaceCard hoverable={false} sx={{ overflow: "hidden" }}>
          <Stack spacing={mobile ? "24px" : 4} sx={{ p: mobile ? "16px" : "24px" }}>
            <Box>
              <FieldLabel id={categoryLabelId} required>
                {t("support_field_category")}
              </FieldLabel>
              <RadioCards
                labelId={categoryLabelId}
                describedBy={required(errors.category) ? categoryErrorId : undefined}
                options={SUPPORT_CATEGORIES.map((c) => ({
                  value: c,
                  title: t(`support_category_${c}`),
                  desc: t(`support_category_${c}_desc`),
                  // A phone's two columns have no room for the glyph next to the text.
                  icon: mobile ? undefined : CATEGORY_ICON[c],
                }))}
                value={draft.category}
                onChange={(category) => setDraft({ ...draft, category })}
                invalid={Boolean(required(errors.category))}
                sx={{
                  display: "grid",
                  gap: "8px",
                  gridTemplateColumns: mobile
                    ? "repeat(2, minmax(0, 1fr))"
                    : "repeat(auto-fill, minmax(190px, 1fr))",
                }}
              />
              {required(errors.category) && (
                <Typography
                  id={categoryErrorId}
                  variant="caption"
                  color="error"
                  component="div"
                  sx={{ mt: "6px" }}>
                  {t("support_required")}
                </Typography>
              )}
            </Box>

            <Box>
              <Box sx={invalidOutline(Boolean(required(errors.subject)))}>
                <TextFieldInput
                  label={`${t("support_field_subject")} *`}
                  value={draft.subject}
                  onChange={(subject) => setDraft({ ...draft, subject })}
                  placeholder={t("support_subject_placeholder")}
                  inputProps={{
                    maxLength: 200,
                    "aria-label": t("support_field_subject"),
                    "aria-required": true,
                    "aria-invalid": Boolean(required(errors.subject)),
                    "aria-describedby": required(errors.subject) ? subjectErrorId : undefined,
                  }}
                />
              </Box>
              {required(errors.subject) && (
                <FieldError id={subjectErrorId}>{t("support_required")}</FieldError>
              )}
            </Box>

            <Box>
              <Box sx={invalidOutline(Boolean(required(errors.description)))}>
                <TextFieldInput
                  label={`${t("support_field_description")} *`}
                  multiline
                  rows={7}
                  clearable={false}
                  value={draft.description}
                  onChange={(description) => setDraft({ ...draft, description })}
                  placeholder={placeholder}
                  inputProps={{
                    maxLength: DESCRIPTION_MAX_LENGTH,
                    "aria-label": t("support_field_description"),
                    "aria-required": true,
                    "aria-invalid": Boolean(required(errors.description)),
                    "aria-describedby": required(errors.description) ? descriptionErrorId : undefined,
                  }}
                />
              </Box>
              {required(errors.description) && (
                <FieldError id={descriptionErrorId}>{t("support_required")}</FieldError>
              )}
            </Box>

            {needsImpact && (
              <Box>
                <FieldLabel id={impactLabelId} required>
                  {t("support_field_impact")}
                </FieldLabel>
                <RadioCards
                  labelId={impactLabelId}
                  describedBy={impactHintId}
                  indicator
                  options={SUPPORT_IMPACTS.map((i) => ({
                    value: i,
                    title: t(`support_impact_${i}`),
                    desc: t(`support_impact_${i}_desc`),
                  }))}
                  value={draft.impact}
                  onChange={(impact) => setDraft({ ...draft, impact })}
                  invalid={Boolean(required(errors.impact))}
                  sx={{
                    display: "grid",
                    gap: "8px",
                    gridTemplateColumns: mobile ? "minmax(0, 1fr)" : "repeat(auto-fit, minmax(180px, 1fr))",
                  }}
                />
                <Typography
                  id={impactHintId}
                  variant="caption"
                  component="div"
                  sx={{ mt: "6px" }}
                  color={required(errors.impact) ? "error" : "text.secondary"}>
                  {required(errors.impact) ?? t("support_impact_hint")}
                </Typography>
              </Box>
            )}

            {projectPicker && (
              <FormControl size="small" fullWidth>
                <FormLabelHelper
                  label={`${t("support_field_project")} (${t("support_optional")})`}
                  color={projectFocused ? theme.palette.primary.main : theme.palette.text.secondary}
                />
                <Autocomplete
                  size="small"
                  options={projectOptions}
                  value={project}
                  // Any project the user can see may be referenced, view-only ones included.
                  onChange={(_, value) => setProject(value)}
                  inputValue={projectInput}
                  onInputChange={(_, value, reason) => {
                    setProjectInput(value);
                    // Only typing searches; picking or clearing returns the list to the full set.
                    setProjectQuery(reason === "input" ? value : "");
                  }}
                  getOptionLabel={(p) => p.name}
                  isOptionEqualToValue={(a, b) => a.id === b.id}
                  // The server filters by the typed text.
                  filterOptions={(x) => x}
                  loading={projectsLoading || projectsValidating}
                  loadingText={t("loading")}
                  noOptionsText={projectQuery.trim() ? t("no_projects_found") : t("no_projects_yet")}
                  clearText={t("clear")}
                  onFocus={() => setProjectFocused(true)}
                  onBlur={() => setProjectFocused(false)}
                  renderOption={(props, p) => {
                    const { key, ...optionProps } = props as typeof props & { key?: string };
                    return (
                      <Box component="li" key={key ?? p.id} {...optionProps} sx={{ gap: "10px" }}>
                        <ProjectThumbnail project={p} />
                        <Box sx={{ minWidth: 0 }}>
                          <Typography noWrap sx={{ fontSize: 13, fontWeight: 600 }}>
                            {p.name}
                          </Typography>
                          <Typography noWrap sx={{ fontSize: 11.5, color: "text.secondary" }}>
                            {spaceDisplayName(
                              spaces.find((space) => space.id === p.space_id),
                              t
                            )}
                          </Typography>
                        </Box>
                      </Box>
                    );
                  }}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      placeholder={t("search_projects")}
                      inputProps={{
                        ...params.inputProps,
                        "aria-label": `${t("support_field_project")} (${t("support_optional")})`,
                      }}
                      InputProps={{
                        ...params.InputProps,
                        startAdornment: project ? (
                          <Box sx={{ display: "flex", ml: "4px", mr: "2px" }}>
                            <ProjectThumbnail project={project} />
                          </Box>
                        ) : (
                          params.InputProps.startAdornment
                        ),
                      }}
                      sx={{
                        "& .MuiAutocomplete-inputRoot": { minHeight: "40px", fontSize: "0.875rem" },
                        "& input": { fontSize: "0.875rem" },
                        "& input::placeholder": { fontSize: "0.875rem" },
                      }}
                    />
                  )}
                />
              </FormControl>
            )}

            <Box>
              <FieldLabel optional={t("support_optional")}>{t("support_field_files")}</FieldLabel>
              <Typography
                component="div"
                sx={{ fontSize: 12.5, color: "text.secondary", mt: "-4px", mb: "8px", lineHeight: 1.45 }}>
                {t("support_files_hint")}
              </Typography>
              <FilePicker files={files} onChange={setFiles} />
            </Box>

            <FormControl size="small" fullWidth>
              <FormLabelHelper
                label={`${t("support_field_colleagues")} (${t("support_optional")})`}
                color={colleaguesFocused ? theme.palette.primary.main : theme.palette.text.secondary}
              />
              <Autocomplete
                multiple
                size="small"
                options={colleagues}
                getOptionLabel={(c) => `${c.name} (${c.email})`}
                value={colleagues.filter((c) => colleagueIds.includes(c.user_id))}
                onChange={(_, value) => setColleagueIds(value.map((c) => c.user_id))}
                getOptionDisabled={(c) =>
                  colleagueIds.length >= MAX_COLLEAGUES && !colleagueIds.includes(c.user_id)
                }
                onFocus={() => setColleaguesFocused(true)}
                onBlur={() => setColleaguesFocused(false)}
                renderTags={(value, getTagProps) =>
                  value.map((c, index) => {
                    const { key, ...tagProps } = getTagProps({ index });
                    return (
                      <Chip
                        key={key}
                        size="small"
                        label={c.name}
                        title={c.email}
                        avatar={<UserAvatar id={c.user_id} name={c.name} size={18} />}
                        {...tagProps}
                      />
                    );
                  })
                }
                renderInput={(params) => (
                  <TextField
                    {...params}
                    inputProps={{
                      ...params.inputProps,
                      "aria-label": `${t("support_field_colleagues")} (${t("support_optional")})`,
                    }}
                    sx={{
                      "& .MuiAutocomplete-inputRoot": { minHeight: "40px", fontSize: "0.875rem" },
                      "& input": { fontSize: "0.875rem" },
                      "& input::placeholder": { fontSize: "0.875rem" },
                    }}
                  />
                )}
              />
              <Typography
                component="div"
                sx={{ fontSize: 12.5, color: "text.secondary", mt: "6px", lineHeight: 1.45 }}>
                {t("support_colleagues_hint")}
              </Typography>
            </FormControl>

            <FormControlLabel
              sx={{ alignItems: "flex-start", ml: "-9px", mr: 0 }}
              control={
                <Checkbox
                  checked={technical}
                  onChange={(e) => setTechnical(e.target.checked)}
                  sx={{ mt: "-7px" }}
                />
              }
              label={
                <Box>
                  <Typography component="div" sx={{ fontSize: 13.5, fontWeight: 700 }}>
                    {t("support_technical")}
                  </Typography>
                  <Typography component="div" sx={{ fontSize: 12.5, color: "text.secondary", mt: "2px" }}>
                    {t("support_technical_hint")}
                  </Typography>
                </Box>
              }
            />
          </Stack>

          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              flexWrap: "wrap",
              gap: mobile ? "12px" : "8px",
              px: mobile ? "16px" : "24px",
              py: "14px",
              borderTop: `1px solid ${theme.palette.divider}`,
              backgroundColor: theme.palette.action.hover,
            }}>
            <Stack
              direction="row"
              spacing="8px"
              alignItems="flex-start"
              sx={{ flex: mobile ? "1 1 100%" : "1 1 260px", minWidth: 0, color: "text.secondary" }}>
              <Icon iconName={ICON_NAME.LOCK} style={{ fontSize: 12, marginTop: 3 }} htmlColor="inherit" />
              <Typography sx={{ fontSize: 12.5, lineHeight: 1.5 }}>{t("support_visibility_note")}</Typography>
            </Stack>
            {mobile ? (
              <Stack direction="row" spacing="8px" sx={{ width: "100%" }}>
                {footerButtons}
              </Stack>
            ) : (
              footerButtons
            )}
          </Box>
        </SurfaceCard>
      </Box>
    </SupportPage>
  );
};

export default NewTicketForm;
