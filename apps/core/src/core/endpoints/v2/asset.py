import mimetypes
import uuid
from io import BytesIO

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.core.config import settings
from core.db.models.asset import AssetType, UploadedAsset
from core.deps.auth import auth_z
from core.endpoints.deps import get_db, get_user_id
from core.services.s3 import s3_service

router = APIRouter()

# Define allowed MIME types for each asset type
ALLOWED_MIME_TYPES = {
    AssetType.IMAGE: [
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "image/bmp",
        "image/tiff",
    ],
    AssetType.ICON: [
        "image/svg+xml",
        "image/x-icon",  # .ico files
        "image/png",  # Small PNGs can also be icons
    ],
}


@router.post(
    "/upload",
    response_model=UploadedAsset,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(auth_z)],
)
async def upload_asset(
    async_session: AsyncSession = Depends(get_db),
    user_id: UUID4 = Depends(get_user_id),
    file: UploadFile = File(...),
    asset_type: AssetType = Form(...),
) -> UploadedAsset:
    """
    Uploads a new asset to S3 and records its metadata in the database.
    Performs validation to ensure only allowed image and icon types are uploaded.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No file selected."
        )

    # 1. Validate MIME type based on asset_type
    # We first try to infer from filename, then rely on content_type provided by browser
    detected_mime_type, _ = mimetypes.guess_type(file.filename)
    if detected_mime_type:
        actual_mime_type = detected_mime_type
    else:
        actual_mime_type = file.content_type  # Fallback to content-type header

    if actual_mime_type not in ALLOWED_MIME_TYPES.get(asset_type, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type for asset_type '{asset_type.value}'. "
            f"Allowed types: {', '.join(ALLOWED_MIME_TYPES.get(asset_type, []))}. "
            f"Received: {actual_mime_type}",
        )

    file_content = await file.read()

    if len(file_content) > settings.ASSETS_MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum allowed size is {settings.ASSETS_MAX_FILE_SIZE // (1024 * 1024)}MB.",
        )

    content_hash = s3_service.calculate_sha256(file_content)

    existing_asset = await async_session.execute(
        select(UploadedAsset)
        .where(UploadedAsset.content_hash == content_hash)
        .where(UploadedAsset.user_id == user_id) # Add this line
    )
    existing_asset = existing_asset.fetchone()
    if existing_asset:
        existing_asset = existing_asset[0]  # Extract the UploadedAsset object
        # If an identical asset (by content and user) already exists,
        # update its file_name if different, then return it.
        # No new upload to S3.
        if existing_asset.file_name != file.filename:
            print(f"Info: User {user_id} re-uploaded existing content. Updating file_name of asset {existing_asset.id} from '{existing_asset.file_name}' to '{file.filename}'.")
            existing_asset.file_name = file.filename
            async_session.add(existing_asset)
            await async_session.commit()
            await async_session.refresh(existing_asset)
            print(f"Info: User {user_id} re-uploaded existing content. Updated asset: {existing_asset.id}")
        else:
            print(f"Info: User {user_id} re-uploaded existing content with the same file_name. Returning existing asset: {existing_asset.id}")

        return existing_asset # Return the existing asset directly

    file_extension = mimetypes.guess_extension(actual_mime_type)
    if not file_extension:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not determine file extension for MIME type '{actual_mime_type}'.",
        )

    s3_key = f"goat/{settings.ENVIRONMENT}/users/{user_id}/{asset_type.value}/{uuid.uuid4().hex}{file_extension}"
    s3_service.upload_file(BytesIO(file_content), settings.AWS_S3_ASSETS_BUCKET, s3_key, actual_mime_type)
    new_asset = UploadedAsset(
        user_id=user_id,
        s3_key=s3_key,
        file_name=file.filename,
        mime_type=actual_mime_type,
        file_size=len(file_content),
        asset_type=asset_type,
        content_hash=content_hash,
    )
    async_session.add(new_asset)
    await async_session.commit()
    await async_session.refresh(new_asset)
    print(f"Info: User {user_id} uploaded new asset: {new_asset.id}")
    return new_asset



