// Copyright: MIT License
// Original Author: rowanwins
// Original Source: https://github.com/rowanwins/maplibregl-mapbox-request-transformer

export function isMapboxURL(url: string) {
  return url.indexOf('mapbox:') === 0;
}

export function transformMapboxUrl(url: string, resourceType: string, accessToken: string): { url: string } | undefined {
  if (url.indexOf('/styles/') > -1 && url.indexOf('/sprite') === -1) return { url: normalizeStyleURL(url, accessToken) }
  if (url.indexOf('/sprites/') > -1) return { url: normalizeSpriteURL(url, '', '.json', accessToken) }
  if (url.indexOf('/fonts/') > -1) return { url: normalizeGlyphsURL(url, accessToken) }
  if (url.indexOf('/v4/') > -1) return { url: normalizeSourceURL(url, accessToken) }
  if (resourceType === 'Source') return { url: normalizeSourceURL(url, accessToken) }
}



function parseUrl(url) {
  const urlRe = /^(\w+):\/\/([^/?]*)(\/[^?]+)?\??(.+)?/;
  const parts = url.match(urlRe);
  if (!parts) {
    throw new Error('Unable to parse URL object');
  }
  return {
    protocol: parts[1],
    authority: parts[2],
    path: parts[3] || '/',
    params: parts[4] ? parts[4].split('&') : []
  };
}

function formatUrl(urlObject, accessToken) {
  const apiUrlObject = parseUrl("https://api.mapbox.com");
  urlObject.protocol = apiUrlObject.protocol;
  urlObject.authority = apiUrlObject.authority;
  urlObject.params.push(`access_token=${accessToken}`);
  const params = urlObject.params.length ? `?${urlObject.params.join('&')}` : '';
  return `${urlObject.protocol}://${urlObject.authority}${urlObject.path}${params}`;
}

function normalizeStyleURL(url, accessToken) {
  const urlObject = parseUrl(url);
  urlObject.path = `/styles/v1${urlObject.path}`;
  return formatUrl(urlObject, accessToken);
}

function normalizeGlyphsURL(url, accessToken) {
  const urlObject = parseUrl(url);
  urlObject.path = `/fonts/v1${urlObject.path}`;
  return formatUrl(urlObject, accessToken);
}

function normalizeSourceURL(url, accessToken) {
  const urlObject = parseUrl(url);
  urlObject.path = `/v4/${urlObject.authority}.json`;
  urlObject.params.push('secure');
  return formatUrl(urlObject, accessToken);
}

function normalizeSpriteURL(url, _format, _extension, accessToken) {
  const urlObject = parseUrl(url);
  const path = urlObject.path.split('.')
  urlObject.path = `/styles/v1${path[0]}/sprite.${path[1]}`;
  return formatUrl(urlObject, accessToken);
}
