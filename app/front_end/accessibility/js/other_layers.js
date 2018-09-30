var reached_network_url = address_geoserver+'wfs?service=WFS&version=1.1.0&request=GetFeature&typeNames=cite:reached_network';
	       	



thematic_data_json = {};
var pois_geom ={};

$("body").on('click','#btnIndex',function (){
	$('#mySpinner').addClass('spinner');
	var radio_input = $(this).siblings(':radio:checked').val()
	var theurl = address_geoserver+'wfs?service=WFS&version=1.1.0&request=GetFeature&viewparams=gid:xxx;&typeNames=cite:thematic_data_json';

	
	var number = $(this).parent().attr('id').replace('content_index_calculation_',''); //Get the number of the calculation


	load_layer_gid(theurl,radio_input,'default_'+number);
	load_layer_gid(theurl,radio_input,'input_'+number);

	})
	
	


$("body").on('change','.pois_check',function (){
	
	var id = this.id.replace('show_pois_','');
	if ($(this).is(":checked")){
	
		
		var theurl = address_geoserver+'wfs?service=WFS&version=1.1.0&request=GetFeature&viewparams=gid:xxx;&typeNames=cite:pois';
	
		load_layer_gid(theurl,'pois',id);
			
		setStyle_pois();
	}
	else{		
		map.removeLayer(pois_geom[id])

	}
})





var prepare_loading = function (id,theurl) {
				var layers = thematic_data[id]
						
					var gid_list =[];	//Is checking for the gids of one calculation and pushing them into an array
					for (x in layers){
						gid_list.push(layers[x].gid)				
					}		
					
					var max_gid = Math.max.apply(null, gid_list); //The highest gid is taken as it is gid from isochrone with the highest step
					
					
				   var url = theurl.replace('xxx',max_gid)	
		
					//This should be changed and NodeJS should be used for thematic data 
					 var layer = new ol.layer.Vector({			//Layer is loaded
				      	opacity:1,
						style:poisStyle,
				        source: new ol.source.Vector({
				         	url:url,			
				        	format: new ol.format.WFS({
				
				            })
				         })   
							           
					})
					return layer
			}

var load_layer_gid = function (theurl,modus,id) {
			
			//The modus variable in the case of a calculation is filled with the input of the radio button (speed or distance)

			if (modus != 'pois' && id in thematic_data){ //if it is an index calculation the calculation function is called
				var layer = prepare_loading(id,theurl);				
				map.addLayer(layer)
				calculation(id,layer,modus);
			}
			
			else if(!(id in pois_geom)){ //if the id is not existing yet in the pois_geom object it is added to the object
					
				 var layer = prepare_loading(id,theurl);				
				 map.addLayer(layer)
				 
			    
				 pois_geom[id] = layer;	    
			   
			}
			else if (id in pois_geom){ //if the id is already existing in the pois geom object the layer is added again to the map
				map.addLayer(pois_geom[id])				
			}
			
}
	




var calculation = function (layer_id,layer,modus) {
	var array_pois = []	
	
	
	if(modus='speed'){
		var divider = parseInt($('#travel_speed').val())
	}
	else{
		var divider = 1;	
	}
	
	thematic_selection = $("#main_thematic_data .content :checkbox:checked");
	for (var i=0; i < thematic_selection.length; i++){
		array_pois.push(thematic_selection[i].id.replace('check_',''));
			
	} 	
	
	var number = layer_id.split('_')[1];
	
	var listenerKey1 = layer.on('change', function(e) {  //Listener waits until PoisJson is loaded
		var y = $('#y_value_'+number).val();		
		
		var features = layer.getSource().getFeatures();		
			
		
		var feature = features[0].getProperties();
			//feature.population = JSON.parse(feature.population); //Text is converted to Javascript Object (Note Geoserver not supporting JSONB)
		feature.pois_isochrones = JSON.parse(feature.pois_isochrones); 		
		
		layer_id = layer_id + '_json'	
		thematic_data[layer_id] = feature;	//Data is saved in thematic_data_json objectd
		

		

		var index_pois = 0;
		
		for (var x=0; x < array_pois.length; x++){				
			var array_objects = feature.pois_isochrones;
			var index_part = 0;		
				for (var z=0; z < array_objects.length; z++){
						
					if (array_objects[z].amenity == array_pois[x]){  //Selects and calculates the accessibility for those selected
						index_part =  index_part +  Math.pow(Math.E,y*(array_objects[z].cost/divider))
								
					}
						
				}
			index_pois = index_pois + index_part		
		}	
		thematic_data[layer_id]['index_pois']	= index_pois;			
		var index_html = '<br>'+layer_id.split('_')[0]+'(y = '+y.toString()+'): '+index_pois.toFixed(2).toString() //selects the word default or input + rounds
		$('#content_index_calculation_'+number).append(index_html)	
		$('#mySpinner').removeClass('spinner');																																														 
	}) 		
}



	
	
	