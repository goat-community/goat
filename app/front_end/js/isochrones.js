// Create the map 



const thematic_data = {};
var number_isochrone_default = 1;
var number_isochrone_input = 1;
const isochrones = {};
const network = {};
var vectorSource;
//////////////////////////////////////////////////////////////////
let draw_isochrone = function(coordinate_input,objectid,parent_id) {
	$('#mySpinner').addClass('spinner');
 	
 	const coordinates= ol.proj.transform([coordinate_input[0],coordinate_input[1]],'EPSG:3857','EPSG:4326');
	let modus = document.getElementById('modus').value;     	
 	

	if (modus=="double_calculation"){
		modus=2			
	}	     	
 	
  	let network_url =  address_geoserver+`wfs?service=WFS&version=1.1.0
  					   &request=GetFeature&viewparams=
  					   objectid:${objectid};
  					   modus:${modus};
  					   userid:${userid}
  					   &typeNames=cite:show_network`;

  	network_url = network_url.replace(/\s+/g, '');
  	
  	let save_isochrones_url = address_geoserver+`wfs?service=WFS&version=1.1.0
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

  	console.log(save_isochrones_url)
   
   	if (modus =='2' && parent_id != 1){
		save_isochrones_url = save_isochrones_url.replace('save_isochrones','save_isochrones_input');	  
		var layer_name = 'input_' + number_calculations.toString();     
   	}
   	else{
   
		var layer_name = 'default_' + number_calculations.toString(); 	       
   	}

  
 //Isochrone is calculated as SQL-View. The Layer is actually empty but the function at the DB is executed by map.addLayer(isochrone)
 //This work around has to be improved (NodeJS) 
  

	var isochrone = new ol.layer.Vector({
	    source: new ol.source.Vector({
	    	url:save_isochrones_url,

	    	format: new ol.format.WFS({

	    	})
	    })   
	       
	});


	map.addLayer(isochrone);

	// Listener is waiting until the layer is loaded 
	var listenerKey = isochrone.getSource().on('change', function(e) {
		
		
	    $('#mySpinner').removeClass('spinner'); //Spinner while calculation is done
		
		var text_calculation = $('#calculation_' + number_calculations.toString()).text();	
		if (text_calculation == ""){
		 	append_dropdown_slider(); 
		}		 	 
	 	 
	 	var type_calculation = layer_name.split('_')[0];
	 	
	 	 
	 	   
	    var  cql_isochrone = address_geoserver+'wfs?service=WFS&version=1.1.0&request=GetFeature&typeName=cite:isochrones&srsname=EPSG:3857&CQL_Filter=objectid='+objectid.toString();
	    
		var layer = new ol.layer.Vector({
			style:styleFunction1,
	        source: new ol.source.Vector({
	         			url:cql_isochrone,
	           	  		format: new ol.format.WFS({

	            	})
	        })
	    })    		    
	    
	    
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

		ol.Observable.unByKey(listenerKey);
		layerWFS_point.getSource().clear()
	});
};



$('#btnInsertintoNetwork').click(function () {
			
	
	$('#mySpinner').addClass('spinner');

	const InsertintoNetwork = new ol.layer.Vector({
    	source: new ol.source.Vector({
     				url:address_geoserver+"wfs?service=WFS&version=1.1.0&request=GetFeature&viewparams=userid:"+userid.toString()+"&typeNames=cite:insert_into_network",
        			format: new ol.format.WFS({
       		})
    	})   
       
	});

	map.addLayer(InsertintoNetwork);
	
	
	
	InsertintoNetwork.getSource().on('change', function(e) {
			$('#mySpinner').removeClass('spinner');	
			
			for (let i of drawnLine.getSource().getFeatures()){
				i.set('line_type','solid');
			}	    

	})

});

function network_style_default(feature, resolution) {
	
	const {modus} = feature;
	const level = feature.get('cost');   
	const speed = document.getElementById('travel_speed').value;   
				
	const color =  set_color(level/speed,color_diff_default,color_1_default);  
	const style = new ol.style.Style({
		stroke: new ol.style.Stroke({
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
		
	const style = new ol.style.Style({
    				stroke: new ol.style.Stroke({
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
	  
	const network_layer = new ol.layer.Vector({
	  	opacity:1,
	  	style: network_style,
		   source: new ol.source.Vector({
	     	url:network_url,
	        format: new ol.format.WFS({

	        })
	     })   
	       
	});	
	network[layer_name] = network_layer;

	
	map.addLayer(network_layer);

	const z_isochrones = isochrones[layer_name].getZIndex();
	
	isochrones[layer_name].setZIndex(z_isochrones+1); //Put isochrone above the network layer
	const z_network_layer = network[layer_name].getZIndex();
	network[layer_name].setVisible(false);

	const z_point = map.getLayers().a.length-1; //Put the point above the network layer
	layerWFS_point.setZIndex(z_point);
}


