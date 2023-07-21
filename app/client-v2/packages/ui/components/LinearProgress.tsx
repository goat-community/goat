import { LinearProgress as MUILinearProgress } from "@mui/material";
import Box from "@mui/material/Box";
import * as React from "react";

interface LinearProgress {
  finished: (value: boolean) => void;
  defaultValue?: number;
}

export default function LinearProgress(props: LinearProgress) {
  const { finished, defaultValue } = props;

  // Component States
  const [progress, setProgress] = React.useState<number>(0);

  React.useEffect(() => {
    if (!defaultValue) {
      const timer = setInterval(() => {
        setProgress((oldProgress) => {
          const diff = Math.random() * 10;
          if (oldProgress === 100) {
            finished(true);
          }
          return Math.min(oldProgress + diff, 100);
        });
      }, 500);

      return () => {
        clearInterval(timer);
      };
    } else {
      setProgress(defaultValue);
    }
  }, []);

  return (
    <Box sx={{ width: "100%" }}>
      <MUILinearProgress variant="determinate" value={progress} />
    </Box>
  );
}
