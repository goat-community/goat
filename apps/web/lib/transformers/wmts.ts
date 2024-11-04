/**
 * Converts a WMTS resource URL to a Maplibre-compatible XYZ URL.
 *
 * @param {string} resourceUrl - The WMTS resource URL template.
 * @param {string} style - The style to be used in the URL.
 * @param {string} tileMatrixSet - The tile matrix set to be used in the URL.
 * @returns {string} - The converted Maplibre-compatible URL.
 */
export const convertWmtsToXYZUrl = (resourceUrl: string, style?: string, tileMatrixSet?: string) => {
  let url = resourceUrl
    .replace("{TileMatrix}", "{z}")
    .replace("{TileRow}", "{y}")
    .replace("{TileCol}", "{x}");

  if (style) {
    url = url.replace("{Style}", style);
  }

  if (tileMatrixSet) {
    url = url.replace("{TileMatrixSet}", tileMatrixSet);
  }

  return url;
};


/**
 * Identifies a Google-compatible TileMatrixSet from the provided tileMatrixSets.
 *
 * @param {Array} tileMatrixSets - The array of TileMatrixSets.
 * @returns {Object|null} - The identified Google-compatible TileMatrixSet or null if not found.
 */
export const getGoogleCompatibleTileMatrixSet = (tileMatrixSets) => {
  // Google Web Mercator ScaleDenominator values (integer part) for levels 0 to 2
  const googleScaleDenominators = [
    559082264, 279541132, 139770566
  ];

  // Try to Identify Google-compatible TileMatrixSets from WellKnownScaleSet
  const googleCompatibleTileMatrixSets = tileMatrixSets.filter((tms) =>
    tms.SupportedCRS?.includes("EPSG:3857") && tms?.WellKnownScaleSet?.includes("GoogleMapsCompatible")
  );

  // If no Google-compatible TileMatrixSets found, try using ScaleDenominator
  if (googleCompatibleTileMatrixSets.length === 0) {
    tileMatrixSets.forEach((tms) => {
      if (tms.SupportedCRS?.includes("EPSG:3857")) {
        const hasGoogleScaleDenominator = tms.TileMatrix?.some((tm) => {
          const scaleDenominatorInt = Math.floor(tm.ScaleDenominator);
          return googleScaleDenominators.includes(scaleDenominatorInt);
        });

        if (hasGoogleScaleDenominator) {
          googleCompatibleTileMatrixSets.push(tms);
        }
      }
    });
  }

  // Return the identified Google-compatible TileMatrixSet or null if not found
  return googleCompatibleTileMatrixSets?.[0] ?? null;
};

/**
 * Extracts the WMTS layers from the capabilities document.
 *
 * @param {object} capabilities - The WMTS capabilities document.
 * @returns {object[]} - The extracted WMTS layers.
 */
export const getWmtsFlatLayers = (capabilities) => {
  const datasets = capabilities?.Contents?.Layer;
  const tileMatrixSets = capabilities?.Contents?.TileMatrixSet;

  // Fallback to any TileMatrixSet with EPSG:3857 if no Google-compatible TileMatrixSet is found
  const webMercator = getGoogleCompatibleTileMatrixSet(tileMatrixSets)
  if (!webMercator) return [];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const options = [] as any[];
  if (datasets?.length) {
    datasets.forEach((dataset) => {
      const tileMatrixSetLink = dataset.TileMatrixSetLink.find((link) =>
        link.TileMatrixSet.includes(webMercator.Identifier)
      );
      const supportedFormats = ["image/png", "image/jpeg", "image/tiff", "image/png8"];
      const resourceUrls = supportedFormats.map((format) => ({
        format,
        url: dataset.ResourceURL.find((url) => url.format.includes(format)),
      }));

      if (tileMatrixSetLink) {
        dataset.Style.forEach((style) => {
          resourceUrls.forEach(({ format, url }) => {
            if (url) {
              options.push({
                Identifier: dataset.Identifier,
                ResourceURL: url.template,
                Format: format,
                TileMatrixSet: tileMatrixSetLink.TileMatrixSet,
                CRS: "EPSG:3857",
                Style: style.Identifier,
                Title: dataset.Title,
                Abstract: dataset.Abstract,
                WGS84BoundingBox: dataset.WGS84BoundingBox,
              });
            }
          });
        });
      }
    });
  }

  return options;
};
