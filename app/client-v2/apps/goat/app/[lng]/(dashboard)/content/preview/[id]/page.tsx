"use client";

import PreviewManagement from "@/app/[lng]/(dashboard)/content/preview/PreviewManagement";

type Props = {
  params: {
    id: string;
  };
};

export default function PreviewPage({ params: { id } }: Props) {
  console.log("id", id);
  return (
    <div>
      <PreviewManagement />
    </div>
  );
}
