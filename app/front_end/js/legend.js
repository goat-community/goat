import {inherits as ol_inherits} from 'ol';
import ol_control_Control from 'ol/control/Control'


function ol_legend(e) {
    var options = e || {};
    var wmsVersion = options.wmsVersion || '1.3.0';
    var format = options.format || 'image/png';
    var legendP = document.createElement('p');
    legendP.innerHTML = 'Legend:';
    var legendDiv = document.createElement('div');
    legendDiv.className = options.class + ' ol-unselectable';
    legendDiv.appendChild(legendP);
    var layers = options.map.getLayers().getArray();
    for (var i = 0; i < layers.length; i++) {
        if (layers[i].get('showLegend') === true) {
            try {
                var url = layers[i].getSource().getUrls()[0];
            } catch (err) {
                var url = layers[i].getSource().getUrl();
            }
            var legendImg = document.createElement('img');
            legendImg.src = url + '&version=' + wmsVersion + '&service=WMS&request=GetLegendGraphic&sld_version=1.1.0&layer=' + layers[i].getSource().getParams().layers + '&format=' + format;
            legendDiv.appendChild(legendImg);
        }
    }
    ol_control_Control.call(this, {
        element: legendDiv
    });
}
inherits(ol_legend, ol_control_Control);