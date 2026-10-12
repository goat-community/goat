import Link from "@docusaurus/Link";
import { translate } from "@docusaurus/Translate";
import React, { type ReactNode } from "react";

import styles from "./styles.module.css";

type IconName =
  | "start"
  | "workspace"
  | "data"
  | "map"
  | "toolbox"
  | "workflows"
  | "layouts"
  | "dashboard"
  | "sharing"
  | "routing"
  | "tutorials"
  | "help";

// 24×24 line icons, drawn with the current text colour.
const ICON_PATHS: Record<IconName, string[]> = {
  start: ["M12 3.5a8.5 8.5 0 1 1 0 17 8.5 8.5 0 0 1 0-17Z", "m10 8.5 5.5 3.5-5.5 3.5v-7Z"],
  workspace: ["M4 4.5h6.5V11H4zM13.5 4.5H20V11h-6.5zM4 14h6.5v6.5H4zM13.5 14H20v6.5h-6.5z"],
  data: [
    "M5 6.5c0-1.7 3.1-3 7-3s7 1.3 7 3-3.1 3-7 3-7-1.3-7-3Z",
    "M5 6.5v11c0 1.7 3.1 3 7 3s7-1.3 7-3v-11",
    "M5 12c0 1.7 3.1 3 7 3s7-1.3 7-3",
  ],
  map: ["M3.5 6.5 9 4l6 2.5L20.5 4v13.5L15 20l-6-2.5-5.5 2.5z", "M9 4v13.5M15 6.5V20"],
  toolbox: [
    "M3.5 9h17v10.5h-17z",
    "M8.5 9V6.5a2 2 0 0 1 2-2h3a2 2 0 0 1 2 2V9",
    "M3.5 13.5h17M10 12v3M14 12v3",
  ],
  workflows: ["M4 5h5v5H4zM15 14h5v5h-5z", "M9 7.5h3.5a2 2 0 0 1 2 2v4.5", "M4 16.5h5M6.5 14v5"],
  layouts: ["M5.5 3.5h13v17h-13z", "M8.5 7h7v5h-7zM8.5 15h7M8.5 17.5h4"],
  dashboard: ["M4 4h7v9H4zM13 4h7v5h-7zM13 11h7v9h-7zM4 15h7v5H4z"],
  sharing: [
    "M17.5 8.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5ZM6.5 14.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5ZM17.5 20.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5Z",
    "m8.7 10.8 6.6-3.6M8.7 13.2l6.6 3.6",
  ],
  routing: [
    "M6 20.5a2 2 0 1 0 0-4 2 2 0 0 0 0 4ZM18 7.5a2 2 0 1 0 0-4 2 2 0 0 0 0 4Z",
    "M8 18.5h7.5a3 3 0 0 0 0-6h-7a3 3 0 0 1 0-6H16",
  ],
  tutorials: [
    "m2.5 9 9.5-4.5L21.5 9 12 13.5z",
    "M6.5 11v5c1.5 1.5 3.3 2.5 5.5 2.5s4-1 5.5-2.5v-5",
    "M21.5 9v5",
  ],
  help: [
    "M12 3.5a8.5 8.5 0 1 1 0 17 8.5 8.5 0 0 1 0-17Z",
    "M9.6 9.4a2.5 2.5 0 1 1 3.6 2.3c-.8.4-1.2 1-1.2 1.8v.5",
    "M12 16.8v.2",
  ],
};

function Icon({ name }: { name: IconName }): ReactNode {
  return (
    <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
      {ICON_PATHS[name].map((d) => (
        <path
          key={d}
          d={d}
          fill="none"
          stroke="currentColor"
          strokeWidth="1.6"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      ))}
    </svg>
  );
}

type Card = {
  to: string;
  icon: IconName;
  title: string;
  description: string;
};

function useCards(): Card[] {
  return [
    {
      to: "/category/getting-started",
      icon: "start",
      title: translate({ id: "goat.home.card.gettingStarted.title", message: "Getting started" }),
      description: translate({
        id: "goat.home.card.gettingStarted.description",
        message: "Sign up, take the quickstart tour and start a project from a template.",
      }),
    },
    {
      to: "/category/workspace",
      icon: "workspace",
      title: translate({ id: "goat.home.card.workspace.title", message: "Workspace" }),
      description: translate({
        id: "goat.home.card.workspace.description",
        message: "Manage your projects, datasets, teams and settings.",
      }),
    },
    {
      to: "/category/data",
      icon: "data",
      title: translate({ id: "goat.home.card.data.title", message: "Data" }),
      description: translate({
        id: "goat.home.card.data.description",
        message: "Use the built-in datasets or upload and connect your own.",
      }),
    },
    {
      to: "/category/map",
      icon: "map",
      title: translate({ id: "goat.home.card.map.title", message: "Map" }),
      description: translate({
        id: "goat.home.card.map.description",
        message: "Add layers, style them, filter features and measure on the map.",
      }),
    },
    {
      to: "/category/toolbox",
      icon: "toolbox",
      title: translate({ id: "goat.home.card.toolbox.title", message: "Toolbox" }),
      description: translate({
        id: "goat.home.card.toolbox.description",
        message: "Accessibility indicators, geoanalysis, geoprocessing and data management tools.",
      }),
    },
    {
      to: "/category/workflows",
      icon: "workflows",
      title: translate({ id: "goat.home.card.workflows.title", message: "Workflows" }),
      description: translate({
        id: "goat.home.card.workflows.description",
        message: "Chain datasets and tools into analysis pipelines you can run again.",
      }),
    },
    {
      to: "/category/layouts",
      icon: "layouts",
      title: translate({ id: "goat.home.card.layouts.title", message: "Layouts" }),
      description: translate({
        id: "goat.home.card.layouts.description",
        message: "Design map reports and export them as PDF or PNG.",
      }),
    },
    {
      to: "/category/dashboard",
      icon: "dashboard",
      title: translate({ id: "goat.home.card.dashboard.title", message: "Dashboard" }),
      description: translate({
        id: "goat.home.card.dashboard.description",
        message: "Build interactive dashboards with widgets, charts and maps.",
      }),
    },
    {
      to: "/category/sharing",
      icon: "sharing",
      title: translate({ id: "goat.home.card.sharing.title", message: "Sharing" }),
      description: translate({
        id: "goat.home.card.sharing.description",
        message: "Work together in teams or publish public and embedded maps.",
      }),
    },
    {
      to: "/category/routing",
      icon: "routing",
      title: translate({ id: "goat.home.card.routing.title", message: "Routing" }),
      description: translate({
        id: "goat.home.card.routing.description",
        message: "How GOAT computes travel times for walking, cycling, public transport and car.",
      }),
    },
    {
      to: "/tutorials",
      icon: "tutorials",
      title: translate({ id: "goat.home.card.tutorials.title", message: "Tutorials" }),
      description: translate({
        id: "goat.home.card.tutorials.description",
        message: "Step-by-step exercises that walk you through GOAT.",
      }),
    },
    {
      to: "/troubleshooting",
      icon: "help",
      title: translate({ id: "goat.home.card.troubleshooting.title", message: "Troubleshooting" }),
      description: translate({
        id: "goat.home.card.troubleshooting.description",
        message: "Solutions for failed jobs and other common issues.",
      }),
    },
  ];
}

/** The banner at the top of the docs landing page. */
export function DocsHero({ title, children }: { title: string; children?: ReactNode }): ReactNode {
  return (
    <header className={styles.hero}>
      <div className={styles.heroText}>
        <h1 className={styles.heroTitle}>{title}</h1>
        {children && <p className={styles.heroLead}>{children}</p>}
      </div>
      <svg className={styles.heroArt} viewBox="0 0 320 240" aria-hidden="true">
        <g fill="none" strokeLinejoin="round">
          <path
            d="M214 30c52 4 94 44 90 96-3 49-44 92-96 92-54 0-104-38-100-94 4-52 52-98 106-94Z"
            className={styles.ring3}
          />
          <path
            d="M212 62c34 2 62 30 58 64-3 33-30 58-62 58-36 0-66-24-62-60 3-34 32-64 66-62Z"
            className={styles.ring2}
          />
          <path
            d="M210 94c17 1 30 15 28 32-2 16-16 28-31 27-18 0-32-13-30-30 2-16 16-30 33-29Z"
            className={styles.ring1}
          />
        </g>
        <circle cx="208" cy="124" r="6" className={styles.origin} />
      </svg>
    </header>
  );
}

/** The grid of cards linking to the main sections, below the hero. */
export function DocsSectionCards(): ReactNode {
  const cards = useCards();
  return (
    <nav
      className={styles.cards}
      aria-label={translate({ id: "goat.home.cards.label", message: "Documentation sections" })}>
      {cards.map((card) => (
        <Link key={card.to} to={card.to} className={styles.card}>
          <span className={styles.cardIcon}>
            <Icon name={card.icon} />
          </span>
          <span className={styles.cardTitle}>{card.title}</span>
          <span className={styles.cardDescription}>{card.description}</span>
        </Link>
      ))}
    </nav>
  );
}
