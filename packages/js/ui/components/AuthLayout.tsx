import type { SxProps } from "@mui/material";
import { Box } from "@mui/material";
import Grid from "@mui/material/Unstable_Grid2";

import authArtwork from "../assets/img/auth-artwork.png";
import { GOATLogoFullWhite } from "../assets/svg/GOATLogoFullWhite";

/** The URL of a bundled image. The artwork is imported, so each app's bundler
 * ships it with its own build and serves it from wherever that build lives:
 * Next.js yields `{ src }`, Create React App (the Keycloak theme) a string. */
const importedUrl = (image: unknown): string =>
  typeof image === "string" ? image : (image as { src: string }).src;

const ARTWORK_URL = importedUrl(authArtwork);

export default function AuthLayout({
  children,
  sx,
}: {
  children: React.ReactNode;
  sx?: SxProps;
}) {
  return (
    <Box
      component="main"
      sx={{
        display: "flex",
        flex: "1 1 auto",
        ...sx,
      }}
    >
      <Grid
        container
        sx={{
          flex: "1 1 auto",
        }}
      >
        <Grid
          xs={12}
          lg={6}
          sx={{
            height: "100vh",
            display: "flex",
            flexDirection: "column",
            position: "relative",
          }}
        >
          <Box
            component="div"
            sx={{
              flex: "1 1 auto",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              alignItems: "center",
            }}
          >
            {children}
          </Box>
        </Grid>
        <Grid
          xs={12}
          lg={6}
          sx={{
            alignItems: "center",
            background: `radial-gradient(50% 50% at 50% 50%, rgba(40,54,72,0.8) 0%, rgba(40,54,72,0.9) 100%), url(${ARTWORK_URL}) no-repeat center`,
            backgroundSize: "cover",
            display: "flex",
            justifyContent: "center",
            "& img": {
              maxWidth: "100%",
            },
          }}
        >
          <Box sx={{ p: 3, width: 350 }} component="div">
            <Box role="img" aria-label="GOAT" sx={{ "& svg": { display: "block", width: "100%" } }}>
              <GOATLogoFullWhite />
            </Box>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
}
