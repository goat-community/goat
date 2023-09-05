from .base import CRUDBase
from src.db.models._link_model import LayerProjectLink
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from src.crud.crud_layer import layer as crud_layer
from sqlalchemy import select
from src.db.models.layer import Layer
from fastapi import HTTPException, status
from src.schemas.project import (
    ITileLayerProjectUpdate,
    IFeatureLayerStandardProjectUpdate,
    IFeatureLayerIndicatorProjectUpdate,
    IFeatureLayerScenarioProjectUpdate,
    IImageryLayerProjectUpdate,
    ITableLayerProjectUpdate,
)


class CRUDLayerProject(CRUDBase):
    async def get_all(
        self,
        async_session: AsyncSession,
        project_id: UUID,
    ):
        """Get all layers from a project"""

        # Get all layers from project
        query = select([Layer, LayerProjectLink]).where(
            LayerProjectLink.project_id == project_id, Layer.id == LayerProjectLink.layer_id
        )

        # Get all layers from project
        layer_projects = await self.get_multi(
            async_session,
            query=query,
        )
        return layer_projects

    async def get_by_ids(
        self,
        async_session: AsyncSession,
        project_id: UUID,
        layer_ids: [UUID],
    ):
        # Get all layers from project by id
        query = select([Layer, LayerProjectLink]).where(
            LayerProjectLink.project_id == project_id,
            Layer.id == LayerProjectLink.layer_id,
            Layer.id.in_(layer_ids),
        )

        # Get all layers from project
        layer_projects = await self.get_multi(
            async_session,
            query=query,
        )
        return layer_projects

    async def create(
        self,
        async_session: AsyncSession,
        project_id: UUID,
        layer_ids: [UUID],
    ):
        """Create a link between a project and a layer"""

        # Get number of layers in project
        layer_projects = await self.get_multi(
            async_session,
            query=select(LayerProjectLink).where(LayerProjectLink.project_id == project_id),
        )

        # Check if maximum number of layers in project is reached. In case layer_project is empty just go on.
        if layer_projects != []:
            if len(layer_projects) + len(layer_ids) >= 300:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Maximum number of layers in project reached",
                )

        # Get layer from catalog
        layers = await crud_layer.get_multi(
            async_session,
            query=select(Layer).where(Layer.id.in_(layer_ids)),
        )

        # Create link between project and layer
        for layer in layers:
            layer = layer[0]
            layer_project = LayerProjectLink(
                project_id=project_id,
                layer_id=layer.id,
                name=layer.name
            )
            # Add style if exists
            if layer.style is not None:
                layer_project.style = layer.style

            # Add to database
            await CRUDBase(LayerProjectLink).create(
                async_session,
                obj_in=layer_project,
            )

        layers = await self.get_by_ids(async_session, project_id, layer_ids)
        return layers

    async def update(
        self,
        async_session: AsyncSession,
        project_id: UUID,
        layer_id: UUID,
        layer_project: IFeatureLayerStandardProjectUpdate
        | IFeatureLayerIndicatorProjectUpdate
        | IFeatureLayerScenarioProjectUpdate
        | ITableLayerProjectUpdate
        | ITileLayerProjectUpdate
        | IImageryLayerProjectUpdate,
    ):
        """Update a link between a project and a layer"""

        # Get layer project
        layer_project_old = await self.get_by_multi_keys(
            async_session,
            keys={"project_id": project_id, "layer_id": layer_id},
        )
        if layer_project_old == []:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Layer project not found"
            )

        # Update layer project
        layer_project = await CRUDBase(LayerProjectLink).update(
            async_session,
            db_obj=layer_project_old[0],
            obj_in=layer_project,
        )
        return layer_project


layer_project = CRUDLayerProject(LayerProjectLink)
