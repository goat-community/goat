import { useCallback, useRef, useState } from "react";

// Client-only: the initializer reads localStorage, so use it from client-only or post-mount UI (not SSR-rendered).
const PREFIX = "goat:support:draft:";

const read = <T>(key: string | null, initial: T): T => {
  if (!key) return initial;
  try {
    const raw = localStorage.getItem(PREFIX + key);
    return raw === null ? initial : (JSON.parse(raw) as T);
  } catch {
    return initial;
  }
};

/** A form value kept in localStorage per key, so a draft survives a reload or a lost connection. */
export const useDraft = <T>(
  key: string | null,
  initial: T
): [T, (value: T) => void, (options?: { keepValue?: boolean }) => void] => {
  // `initial` may be a new object on every render; keep the latest in a ref so `clear` stays stable.
  const initialRef = useRef(initial);
  initialRef.current = initial;

  const [state, setState] = useState<{ key: string | null; value: T }>(() => ({
    key,
    value: read(key, initial),
  }));
  let value = state.value;
  if (state.key !== key) {
    // The key changed without a remount (e.g. ticket 31 -> 32): switch to that key's draft.
    value = read(key, initial);
    setState({ key, value });
  }

  const update = useCallback(
    (next: T) => {
      setState({ key, value: next });
      if (!key) return;
      try {
        localStorage.setItem(PREFIX + key, JSON.stringify(next));
      } catch {
        // storage full or blocked: the draft just isn't kept
      }
    },
    [key]
  );
  // `keepValue` forgets the stored draft but leaves the form as it is, for a form that is
  // about to go away (sent, navigating on): resetting it first would flash an empty form.
  const clear = useCallback(
    (options?: { keepValue?: boolean }) => {
      if (!options?.keepValue) setState({ key, value: initialRef.current });
      if (!key) return;
      try {
        localStorage.removeItem(PREFIX + key);
      } catch {
        // ignore
      }
    },
    [key]
  );
  return [value, update, clear];
};
