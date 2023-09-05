from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from fastapi_pagination import Page
from fastapi_pagination import Params as PaginationParams
from pydantic import UUID4
from sqlalchemy import and_, select

from src.crud.crud_report import report as crud_report
from src.db.models.report import Report
from src.db.session import AsyncSession
from src.endpoints.deps import get_db, get_user_id
from src.schemas.common import ContentIdList, OrderEnum
from src.schemas.report import (
    IReportCreate,
    IReportRead,
    IReportUpdate,
    request_examples as report_request_examples,
)
from src.core.content import (
    create_content,
    delete_content_by_id,
    read_content_by_id,
    read_contents_by_ids,
    update_content_by_id,
)

router = APIRouter()


# Report endpoints
@router.post(
    "",
    summary="Create a new report",
    response_model=IReportRead,
    response_model_exclude_none=True,
    status_code=201,
)
async def create_report(
    async_session: AsyncSession = Depends(get_db),
    user_id: UUID4 = Depends(get_user_id),
    *,
    report_in: IReportCreate = Body(
        ..., example=report_request_examples["create"], description="Project to create"
    ),
):
    """This will create an empty report."""
    return await create_content(
        async_session=async_session,
        model=Report,
        crud_content=crud_report,
        content_in=report_in,
        other_params={"user_id": user_id},
    )


@router.post(
    "/get-by-ids",
    summary="Retrieve a list of reports by their IDs",
    response_model=Page[IReportRead],
    response_model_exclude_none=True,
    status_code=200,
)
async def read_reports_by_ids(
    async_session: AsyncSession = Depends(get_db),
    page_params: PaginationParams = Depends(),
    ids: ContentIdList = Body(
        ...,
        example=report_request_examples["get"],
        description="List of report IDs to retrieve",
    ),
):
    return await read_contents_by_ids(
        async_session=async_session,
        ids=ids,
        model=Report,
        crud_content=crud_report,
        page_params=page_params,
    )


@router.get(
    "/{id}",
    summary="Retrieve a report by its ID",
    response_model=IReportRead,
    response_model_exclude_none=True,
    status_code=200,
)
async def read_report(
    async_session: AsyncSession = Depends(get_db),
    id: UUID4 = Path(
        ...,
        description="The ID of the report to get",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
):
    """Retrieve a report by its ID."""
    return await read_content_by_id(
        async_session=async_session, id=id, model=Report, crud_content=crud_report
    )


@router.get(
    "",
    summary="Retrieve a list of reports",
    response_model=Page[IReportRead],
    response_model_exclude_none=True,
    status_code=200,
)
async def read_reports(
    async_session: AsyncSession = Depends(get_db),
    page_params: PaginationParams = Depends(),
    folder_id: UUID4 = Query(..., description="Folder ID"),
    user_id: UUID4 = Depends(get_user_id),
    search: str = Query(None, description="Searches the name of the report"),
    order_by: str = Query(
        None,
        description="Specify the column name that should be used to order. You can check the Report model to see which column names exist.",
        example="created_at",
    ),
    order: OrderEnum = Query(
        "ascendent",
        description="Specify the order to apply. There are the option ascendent or descendent.",
        example="ascendent",
    ),
):
    """Retrieve a list of reports."""
    query = select(Report).where(and_(Report.user_id == user_id, Report.folder_id == folder_id))
    reports = await crud_report.get_multi(
        async_session,
        query=query,
        page_params=page_params,
        search_text={"name": search} if search else {},
        order_by=order_by,
        order=order,
    )

    if len(reports.items) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Reports Found")

    return reports


@router.put(
    "/{id}",
    response_model=IReportRead,
    response_model_exclude_none=True,
    status_code=200,
)
async def update_report(
    async_session: AsyncSession = Depends(get_db),
    id: UUID4 = Path(
        ...,
        description="The ID of the report to update",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
    report_in: IReportUpdate = Body(
        ..., example=report_request_examples["update"], description="Report to update"
    ),
):
    return await update_content_by_id(
        async_session=async_session,
        id=id,
        model=Report,
        crud_content=crud_report,
        content_in=report_in,
    )


@router.delete(
    "/{id}",
    response_model=None,
    status_code=204,
)
async def delete_report(
    async_session: AsyncSession = Depends(get_db),
    id: UUID4 = Path(
        ...,
        description="The ID of the report to update",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
):
    return await delete_content_by_id(
        async_session=async_session, id=id, model=Report, crud_content=crud_report
    )
