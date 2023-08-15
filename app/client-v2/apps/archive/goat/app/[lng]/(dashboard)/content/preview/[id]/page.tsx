"use client";

import PreviewManagement from "@/app/[lng]/(dashboard)/content/preview/PreviewManagement";

interface IParams {
  params: {
    id: string;
  };
}

export default function PreviewPage({ params: { id } }: IParams) {
  return (
    <div>
      <PreviewManagement id={id} />
    </div>
  );
}
