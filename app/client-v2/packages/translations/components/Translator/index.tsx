import { Translation } from "react-i18next";

import "../../i18n";

interface TranslatorProps {
  text: string;
}

// Check that i18n already loaded.
// If not, it will be loaded by the Translation component.
export default function Translator({ text }: TranslatorProps) {
  // check if i18n is already initialized
  return <Translation>{(t) => <p>{t(text)}</p>}</Translation>;
}
