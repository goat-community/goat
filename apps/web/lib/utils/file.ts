export function getTotalFilesSize(files: File[]): number {
  return files.reduce((previousValue, currentFile) => {
    return previousValue + currentFile.size;
  }, 0);
}

export function matchIsFile(value: unknown): value is File {
  // Secure SSR
  return typeof window !== "undefined" && value instanceof File;
}

export function fileListToArray(filelist: FileList): File[] {
  return Array.from(filelist);
}

export function getFileDetails(value: File | File[]) {
  const name = matchIsFile(value) ? value.name : value[0]?.name || "";
  const parts = name.split(".");
  const extension = parts.pop() as string;
  const filenameWithoutExtension = parts.join(".");

  return {
    filename: filenameWithoutExtension,
    extension,
  };
}
