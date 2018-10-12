import {Map, View} from 'ol';
import {transform} from 'ol/proj';
import ApiConstants from './secrets';
import {GetBaseLayers,addRemoveAccesibilityLayer,WaysLayers} from './layers';
import 'ol-ext/control/Search.css';
import SearchPhoton from 'ol-ext/control/SearchPhoton';


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


//////*****WAYS LAYER*****///////////////////

WaysLayers.addTo(map);
// WaysLayers.removeFrom(map);
//////////////////////////////////////////////

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
    //layer_accessibility.set('name', 'layer_accessibility');
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
