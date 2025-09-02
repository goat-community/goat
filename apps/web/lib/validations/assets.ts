import { z } from "zod";

// Enum for AssetType
export const assetTypeEnum = z.enum(["image", "icon"]);

// UploadedAsset Zod schema
export const uploadedAssetSchema = z.object({
    id: z.string().uuid().optional(),
    user_id: z.string().uuid(),
    s3_key: z.string().min(1),
    file_name: z.string().max(255),
    mime_type: z.string().max(100),
    file_size: z.number().int().nonnegative(),
    asset_type: assetTypeEnum,
    content_hash: z.string().length(64), // SHA256 hash, exactly 64 chars
    created_at: z.string().datetime().optional(),
    updated_at: z.string().datetime().optional(),
});

export type UploadedAsset = z.infer<typeof uploadedAssetSchema>;
export type AssetTypeEnum = z.infer<typeof assetTypeEnum>;