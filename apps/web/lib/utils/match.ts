/* eslint-disable @typescript-eslint/no-explicit-any */
import removeDiacritics from "remove-accents";

const specialCharsRegex = /[.*+?^${}()|[\]\\]/g;
const wordCharacterRegex = /[a-z0-9_]/i;
const whitespacesRegex = /\s+/;

function escapeRegexCharacters(str: string): string {
  return str.replace(specialCharsRegex, "\\$&");
}

interface MatchOptions {
  insideWords?: boolean;
  findAllOccurrences?: boolean;
  requireMatchAll?: boolean;
}

function extend(subject: any, baseObject: any): any {
  subject = subject || {};
  Object.keys(subject).forEach((key) => {
    baseObject[key] = !!subject[key];
  });
  return baseObject;
}

export function match(text: string, query: string, options: MatchOptions = {}) {
  options = extend(options, {
    insideWords: false,
    findAllOccurrences: false,
    requireMatchAll: false,
  });

  const cleanedTextArray = Array.from(text).map((x) => removeDiacritics(x));
  let cleanedText = cleanedTextArray.join("");

  query = removeDiacritics(query);

  return query
    .trim()
    .split(whitespacesRegex)
    .filter((word) => word.length > 0)
    .reduce((result: any, word: string) => {
      const wordLen = word.length;
      const prefix = !options.insideWords && wordCharacterRegex.test(word[0]) ? "\\b" : "";
      const regex = new RegExp(prefix + escapeRegexCharacters(word), "i");
      let occurrence;
      let index;

      occurrence = regex.exec(cleanedText);
      if (options.requireMatchAll && occurrence === null) {
        cleanedText = "";
        return [];
      }

      while (occurrence) {
        index = occurrence.index;

        const cleanedLength = cleanedTextArray.slice(index, index + wordLen).join("").length;
        const offset = wordLen - cleanedLength;

        const initialOffset = index - cleanedTextArray.slice(0, index).join("").length;

        const indexes = [index + initialOffset, index + wordLen + initialOffset + offset];

        if (indexes[0] !== indexes[1]) {
          result.push(indexes);
        }

        cleanedText =
          cleanedText.slice(0, index) + new Array(wordLen + 1).join(" ") + cleanedText.slice(index + wordLen);

        if (!options.findAllOccurrences) {
          break;
        }

        occurrence = regex.exec(cleanedText);
      }

      return result;
    }, [])
    .sort((match1, match2) => match1[0] - match2[0]);
}
