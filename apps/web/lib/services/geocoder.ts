/* eslint-disable @typescript-eslint/no-explicit-any */
export default async function search(
  endpoint: string,
  source: string,
  accessToken: string,
  query: string,
  onResult: (err: any, res: Response | null) => void,
  proximity?: { longitude: number; latitude: number },
  country?: string,
  bbox?: number[],
  types?: string,
  limit?: number,
  autocomplete?: boolean,
  language?: string
) {
  try {
    const baseUrl = `${endpoint}/geocoding/v5/${source}/${query}.json`;
    const searchParams = {
      ...(isNotNil(accessToken) && { access_token: accessToken }),
      ...(isNotNil(proximity) && {
        proximity:
          proximity && Object.keys(proximity).length === 2
            ? `${proximity.longitude},${proximity.latitude}`
            : null,
      }),
      ...(isNotNil(bbox) && {
        bbox: bbox && bbox.length > 0 ? bbox.join(",") : null,
      }),

      ...(isNotNil(types) && {
        types,
      }),
      ...(isNotNil(country) && {
        country,
      }),
      ...(isNotNil(limit) && {
        limit,
      }),
      ...(isNotNil(autocomplete) && {
        autocomplete,
      }),
      ...(isNotNil(language) && {
        language,
      }),
    };
    const url = `${baseUrl}?${toUrlString(searchParams)}`;
    const res = await fetch(url);
    const data = await res.json();
    onResult(null, data);
    return { err: null, res };
  } catch (err) {
    onResult(err, null);
    return { err, res: null };
  }
}
function toUrlString(params: any) {
  return Object.keys(params)
    .map((key) => encodeURIComponent(key) + "=" + encodeURIComponent(params[key]))
    .join("&");
}

function isNotNil(value: unknown) {
  return value !== undefined && value !== null;
}
