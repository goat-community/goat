# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.models.base_class import Base  

from .study_area import StudyArea as StudyAreaDB
from .grid_visualization import GridVisualization as GridVisualizationDB
from .grid_visualization_parameter import GridVisualizationParameter as GridVisualizationParameterDB
from .grid_calculation import GridCalculation as GridCalculationDB
from .study_area_grid_visualization import StudyAreaGridVisualization as StudyAreaGridVisualizationDB
from .sub_study_area import SubStudyArea as SubStudyAreaDB
from .aoi import Aoi as AoiDB 
from .building import Building as BuildingDB
from .node import Node as NodeDB 
from .poi import Poi as PoiDB
from .edge import Edge as EdgeDB 
from .population import Population as PopulationDB
from .reached_poi_heatmap import ReachedPoiHeatmap as ReachedPoiHeatmapDB
from .reached_edge_heatmap import ReachedEdgeHeatmap as ReachedEdgeHeatmapDB
from .reached_poi_heatmap_accessibility import ReachedPoiHeatmapAccessibility as ReachedPoiHeatmapAccessibilityDB
from .reached_edge_heatmap_grid_calculation import ReachedEdgeHeatmapGridCalculation as ReachedEdgeHeatmapGridCalculationDB