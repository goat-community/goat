import { languages } from "@/app/i18/settings";
import Image from "next/image";
import Link from "next/link";
import { v4 } from "uuid";

export const TranslationSwitcher = ({ lng }: { lng: string }) => {
  return (
    <div>
      {languages
        .filter((l) => lng !== l)
        .map((l, index) => {
          return (
            <span key={v4()}>
              {index > 0 && " or "}
              <Link href={`/${l}/home`} style={{ display: "flex" }}>
                <Image src={`/assets/languages/${l}.png`} alt={l} width={20} height={20} />
              </Link>
            </span>
          );
        })}
    </div>
  );
};
