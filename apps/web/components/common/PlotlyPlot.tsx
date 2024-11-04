import dynamic from "next/dynamic";
import * as deLocale from "plotly.js/lib/locales/de.js";
import type { PlotParams } from "react-plotly.js";

/**
 * Dynamic import as a workaround to use Plotly in Next.js
 * see: https://github.com/plotly/react-plotly.js/issues/272
 */
const Plotly = dynamic(
  () =>
    import("react-plotly.js").then((Plotly) => {
      return Plotly;
    }),
  { ssr: false }
);

export const Plot = ({ ...props }: PlotParams) => {
  return (
    <div style={{ width: "100%", height: "100%" }}>
      <Plotly
        useResizeHandler
        {...props}
        layout={{
          autosize: true,
          ...props.layout,
        }}
        style={{
          width: "100%",
          height: "100%",
          ...props.style,
        }}
        config={{
          locales: { de: deLocale },
          ...props.config,
        }}
      />
    </div>
  );
};
