import {transform} from 'ol/proj';
import {map} from './map';
import ApiConstants from './secrets';
import {styleFunction1,network_style} from './style';
import {Vector as VectorLayer} from 'ol/layer';
import {Vector as VectorSource} from 'ol/source';
import {GeoJSON, WFS} from 'ol/format';
import {Stroke, Style} from 'ol/style';
import {userid,number_calculations,layerWFS_point,drawnLine} from './interaction';
import {append_dropdown_slider,dictionary} from './variables';




var number_isochrone_default = 1;
var number_isochrone_input = 1;
const isochrones = {};
const network = {};

console.log(userid)

//////////////////////////////////////////////////////////////////
let draw_isochrone = function(coordinate_input,objectid,parent_id) {
	$('#mySpinner').addClass('spinner');
 	
 	const coordinates= transform([coordinate_input[0],coordinate_input[1]],'EPSG:3857','EPSG:4326');
	let modus = document.getElementById('modus').value;     	
 	
       	/*
	modus = 1 (default calculation)
	modus = 2 (input calculation)
	modus = 3 (double calculation - default)
	modus = 4 (double calculation - input)
	*/ 

	if (modus == "double_calculation" && parent_id == 1){
		modus = '3'			
	}
	else if (modus == "double_calculation"){
		modus = '4'
	} 	
 	
	let network_url =  ApiConstants.address_geoserver+`wfs?service=WFS&version=1.1.0
						&request=GetFeature&viewparams=
						objectid:${objectid};
						modus:${modus}
						&typeNames=cite:show_network`;

  	network_url = network_url.replace(/\s+/g, '');
  	
	let save_isochrones_url = ApiConstants.address_geoserver+`wfs?service=WFS&version=1.1.0
						&request=GetFeature&viewparams=
						userid_input:${userid};
						minutes:${document.getElementById('max_traveltime').value};
						x:${coordinates[0]};
						y:${coordinates[1]};
						steps:${document.getElementById('steps_isochrones').value};
						speed:${document.getElementById('travel_speed').value};
						concavity:${document.getElementById('concavity').value};
						modus:${modus};
						objectid_input:${objectid};
						parent_id:${parent_id}
						&typeNames=cite:save_isochrones`;

  	save_isochrones_url = save_isochrones_url.replace(/\s+/g, '');

	


   	if (modus == 2 || modus == 4 ){
		//save_isochrones_url = save_isochrones_url.replace('save_isochrones','save_isochrones_input');	  
		var layer_name = 'input_' + number_calculations.toString();     
   	}
   	else{
   
		var layer_name = 'default_' + number_calculations.toString(); 	       
   	}

  
 //Isochrone is calculated as SQL-View. The Layer is actually empty but the function at the DB is executed by map.addLayer(isochrone)
 //This work around has to be improved (NodeJS) 
  

	var isochrone = new VectorLayer({
	    source: new VectorSource({
	   // 	url:save_isochrones_url,
		//	format: new GeoJSON()
	    	format: new WFS({

	    	})
		}),
		zIndex: 10  
	       
	});
	

	map.addLayer(isochrone);
	
	fetch(save_isochrones_url, {
		method: 'GET',
	}).then(function (response) {
		isochrone_load_fn ();
	//	return response.json();
	}).then(function (json) {
		//var features = new ol.format.GeoJSON().readFeatures(json);
	});


function isochrone_load_fn (){

		
	    $('#mySpinner').removeClass('spinner'); //Spinner while calculation is done
		
		var text_calculation = $('#calculation_' + number_calculations.toString()).text();	
		if (text_calculation == ""){
		 	append_dropdown_slider(); 
		}		 	 
	 	var type_calculation = layer_name.split('_')[0];
	    var  cql_isochrone = ApiConstants.address_geoserver+'wfs?service=WFS&version=1.1.0&request=GetFeature&typeName=cite:isochrones&srsname=EPSG:3857&CQL_Filter=objectid='+objectid.toString();
		var layer = new VectorLayer({
			style:styleFunction1,
	        source: new VectorSource({
						 url:cql_isochrone,
						// format: new GeoJSON(),
	           	  		format: new  WFS({

	            	})
			}),
			zIndex: 10 
		})
		
		
		layer.once('render', function(event) {
			//If Modus is double calculation this event will fire once // for the last layer 'default'
			
			if (layer.getVisible()) {
				if(document.getElementById('modus').value == 'double_calculation')
				{
					layer.rendered = true;
					var defaultLayerObj = isochrones['default_'+layer_name.split('_')[1]];
					var inputLayerObj = isochrones['input_'+layer_name.split('_')[1]];
					//Check if both layer are rendered
					if (!(defaultLayerObj.hasOwnProperty('rendered') && inputLayerObj.hasOwnProperty('rendered'))){
						return;
					}
				}
				//Expand Right Panel on Layer Render
				$("#calculation_"+number_calculations).children().first().click();
				$("#header_legend_"+number_calculations).children().first().click();
			}
		});
		
		//The isochrones are loaded directly from the isochrones table. Note there was an issue with incorrect geometries when loaded directly from SQL-View
		isochrones[layer_name] = layer
		map.addLayer(isochrones[layer_name]);
		show_network(network_url,layer_name);
		var checkbox_layer = `<input type="checkbox" class ="filled-in isochrones_check" name="isochrones_${type_calculation}" 
							  id="isochrones_${layer_name}" checked></input> 
	 						  <label style="color: white !important;"for="isochrones_${layer_name}">${dictionary[type_calculation]}</label>`	

	 	$('#checkbox_container_'+layer_name).append(checkbox_layer);			
		
		var checkbox_network = `<b>${type_calculation}</b><br>
								<input style="margin-left:7px;" type="checkbox"  class ="filled-in network" name="network_${type_calculation}"  
								id="network_${type_calculation}_${number_calculations}" unchecked/><label for="network_${type_calculation}_${number_calculations}">Network</label>`;		
	   

	    $("#additional_layer_container_"+type_calculation+'_'+number_calculations).append(checkbox_network);	
	    var checkbox_pois = `<input style="margin-left:7px;" type="checkbox" class="filled-in pois_check" id="show_pois_${type_calculation}_${number_calculations}"/>
	   						<label for="show_pois_${type_calculation}_${number_calculations}">POIs</label>`
		$("#additional_layer_container_"+type_calculation+'_'+number_calculations).append(checkbox_pois)
	//	Observable.unByKey(listenerKey);
		layerWFS_point.getSource().clear();
}

};



$('#btnInsertintoNetwork').click(function () {
			
	
	$('#mySpinner').addClass('spinner');

	const InsertintoNetwork = new VectorLayer({
    	source: new VectorSource({
				url:ApiConstants.address_geoserver+"wfs?service=WFS&version=1.1.0&request=GetFeature&viewparams=userid:"+userid.toString()+"&typeNames=cite:network_modification",
					format: new WFS({
       		})
    	})   
       
	});

	map.addLayer(InsertintoNetwork);
	
	
	
	InsertintoNetwork.getSource().on('change', function(e) {
			$('#mySpinner').removeClass('spinner');	
			/*
			for (let i of drawnLine.getSource().getFeatures()){
				i.set('line_type','solid');
			}	    
			*/
	})

});

function network_style_default(feature, resolution) {
	
	const {modus} = feature;
	const level = feature.get('cost');   
	const speed = document.getElementById('travel_speed').value;   
				
	const color =  set_color(level/speed,color_diff_default,color_1_default);  
	const style = new Style({
		stroke: new Stroke({
			color: `rgb(${Math.round(color[0])},${Math.round(color[1])},${Math.round(color[2])})`,
			width: 2
	 	})   
	})

	return style;
}        

function network_style_input(feature, resolution) {

	const {modus} = feature;
	const level = feature.get('cost');   
	const speed = document.getElementById('travel_speed').value; 

	const color =  set_color(level/speed,color_diff_input,color_1_input);  
		
	const style = new Style({
    	stroke: new Stroke({
			color: `rgb(${Math.round(color[0])},${Math.round(color[1])},${Math.round(color[2])})`,
			width: 2
 		})          
	})	


	return style;	
}

var show_network = function(network_url,layer_name){
	if (layer_name.includes('default')){
		const network_style = network_style_default;
	}
	else{
	  	const network_style = network_style_input;
	}
	  
	const network_layer = new VectorLayer({
	  	opacity:1,
	  	style: network_style,
		   source: new VectorSource({
			 url:network_url,
			// format: new GeoJSON()
	        format: new  WFS({

	        })
	     })   
	       
	});	
	network[layer_name] = network_layer;

	
	map.addLayer(network_layer);

	const z_isochrones = isochrones[layer_name].getZIndex();
	
	isochrones[layer_name].setZIndex(z_isochrones+1); //Put isochrone above the network layer
	const z_network_layer = network[layer_name].getZIndex();
	network[layer_name].setVisible(false);


	console.log(map.getLayers().getLength());	
	const z_point = map.getLayers().getLength()-1; //Put the point above the network layer
	layerWFS_point.setZIndex(z_point);
}


export {draw_isochrone,isochrones,network};