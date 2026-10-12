/**
 * Text typed into a contentEditable label, as it is stored and shown.
 *
 * Chromium keeps a typed space visible by writing a no-break space (U+00A0)
 * wherever a plain one would collapse, at the end of the text or next to
 * another space, and `textContent` returns it as it is. Stored that way, the
 * words on either side never wrap apart again: a legend title takes an extra
 * line in a narrow legend and pushes the last entry out of the box. Applied to
 * the saved value and to the shown one, so labels saved before also wrap.
 */
export function cleanEditedText(text: string): string {
  return text.replace(/ /g, " ").trim();
}
