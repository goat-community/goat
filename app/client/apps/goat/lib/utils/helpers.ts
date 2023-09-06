import dayjs from "dayjs";
import Color from "color";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function filterSearch<T extends Record<string, any>>(
  allArray: T[],
  searchKey: keyof T,
  searchText: string
) {
  if (searchText !== "") {
    return allArray.filter((item) => {
      const value = String(item[searchKey]).toLowerCase();
      return value.includes(searchText.toLowerCase());
    });
  }
  return allArray;
}

export function makeArrayUnique<T>(arr: T[], key: keyof T): T[] {
  const uniqueSet = new Set();
  const uniqueArray: T[] = [];

  arr.forEach((obj) => {
    const uniqueValue = criterion(obj, key);

    if (!uniqueSet.has(uniqueValue)) {
      uniqueSet.add(uniqueValue);
      uniqueArray.push(obj);
    }
  });

  return uniqueArray;
}

export function groupBy(arr, prop) {
  return arr.reduce((acc, obj) => {
    const key = obj[prop];
    if (!acc[key]) {
      acc[key] = [];
    }
    acc[key].push(obj);
    return acc;
  }, {});
}

function criterion<T>(person: T, key: keyof T) {
  return person[key];
}

export const formatDate = (date: string, format: string) => {
  return dayjs(date).format(format);
};

export const supportedFileTypes = [
  "geojson",
  "shapefile",
  "geopackage",
  "geobuf",
  "csv",
  "xlsx",
  "kml",
  "mvt",
  "wfs",
  "binary",
  "wms",
  "xyz",
  "wmts",
  "mvt",
  "csv",
  "xlsx",
  "json",
];

export const calculateLayersCountByKey = (data: [] | undefined, keyToCount: string) => {
  let count = 0;

  data?.forEach((obj) => {
    if (obj[keyToCount]) {
      count++;
    }
  });

  return count;
};

export const calculateLayersCountByKeyAndValue = (
  data: [] | undefined,
  keyToCount: string,
  value: string
) => {
  let count = 0;

  data?.forEach((obj) => {
    if (obj[keyToCount] === value) {
      count++;
    }
  });

  return count;
};

export function changeColorOpacity(params: { color: string; opacity: number }): string {
  const { color, opacity } = params;
  return new Color(color).rgb().alpha(opacity).string();
}