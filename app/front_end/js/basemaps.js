

var oepnv_attribution = '<a href="https://memomaps.de/">memomaps.de</a> <a href="http://creativecommons.org/licenses/by-sa/2.0/">'
                    		+'CC-BY-SA</a>, map data <a href="http://openstreetmap.org/">'
                    		+'Openstreetmap</a> <a href="http://opendatacommons.org/licenses/odbl/1.0/">ODbL</a>'


var center = ol.proj.transform([x,y], 'EPSG:4326', 'EPSG:3857');
var styles = ["OSM-Standard","OSM-Carto-DB-Light","OSM-Carto-DB-Dark"];


urls = ['http://{a-c}.tile.openstreetmap.org/{z}/{x}/{y}.png','http://{a-c}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png','http://{a-c}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png'];

var layers = [];
var i, ii;
for (i = 0, ii = styles.length; i < ii; ++i) {
  layers.push(new ol.layer.Tile({
      visible: false,
      preload: Infinity,
      source: new ol.source.OSM({
      "url": urls[i],
      imagerySet: styles[i],

      maxZoom: 19

    })
  }));
}


var bingmaps = new ol.layer.Tile({
    visible: false,
    preload: Infinity,
    source: new ol.source.BingMaps({
      key: bingmaps_key,
      imagerySet: 'Aerial',
      maxZoom: 19

    })
  });

layers.push(bingmaps);
styles.push('Aerial');




var mapbox = new ol.layer.Tile({
	source: new ol.source.XYZ({
	url: 'https://api.mapbox.com/styles/v1/mapbox/streets-v10/tiles/256/{z}/{x}/{y}?access_token='+mapbox_key
	})
})

layers.push(mapbox);
styles.push('Mapbox');


var oepnv_karte = new ol.layer.Tile({
//extent: [-20037508,-20037508,20037508,20037508],
visible: false,
preload: Infinity,
source: new ol.source.XYZ({
	attributions: oepnv_attribution,
  url:"https://tileserver.memomaps.de/tilegen/{z}/{x}/{y}.png",
  maxZoom:18,
  })
 })

layers.push(oepnv_karte);
styles.push('PublicTransport');




var map = new ol.Map({
  layers: layers,
  loadTilesWhileInteracting: true,
  target: 'map',
  view: new ol.View({
    center: center,
    zoom: 14
  })
});


//$('#mapbox').toggle();

//layers[0].setVisible(styles[0]);



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

var layer_accessibility;

var numbers = {'1':'one','2':'two','3':'three','4':'four','5':'five'}





var accessibility_layer = function(){

  let heatmap_input ={};
  let select_heatmap_input = $('#main_thematic_data .content :checkbox:checked')
  let link = address_geoserver+'cite/wms?service=WMS&version=1.1.0&request=GetMap&layers=cite:heatmap&LAYERS=cite%3Aheatmap&viewparams=amenities:%27'

 
  let link_part = '' 
  for (var i=0; i < select_heatmap_input.length; i++){

    link_part = link_part + "eeeppp" + select_heatmap_input[i].id.replace('check_','') + 'cccttt' + numbers[$(select_heatmap_input[i]).next().next().val()] + 'xxxlll'

  }
  link = link + link_part.slice(0, -3) + '%27' +';resolution:300'

  layer_accessibility = new ol.layer.Image({
      opacity: 1,
      source: new ol.source.ImageWMS({
        url: link,
        name:'layer_accessibility'
      })
  })
  
}




/*Çhange resolution accessibility_layer when zoomed

map.getView().on('propertychange', function(e) {
   if ($('#accessibility_basemap_select').val() != 'no_basemap'){
     switch (e.key) {
        case 'resolution':
          console.log(e.oldValue);
          map.removeLayer(layer_accessibility);
          accessibility_layer();
          map.addLayer(layer_accessibility);
          break
      }
    }
});

*/


$('body').on('change','.thematic_data_weight, .thematic_item_check',function(){
  console.log(this.class)
  if ($('#accessibility_basemap_select').val() != 'no_basemap'){
    map.removeLayer(layer_accessibility);
    accessibility_layer();
    map.addLayer(layer_accessibility);
  }  

})




$('body').on('change','#accessibility_basemap_select',function(){
  let style = this.value;
  if (style != 'no_basemap'){
    accessibility_layer();
    
    map.addLayer(layer_accessibility)
    //layer_accessibility.set('name', 'layer_accessibility');
  }
  else{
    map.getLayers().forEach(function (layer) {
    if (layer.get('name') != undefined & layer.get('name') === 'layer_accessibility') {
        map.removeLayer(layer_accessibility);
    }
    });
  }
  
});








////////Ol3-ext Photon Address
var search = new ol.control.SearchPhoton(
{	//target: $(".options").get(0),
	lang:"en",		// Force preferred language
	position: true	// Search, with priority to geo position
});
map.addControl (search);

// Select feature when click on the reference index
search.on('select', function(e)
{	
	map.getView().setCenter(e.coordinate);
	map.getView().setZoom(18);
	
});

//Load Study Area
 var study_area = address_geoserver+'wfs?service=WFS&version=1.1.0&request=GetFeature&typeName=cite:study_area_union&srsname=EPSG:3857'
 var study_area = new ol.layer.Vector({
 			style:boundaryStyle,
            source: new ol.source.Vector({
      			url:study_area,
	
        		format: new ol.format.WFS({

        		})
      })   
        
});


map.addLayer(study_area);

//For all basemaps a filter excluding everything a part from the Study-Area is set.
study_area.getSource().on('change', function(e) {
	var f = study_area.getSource().getFeatures()[0]
	var mask = new ol.filter.Mask({ feature: f, inner:false, fill: new ol.style.Fill({ color:[169,169,169,0.8] }) })

	for (i of layers){
		i.addFilter(mask);
	}
})


		

