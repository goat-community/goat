import {Map, View} from 'ol';
import {transform} from 'ol/proj';
import ApiConstants from './secrets';
import {GetBaseLayers,addRemoveAccesibilityLayer,WaysLayers} from './layers';
import 'ol-ext/control/Search.css';
import SearchPhoton from 'ol-ext/control/SearchPhoton';
import {ol_legend} from './legend';


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
 console.log('testtest');
    addRemoveAccesibilityLayer.add(map);
  }  

})

$('body').on('change','#accessibility_basemap_select',function(){
 console.log('testtest');
  let style = this.value;
  if (style != 'no_basemap'){
    addRemoveAccesibilityLayer.add(map);

   
  }
  else{
    map.getLayers().forEach(function (layer) {
      console.log(layer.get('name'));
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
