import {Map, View} from 'ol';
import {transform} from 'ol/proj';
import ApiConstants from './secrets';
import {GetBaseLayers,addRemoveAccesibilityLayer,WaysLayers} from './layers';
import 'ol-ext/control/Search.css';
import SearchPhoton from 'ol-ext/control/SearchPhoton';
import {ol_legend} from './legend';
import Mask from 'ol-ext/filter/Mask';
import {Fill} from 'ol/style';
import {getCenter} from 'ol/extent';

var center = transform([ApiConstants.x,ApiConstants.y], 'EPSG:4326', 'EPSG:3857');
var map = new Map({
    layers: GetBaseLayers(),
    loadTilesWhileInteracting: true,
    target: 'map',
    view: new View({
      center: center,
      zoom: 14
    })
});

GetBaseLayers().forEach(function(layer,index,array){
  if (layer.get('name') =='StudyArea'){
  //For all basemaps a filter excluding everything a part from the Study-Area is set.
    var i;
    layer.getSource().on('change', function(e) {
      var f = layer.getSource().getFeatures()[0];
      var extent = f.getGeometry().getExtent();
      map.getView().fit(extent,map.getSize());
      var center = getCenter(extent);
      var geographicCenter = transform([center[0],center[1]], 'EPSG:3857','EPSG:4326');
      //Update ApiConstant
      ApiConstants.x = geographicCenter[0];
      ApiConstants.y = geographicCenter[1];
      var mask = new Mask({ feature: f, inner:false, fill: new Fill({ color:[169,169,169,0.8] }) })
      for (i of array){
        i.addFilter(mask);
      }
    })
  }
});
////////Ol3-ext Photon Address
var search = new SearchPhoton(
  {	
    lang:"en",	
    position: true	
  });
    

// Select feature when click on the reference index
search.on('select', function(e)
{	
	map.getView().setCenter(e.coordinate);
	map.getView().setZoom(18);
	
});
map.addControl(search);


var legendControl = new ol_legend({
  map: map,
  class: 'ol_legend'
});

map.addControl(legendControl);

//Events for accesibility layer

$('body').on('change','.thematic_data_weight, .thematic_item_check',function(){
 
  if ($('#accessibility_basemap_select').val() != 'no_basemap'){

    addRemoveAccesibilityLayer.add(map);
  }  

})

$('body').on('change','#accessibility_basemap_select',function(){

  let style = this.value;
  if (style != 'no_basemap'){
    addRemoveAccesibilityLayer.add(map);

   
  }
  else{
    map.getLayers().forEach(function (layer) {
    if (layer.get('name') != undefined & layer.get('name') === 'layer_accessibility') {
      addRemoveAccesibilityLayer.remove(map);
    }
    });
  }
  
});

function getMap(){
  return map;
}



export {map,getMap};
