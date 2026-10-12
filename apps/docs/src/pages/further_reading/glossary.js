import React, { useEffect } from "react";
import Head from "@docusaurus/Head";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";

// The glossary moved to the Plan4Better website. This page keeps the old
// docs address working by sending visitors on to it in their language.
const GLOSSARY = {
  en: "https://www.plan4better.de/en/glossary",
  de: "https://www.plan4better.de/de/glossar",
};

export default function GlossaryRedirect() {
  const { i18n } = useDocusaurusContext();
  const target = GLOSSARY[i18n.currentLocale] || GLOSSARY.en;

  useEffect(() => {
    window.location.replace(target);
  }, [target]);

  return (
    <>
      <Head>
        <meta httpEquiv="refresh" content={`0; url=${target}`} />
        <meta name="robots" content="noindex" />
        <link rel="canonical" href={target} />
      </Head>
      <p style={{ padding: "2rem" }}>
        <a href={target}>{target}</a>
      </p>
    </>
  );
}
