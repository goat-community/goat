
 import {Tile as TileLayer, Vector as VectorLayer, Image as ImageLayer} from 'ol/layer';
 import {OSM,XYZ,BingMaps,Vector as VectorSource, ImageWMS} from 'ol/source';
 import {WFS,GeoJSON} from 'ol/format';
 import {boundaryStyle} from './style';
 import {Fill} from 'ol/style';
 import ApiConstants from './secrets';
 import Mask from 'ol-ext/filter/Mask';
//  import {map} from './map';

var oepnv_attribution = '<a href="https://memomaps.de/">memomaps.de</a> <a href="http://creativecommons.org/licenses/by-sa/2.0/">'
+'CC-BY-SA</a>, map data <a href="http://openstreetmap.org/">'
+'Openstreetmap</a> <a href="http://opendatacommons.org/licenses/odbl/1.0/">ODbL</a>'
var styles = ["OSM-Standard","OSM-Carto-DB-Light","OSM-Carto-DB-Dark"];
var urls = ['http://{a-c}.tile.openstreetmap.org/{z}/{x}/{y}.png','http://{a-c}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png','http://{a-c}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png'];
var layers = [];
var i, ii;
for (i = 0, ii = styles.length; i < ii; ++i) {
  layers.push(new TileLayer({
      visible: false,
      preload: Infinity,
      source: new OSM({
      "url": urls[i],
      imagerySet: styles[i],
      maxZoom: 19
    })
  }));
}

var bingmaps = new TileLayer({
    visible: false,
    preload: Infinity,
    source: new BingMaps({
      key: ApiConstants.bingmaps_key,
      imagerySet: 'Aerial',
      maxZoom: 19

    })
  });

layers.push(bingmaps);
styles.push('Aerial');

var mapbox = new TileLayer({
	source: new XYZ({
	url: 'https://api.mapbox.com/styles/v1/mapbox/streets-v10/tiles/256/{z}/{x}/{y}?access_token='+ApiConstants.mapbox_key
	})
})

layers.push(mapbox);
styles.push('Mapbox');


var oepnv_karte = new TileLayer({
  //extent: [-20037508,-20037508,20037508,20037508],
  visible: false,
  preload: Infinity,
  source: new XYZ({
    attributions: oepnv_attribution,
    url:"https://tileserver.memomaps.de/tilegen/{z}/{x}/{y}.png",
    maxZoom:18,
    })
   })
  
  layers.push(oepnv_karte);
  styles.push('PublicTransport');


$('body').on('change','#layer-select',function(){
  var style = this.value;
  for (var i = 0, ii = layers.length; i < ii; ++i) {
    layers[i].setVisible(styles[i] === style);
    if (style == 'Mapbox'){
    	$('#mapbox').show()
    }
    else{
    	$('#mapbox').hide()
    }
  }
})


var numbers = {'1':'one','2':'two','3':'three','4':'four','5':'five'}





var accessibility_layer = function(){
  let heatmap_input ={};
  let select_heatmap_input = $('#main_thematic_data .content :checkbox:checked')
  let link = ApiConstants.host_geoserver_url+'cite/wms?service=WMS&version=1.1.0&request=GetMap&layers=cite:heatmap&LAYERS=cite%3Aheatmap&viewparams=amenities:%27'
  let link_part = '' 
  for (var i=0; i < select_heatmap_input.length; i++){
    link_part = link_part + "eeeppp" + select_heatmap_input[i].id.replace('check_','') + 'cccttt' + numbers[$(select_heatmap_input[i]).next().next().val()] + 'xxxlll'
  }
  link = link + link_part.slice(0, -3) + '%27' +';resolution:300'

 return new ImageLayer({
      opacity: 1,
      source: new ImageWMS({
        url: link,
        name:'layer_accessibility'
      })
  })
  
}



//Load Study Area
var study_area_url = ApiConstants.address_geoserver+'wfs?service=WFS&version=1.1.0&request=GetFeature&typeName=cite:study_area_union&srsname=EPSG:3857'

 var study_area = new VectorLayer({
 			      style: boundaryStyle,
            source: new VectorSource({
            url:study_area_url,
            format: new WFS()
      })    
});



layers.push(study_area);

//For all basemaps a filter excluding everything a part from the Study-Area is set.
var i;
study_area.getSource().on('change', function(e) {
	var f = study_area.getSource().getFeatures()[0]
	var mask = new Mask({ feature: f, inner:false, fill: new Fill({ color:[169,169,169,0.8] }) })
	for (i of layers){
		i.addFilter(mask);
	}
})

var addRemoveAccesibilityLayer = {	
  layer: null,	
  add : function (map){	
    if (this.layer != null) {	
      this.remove(map);	
    }	
    this.layer = accessibility_layer();	
    map.addLayer(this.layer);	
  },	
  remove : function (map){	
    map.removeLayer(this.layer);	
  }	
}

	
//EXPORT MODULAR FUNCTIONS
function GetBaseLayers(){
  return layers;
}

export {GetBaseLayers,addRemoveAccesibilityLayer};