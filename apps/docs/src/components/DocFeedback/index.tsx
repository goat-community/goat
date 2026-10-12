import Translate, { translate } from "@docusaurus/Translate";
import { useLocation } from "@docusaurus/router";
import clsx from "clsx";
import React, { type ReactNode, useState } from "react";

import styles from "./styles.module.css";

type Rating = {
  /** Matomo event action. */
  action: string;
  /** Matomo event value, so the average rating of a page can be read off. */
  value: number;
  label: string;
  mouth: string;
};

const MATOMO_CATEGORY = "Docs feedback";

function useRatings(): Rating[] {
  return [
    {
      action: "Not helpful",
      value: 1,
      label: translate({
        id: "goat.feedback.notHelpful",
        message: "Not helpful",
        description: "Feedback face",
      }),
      mouth: "M8.5 16.5c1-1.3 2.2-2 3.5-2s2.5.7 3.5 2",
    },
    {
      action: "Somewhat helpful",
      value: 2,
      label: translate({
        id: "goat.feedback.somewhatHelpful",
        message: "Somewhat helpful",
        description: "Feedback face",
      }),
      mouth: "M8.5 15.5h7",
    },
    {
      action: "Helpful",
      value: 3,
      label: translate({ id: "goat.feedback.helpful", message: "Helpful", description: "Feedback face" }),
      mouth: "M8.5 14.5c1 1.3 2.2 2 3.5 2s2.5-.7 3.5-2",
    },
  ];
}

/** Records the vote as a Matomo event. Does nothing when Matomo was not set up (see `src/matomo.js`). */
function trackVote(rating: Rating, pathname: string): void {
  const paq = (window as unknown as { _paq?: { push?: (command: unknown[]) => void } })._paq;
  if (!paq || typeof paq.push !== "function") {
    return;
  }
  paq.push(["trackEvent", MATOMO_CATEGORY, rating.action, pathname, rating.value]);
}

function Face({ mouth }: { mouth: string }): ReactNode {
  return (
    <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
      <circle cx="12" cy="12" r="9.25" fill="none" stroke="currentColor" strokeWidth="1.5" />
      <circle cx="9" cy="10" r="1.1" fill="currentColor" />
      <circle cx="15" cy="10" r="1.1" fill="currentColor" />
      <path d={mouth} fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}

function DocFeedbackForPage({ className, pathname }: { className?: string; pathname: string }): ReactNode {
  const ratings = useRatings();
  const [voted, setVoted] = useState<Rating | null>(null);

  const vote = (rating: Rating) => {
    if (voted) {
      return;
    }
    setVoted(rating);
    trackVote(rating, pathname);
  };

  return (
    <div className={clsx(styles.feedback, className)}>
      <div className={styles.question} id="doc-feedback-question">
        {voted ? (
          <Translate id="goat.feedback.thanks" description="Shown after a reader rated a doc page">
            Thanks for your feedback!
          </Translate>
        ) : (
          <Translate id="goat.feedback.question" description="Question of the doc page feedback widget">
            Was this helpful?
          </Translate>
        )}
      </div>
      <div className={styles.faces} role="group" aria-labelledby="doc-feedback-question">
        {ratings.map((rating) => (
          <button
            key={rating.action}
            type="button"
            className={clsx(
              styles.face,
              voted?.action === rating.action && styles.selected,
              voted && voted.action !== rating.action && styles.dimmed
            )}
            aria-label={rating.label}
            aria-pressed={voted?.action === rating.action}
            title={rating.label}
            disabled={voted !== null}
            onClick={() => vote(rating)}>
            <Face mouth={rating.mouth} />
          </button>
        ))}
      </div>
    </div>
  );
}

/** "Was this helpful?" with three faces; one vote per page view. */
export default function DocFeedback({ className }: { className?: string }): ReactNode {
  const { pathname } = useLocation();
  // Keyed by page so the widget starts over after client-side navigation.
  return <DocFeedbackForPage key={pathname} className={className} pathname={pathname} />;
}
