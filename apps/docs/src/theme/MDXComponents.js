import React from "react";
import MDXComponents from "@theme-original/MDXComponents";
import { usePluginData } from "@docusaurus/useGlobalData";
import Video from "@site/src/components/Video";
import GlossaryTerm from "@site/src/components/GlossaryTerm";
import { termKey } from "@site/src/glossary/terms";

// A link to a term on the website glossary shows a preview of the term; every
// other link renders as before.
function Link(props) {
  const { terms = {} } = usePluginData("glossary") || {};
  const key = termKey(props.href);
  const term = key ? terms[key] : undefined;
  if (!term) {
    return <MDXComponents.a {...props} />;
  }
  return (
    <GlossaryTerm term={term} href={props.href}>
      {props.children}
    </GlossaryTerm>
  );
}

// Components every docs page can use without importing them.
export default {
  ...MDXComponents,
  a: Link,
  Video,
};
