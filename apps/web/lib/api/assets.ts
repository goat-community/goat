import { apiRequestAuth } from "@/lib/api/fetcher";
import type { AssetTypeEnum, UploadedAsset } from "@/lib/validations/assets";
import { uploadedAssetSchema } from "@/lib/validations/assets";

export const ASSETS_API_BASE_URL = new URL("api/v2/asset", process.env.NEXT_PUBLIC_API_URL).href;

export const uploadAsset = async (file: File, assetType: AssetTypeEnum): Promise<UploadedAsset> => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("asset_type", assetType);

    const response = await apiRequestAuth(`${ASSETS_API_BASE_URL}/upload`, {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        // The server returned an error; you can throw it to be caught in the UI
        throw new Error("Upload failed");
    }

    const data = await response.json();

    // Validate with Zod and return
    return uploadedAssetSchema.parse(data);
};
