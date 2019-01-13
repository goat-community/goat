import {inherits as ol_inherits} from 'ol';
import ol_control_Control from 'ol/control/Control';
import ApiConstants from './secrets';
import {humanize,gup} from './helpers';


function addRowFn(layer){
    if (layer.get('showLegend') === true){
        try {
            var url = layer.getSource().getUrls()[0];
        } catch (err) {
            var url = layer.getSource().getUrl();
        }

        console.log(url);
        var layerName = gup('layers',url.toString());
       
        console.log(layerName);
        if (layerName == null) return;
        var legendItemDiv = document.createElement('div');
        legendItemDiv.className = 'layer-item';
        legendItemDiv.id = layer.get('name');
        document.getElementById("legend-items").appendChild(legendItemDiv);
    
        var legendItemSpan = document.createElement('span');
        legendItemSpan.innerHTML = humanize(layer.get('name'));
        legendItemDiv.appendChild(legendItemSpan);
    
        var legendItemImg = document.createElement('img');
        legendItemImg.style = "width:100%;height:auto;"
        legendItemImg.src = ApiConstants.address_geoserver + 'ows?service=WMS&request=GetLegendGraphic&format=image/png&layer=' +layerName;
        legendItemDiv.appendChild(legendItemImg);
    }

}

function removeRowFn(layer){
    $("#"+layer.get('name')).remove();
}

function ol_legend(e) {
    var options = e || {};
    var wmsVersion = options.wmsVersion || '1.3.0';
    var format = options.format || 'image/png';
    var legendOlDiv = document.createElement('div');
    legendOlDiv.className = options.class + ' ol-unselectable';
    legendOlDiv.id = 'layerLegendId';
    var htmlString = `<div id="layer-legend" class="layer-legend">
                        <div class="layer-legend-header">
                                Layer Legend
                            <span class="fa fa-chevron-up" id="legendBtnId"></span>
                            </div>
                        <div id="legend-items" class="layer-items-container active" style="display:none;">
                        </div>
                    </div>`
    legendOlDiv.innerHTML = htmlString;

    var legendItems = legendOlDiv.querySelector("#legend-items");
    legendOlDiv.querySelector("#legendBtnId").addEventListener('click',legendToggleFn);

    var layers = options.map.getLayers().getArray();
    options.map.getLayers().on("add",function(e){
        e.stopPropagation();
        addRowFn(e.element);
        console.log(e);
    });
    options.map.getLayers().on("remove",function(e){
        e.stopPropagation();
        removeRowFn(e.element);
    })

    ol_control_Control.call(this, {
        element: legendOlDiv,
        target: 'map'
    });
  
}
function legendToggleFn(e){
    e.stopPropagation();
    $('.layer-items-container').slideToggle().toggleClass('active');
    if ($('.layer-items-container').hasClass('active')) {
        $('#legendBtnId').attr('class', 'fa fa-chevron-up');
    } else {
        $('#legendBtnId').attr('class', 'fa fa-chevron-down');
    }
}

ol_legend.prototype.collapse = legendToggleFn;
ol_legend.prototype.expand = legendToggleFn;
ol_legend.prototype.addRow = addRowFn;
ol_legend.prototype.removeRow = removeRowFn



ol_inherits(ol_legend, ol_control_Control);

export {ol_legend};