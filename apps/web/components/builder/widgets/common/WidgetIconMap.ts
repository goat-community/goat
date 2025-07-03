import type { WidgetTypes } from "@/lib/validations/widget";
import { chartTypes, dataTypes, elementTypes, informationTypes } from "@/lib/validations/widget";
import {
    Bookmark as BookmarksIcon,
    Category as CategoriesIcon,
    Comment as CommentsIcon,
    HorizontalRule as DividerIcon,
    List as FeatureListIcon,
    FilterList as FilterIcon,
    BarChart as HistogramIcon,
    Image as ImageIcon,
    Layers as LayersIcon,
    Functions as NumbersIcon,
    PieChart as PieChartIcon,
    TableChart as TableIcon,
    TextFields as TextIcon,
} from "@mui/icons-material";

type IconMap = {
    [K in WidgetTypes]: React.ElementType;
};

export const iconMap: IconMap = {
    // informationTypes
    [informationTypes.enum.layers]: LayersIcon,
    [informationTypes.enum.bookmarks]: BookmarksIcon,
    [informationTypes.enum.comments]: CommentsIcon,

    // dataTypes
    [dataTypes.enum.filter]: FilterIcon,
    [dataTypes.enum.table]: TableIcon,
    [dataTypes.enum.numbers]: NumbersIcon,
    [dataTypes.enum.feature_list]: FeatureListIcon,

    // chartTypes
    [chartTypes.enum.categories_chart]: CategoriesIcon,
    [chartTypes.enum.histogram_chart]: HistogramIcon,
    [chartTypes.enum.pie_chart]: PieChartIcon,

    // elementTypes
    [elementTypes.enum.text]: TextIcon,
    [elementTypes.enum.divider]: DividerIcon,
    [elementTypes.enum.image]: ImageIcon,
};