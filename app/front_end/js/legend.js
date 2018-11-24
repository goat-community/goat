import {inherits as ol_inherits} from 'ol';
import ol_control_Control from 'ol/control/Control';
import ApiConstants from './secrets';

function ol_legend(e) {
    var options = e || {};
    var wmsVersion = options.wmsVersion || '1.3.0';
    var format = options.format || 'image/png';

    var legendOlDiv = document.createElement('div');
    legendOlDiv.className = options.class + ' ol-unselectable';
    var htmlString = `<div id="layer-legend" style="visibility:hidden;" class="layer-legend">
                        <div class="layer-legend-header">
                                Layer Legend
                            <span class="fa fa-chevron-up"></span>
                            </div>
                        <div id="legend-items" class="layer-items-container">
                        </div>
                    </div>`
    legendOlDiv.innerHTML = htmlString;

    var legendItems = legendOlDiv.querySelector("#legend-items");

    var layers = options.map.getLayers().getArray();
    for (var i = 0; i < layers.length; i++) {
        if (layers[i].get('showLegend') === true) {
            try {
                var url = layers[i].getSource().getUrls()[0];
            } catch (err) {
                var url = layers[i].getSource().getUrl();
            }
            var legendItemDiv = document.createElement('div');
            legendItemDiv.className = 'layer-item';
            legendItems.appendChild(legendItemDiv);

            var legendItemSpan = document.createElement('span');
            legendItemSpan.innerHTML = "Heatmap ";
            legendItemDiv.appendChild(legendItemSpan);

            var legendItemImg = document.createElement('img');
            legendItemImg.src = ApiConstants.guest_geoserver_url + 'ows?service=WMS&request=GetLegendGraphic&format=image/png&layer=cite:heatmap';
            legendItemDiv.appendChild(legendItemImg);
        }
    }

    ol_control_Control.call(this, {
        element: legendOlDiv,
        target: 'map'
    });
  
}
ol_inherits(ol_legend, ol_control_Control);

export {ol_legend};