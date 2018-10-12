import {GeoJSON,WFS,GML} from 'ol/format';
import {Vector as VectorLayer} from 'ol/layer';
import {Vector as VectorSource} from 'ol/source'; 
import ApiConstants from './secrets';	
import {bbox as bboxStrategy} from 'ol/loadingstrategy';
import {map} from './map';
import {iconStyle,drawing_style} from './style';
import Select from 'ol/interaction/Select';
import {Draw, Modify, Snap} from 'ol/interaction';
import { pointerMove} from 'ol/events/condition';
import {Stroke, Style} from 'ol/style';
import Feature from 'ol/Feature';
import {tool_tip} from './tooltip';
import {draw_isochrone} from './isochrones';
 	
const userid = Math.floor(Math.random() * 10000000);

var objectid; 	
var formatWFS = new WFS();
var formatGeoJSON = new GeoJSON();
var formatGML;
var number_calculations = 0;

var xs = new XMLSerializer();

var cql="userid="+userid.toString();
	
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////LineLineLine///////////////////////////////////////////////////////////////////////


var source_drawnLine = new VectorSource({
    loader: function (extent) {
        $.ajax(ApiConstants.address_geoserver+'wfs?', {
            type: 'GET',
            data: {
                service: 'WFS',
                version: '1.1.0',
                request: 'GetFeature',
                typename: 'cite:input_network',
                srsname: 'EPSG:3857',
                CQL_FILTER: cql
                //bbox: extent.join(',') + ',EPSG:3857'
            }
        }).done(function (response) {
            source_drawnLine.addFeatures(formatWFS.readFeatures(response));
            
        });
    },
    //strategy: ol.loadingstrategy.tile(ol.tilegrid.createXYZ()),
    strategy: bboxStrategy,
    projection: 'EPSG:3857'
});



var drawnLine = new VectorLayer({
    source: source_drawnLine,
   style: drawing_style
});

map.addLayer(drawnLine);



	
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////PointPointPoint///////////////////////////////////////////////////////////////////////
	
var sourceWFS_point = new VectorSource({
    loader: function (extent) {
        $.ajax(ApiConstants.address_geoserver+'wfs?', {
            type: 'GET',
            data: {
                service: 'WFS',
                version: '1.1.0',
                request: 'GetFeature',
                typename: 'cite:starting_point_isochrones',
                srsname: 'EPSG:3857',
                CQL_FILTER: cql
                //bbox: extent.join(',') + ',EPSG:3857'
            }
        }).done(function (response) {
            var resp = formatWFS.readFeatures(response);
            
            sourceWFS_point.addFeatures(resp);
        });
    },
    //strategy: ol.loadingstrategy.tile(ol.tilegrid.createXYZ()),
    strategy: bboxStrategy,
    projection: 'EPSG:3857'
});


	
var layerWFS_point = new VectorLayer({
    source: sourceWFS_point,
    style: iconStyle
});

map.addLayer(layerWFS_point);	



var interaction;

var interactionSelectPointerMove = new Select({
    condition: pointerMove
});

var interactionSelect = new Select({
    style: new Style({
        stroke: new Stroke({
            color: '#FF2828'
        })
    })
});
	
	
	

	

//wfs-t
var dirty = {};
var transactWFS = function (mode, f,formatGML,way_type) {
	
    var node;
    objectid = Math.floor(Math.random() * 10000000);
    var geometry = f.getGeometry().clone();
    geometry.transform("EPSG:3857", "EPSG:4326");

    var  newFeature = new Feature({	
		 
		userid : userid,                
        geometry: geometry,
        objectid:objectid,
        number_calculation:number_calculations + 1,
        way_type : way_type 
       
    });
    newFeature.setGeometryName("geometry");
    newFeature.setProperties(newFeature.getProperties());
    newFeature.setId(f.getId());
    

    switch (mode) {
        case 'insert':
            node = formatWFS.writeTransaction([newFeature], null, null, formatGML);       
            break;
        case 'update':
            node = formatWFS.writeTransaction(null, [newFeature], null, formatGML);
            break;
        case 'delete':
            node = formatWFS.writeTransaction(null, null, [newFeature], formatGML);
            break;
    }
    var payload = xs.serializeToString(node);
    $.ajax(ApiConstants.address_geoserver+'wfs', {
        type: 'POST',
        dataType: 'xml',
        processData: false,
        contentType: 'text/xml',
        data: payload
    }).done(function() {
        sourceWFS_point.clear();
        source_drawnLine.clear();
    });
};
	
$('button').click(function () {

    map.removeInteraction(interaction);
    interactionSelect.getFeatures().clear();
    map.removeInteraction(interactionSelect);

    switch ($(this).attr('class')) {

        case 'draw_way':

         //Define Format and table for POST
         	var way_type = this.id.replace('btn','');

			formatGML = new GML({
				featureNS: 'muc',
				featureType: 'cite:input_network'//,
				//srsName: 'EPSG:3857'
			});
	        
        
            interaction = new Draw({
                type: 'LineString',
                source: drawnLine.getSource()
            });
            var interactionSnap = new Snap({
    				source: drawnLine.getSource()
				});
            map.addInteraction(interaction);
            map.addInteraction(interactionSnap);
            interaction.on('drawend', function (e) {
                transactWFS('insert', e.feature,formatGML,way_type);
               
            });
            tool_tip(interaction,'line');
            break;
		 
		 case 'draw_isochrone':

				
		 //Define Format and table for POST
		 	
            formatGML = new GML({
    				featureNS: 'muc',
    				featureType: 'cite:starting_point_isochrones'//,
    			//	srsName: 'EPSG:3857'
			});
  
           
            interaction = new Draw({
               	type:'Point',
                source: layerWFS_point.getSource()
            });

           
           
            tool_tip(interaction,'point');
            var interactionSnap = new Snap({
    			source: layerWFS_point.getSource()
			});

            map.addInteraction(interaction);
            interaction.on('drawend', function (e) {
                transactWFS('insert', e.feature,formatGML);
                number_calculations = number_calculations + 1;
					 
                var feature=e.feature;
                map.removeInteraction(interaction);
                var coordinates = feature.getGeometry().getCoordinates();
                console.log(coordinates);
                var modus = document.getElementById('modus').value;
     	
 					if (modus=='double_calculation'){
 						var new_objectid = Math.floor(Math.random() * 10000000);
				
					   draw_isochrone(coordinates,new_objectid,objectid);  //A objectid for the second isochrone is created and the first objectid is used as parent_id 
 					   draw_isochrone(coordinates,objectid,1);		
	
 					}
 					else if (modus=="2"){
						draw_isochrone(coordinates,objectid,2);	     					
 					}
 					else{
            		draw_isochrone(coordinates,objectid,1);
            		
            	}
                	
            });
            	            
            break;
            
        case 'btnDelete':
    		formatGML = new GML({
				featureNS: 'muc',
				featureType: 'cite:input_network'//,
			//	srsName: 'EPSG:3857'
			});
				
            interaction = new Select();
            interaction.getFeatures().on('add', function (e) {
                transactWFS('delete', e.target.item(0),formatGML);
                interactionSelectPointerMove.getFeatures().clear();
                interaction.getFeatures().clear();
            });
            map.addInteraction(interaction);
            break;

        default:
            break;
    }
});
export {userid,number_calculations,layerWFS_point,drawnLine};





//http://212.83.58.36:8080/geoserver/wfs?service=WFS&version=1.1.0&request=GetFeature&viewparams=gid:xxx;&typeNames=cite:pois
/*
let extract_streets_url = ip_address +':3000/load_ways'
let data_extract_streets;
$.ajax({
        type: 'GET',     
        url: extract_streets_url,
        success: data => {                              
            data_extract_streets = data;
            
        }
});

let extract_streets = new ol.layer.Vector({
        style:boundaryStyle,
        source: new ol.source.Vector({
            url:extract_streets_url,
            format: new ol.format.GeoJSON({

            })
        })   

});



map.addLayer(extract_streets);



let selectInteraction = new ol.interaction.Select({
    layers: function(layer) {
        return layer.get('selectable') == true;
    }
});



let modifyInteraction = new ol.interaction.Modify({
    features: selectInteraction.getFeatures()
});

let snapInteraction = new ol.interaction.Snap({
    source: extract_streets.getSource()
});

let drawInteraction = new ol.interaction.Draw({
    type: 'LineString',
    source: extract_streets.getSource()
});





function deleteInteraction(evt){

    var feature = map.forEachFeatureAtPixel(evt.pixel,function (feature) {
        extract_streets.getSource().removeFeature(feature);
        console.log(feature.id);
    });
}

function addAttribute(evt){

    var feature = map.forEachFeatureAtPixel(evt.pixel,function (feature, extract_streets) {
        
        feature.set('type', 'modified');
        
    });
}

function send_streets_modified(){


    for (i of extract_streets.getSource().getFeatures()){

        console.log(i.getProperties().id+'    '+extract_streets.getSource().getFeatures()[0].getProperties().geom.v +'      '+extract_streets.getSource().getFeatures()[0].getProperties().type)



    }
}

copy_extract_streets=[];

$('.expert_draw').click(function () {
    if (copy_extract_streets.length==0){copy_extract_streets=extract_streets.getSource().getFeatures();} 
    let buttonID = this.id;

    map.removeInteraction(selectInteraction);
    map.removeInteraction(modifyInteraction);
    map.removeInteraction(snapInteraction);
    map.removeInteraction(drawInteraction);
    
   
    map.un('singleclick', deleteInteraction);

    if (buttonID == 'btnModify'){

       
        map.addInteraction(selectInteraction)
        map.addInteraction(modifyInteraction);
        map.addInteraction(snapInteraction);
        extract_streets.set('selectable', true);
        map.on('singleclick', addAttribute);

    }

    else if(buttonID == 'btnDraw'){

        
        map.addInteraction(drawInteraction);
        map.addInteraction(snapInteraction);

    }
    else{
        map.addInteraction(selectInteraction);
        map.removeInteraction(snapInteraction);
        map.on('singleclick', deleteInteraction);
    }
   

});

*/

