import dayjs from "dayjs";

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

function criterion<T>(person: T, key: keyof T) {
  return person[key];
}

export const formatDate = (date, format) => {
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

export const generateRowData = (data: object, label: string) => {
  return {
    ...data,
    id: data.id,
    name: data?.name,
    modified: formatDate(data?.metadata?.updated_at, "DD MMM YY"),
    path: ["home"],
    size: `${data?.metadata?.size || ""} kb`,
    label: label,
    info: [
      {
        tag: "Name",
        data: data?.name,
      },
      {
        tag: "Description",
        data: data?.description,
      },
      {
        tag: "Type",
        data: data?.type,
      },
      {
        tag: "Modified",
        data: data?.updated_at,
      },
      {
        tag: "Size",
        data: `${data?.metadata?.size || ""} kb`,
      },
    ],
  };
};
