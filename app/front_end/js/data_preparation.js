import {pois} from './variables';
import {isochrones} from './isochrones';
import {colors_isochrones_default,colors_isochrones_input} from './style';
import ApiConstants from './secrets';
import {GeoJSON} from 'ol/format';
var FileSaver = require("file-saver");
var JsZip = require("jszip");


const thematic_data = {};
$("body").on('click','.fa-chevron-right',function () {	
	var ids = [];
	
	
	$(this).siblings('div').find('.isochrones_check').map(function () {	//Finds ids and pushes them into an array
	 	    
     ids.push(this.id.replace('isochrones_',''));
	})
	
	var time_steps = [];	
	
	$.each(ids,function (key,value) {
		
		 if (value in thematic_data == false){			//Check if the the thematic data was already added to the object
			 var features = isochrones[value].getSource().getFeatures();
			 
			 var relevant_features = [];
			 //set time_steps to [] otherwise steps are added twice of double calculation
			 time_steps = [];
			 $.each(features,function (key1,value1) {
	
			  		relevant_features.push(value1.getProperties());
			  		time_steps.push(value1.getProperties().step)
		
			 })
			 thematic_data[value]= relevant_features;
	    }  	   
	})
	
	if (time_steps.length > 0){
		create_dropdown(time_steps,ids);	 
    
	}  	

})



//Legend + Dropdown    
var create_dropdown = function(time_steps,ids){
	var number = ids[0].split('_')[1]
  	var title = '<option value="" selected disabled hidden>Choose here</option>'
	var legend = '';      
	time_steps = time_steps.sort((a, b) => a - b);
  	var dropdown = '<select style="margin-left:7px;" class ="dropdown_thematic" id=isochrone_'+ number+'>'+title
	$.each(time_steps,function(key,value){
		var id = parseInt(key) + 1
		value = value.toString();
		  	dropdown = dropdown + '<option value="'+id.toString()+'">'+value+' min'
		 	
			 var colors = '<div class="legend_item" style="margin-left: 7px;margin-right: 7px;width:50px;height:20px;border:2px solid #000;background-color:'+colors_isochrones_default[value]+';"></div>'
			 if (key == 0 && ids.length != 2){
				 var label = '<span style="margin-left: 7px;margin-right: 7px;font-weight: bold;">Default</span><br>'
				 colors = label + colors;
			 }
		if (ids.length == 1 && ids[0].includes('input')){
			var colors = '<div class="legend_item" style="margin-left: 7px;margin-right: 7px;width:50px;height:20px;border:2px solid #000;background-color:'+colors_isochrones_input[value]+';"></div>'
			if (key == 0){
				var label = '<span style="margin-left: 7px;margin-right: 7px;font-weight: bold;">Scenario</span><br>'
				colors = label + colors;
			}
		}
		if (ids.length == 2){ //If two calculations are done the color get displayed next to each other
			var inputDiv = '<div class="legend_item"  style="margin-left: 7px;margin-right: 7px;width:50px;height:20px;border:2px solid #000;background-color:'+colors_isochrones_input[value]+';"></div>'
			colors = colors + inputDiv;
			if (key == 0){
				var label = '<span style="margin-left: 7px;margin-right: 7px;font-weight: bold;">Default</span><span style="margin-left: 7px;margin-right: 7px;font-weight: bold;">Scenario</span><br>'
				colors = label + colors;
			}		
		}		
			  	
		if (key == 0){
			var legend_item = colors+'<span>'+value+' minutes</span><br>'	 
		} else {
			var legend_item = 	'<br>'+colors+'<span>'+value+' minutes</span><br>'	 
		}
		  
		   	legend = legend + legend_item
			
	})

	dropdown =dropdown + '</select>'
	$("#content_thematic_data_"+number).append(dropdown);
	$("#legend_container_"+number).append(legend);
}

function downloadFn (objectid,outputformat){
	//var  cql_isochrone = ApiConstants.address_geoserver+'wfs?service=WFS&version=1.1.0&request=GetFeature&typeName=cite:isochrones&outputFormat='+outputformat+'&srsname=EPSG:3857&CQL_Filter=objectid='+objectid.toString();
	var  cql_isochrone = ApiConstants.address_geoserver+'wfs?service=WFS&version=1.1.0&request=GetFeature&viewparams=objectid:'+objectid.toString()+'&typeName=cite:download_isochrones&outputFormat='+outputformat+'&srsname=EPSG:4326';
	var  ways = ApiConstants.address_geoserver+'wfs?service=WFS&version=1.1.0&request=GetFeature&viewparams=objectid:'+objectid+'&typeNames=cite:download_reached_network&outputFormat='+outputformat+'&srsname=EPSG:4326';
	var extension;
		if (outputformat == 'application/json' ){
			extension = 'json'
		} else {
			extension = 'zip'
		}
	//Fetch Isochrones Request
	var IsochronesReq = fetch(cql_isochrone,{
		method: 'GET',
	}).then(function(response){
		return response.blob();
	});
	
	//Fetch Ways Request
	var WaysReq = fetch(ways,{
		method: 'GET',
	}).then(function(response){
		return response.blob();
	});
	Promise.all([IsochronesReq,WaysReq]).then(function(values){
		var zip = new JsZip();
		var isochrones = values[0]; 
		zip.file("isochrones."+objectid+"."+extension, isochrones);
		var ways = values[1];
		zip.file("network."+objectid+"."+extension, ways);

		zip.generateAsync({type:"blob"})
			.then(function(content) {
				FileSaver.saveAs(content, "results_"+extension+"."+objectid+"."+"zip");
			});
	});	
}
   
$("body").on('change','.dropdown_thematic',function () {

	if (this.id.toString().indexOf('select_dowload_format') > -1){
		var objId = this.id.split('.')[1];
		var outputFormat;
		if (this.value == 1){
			outputFormat = 'application/json'
		} else {
			outputFormat = 'shape-zip'
		}
		downloadFn(objId,outputFormat);
		return;
	}


   var counter = this.id.replace('isochrone_','')

   var id = parseInt($(this).val())
   $("#table_thematic_data_"+counter).remove();
   var keys_feature;		

		
		//Depending on the modus the input data for the table is selected 
	if ('default_'+counter in thematic_data){     	
		var one_object_default = $.grep(thematic_data['default_'+counter], function(element){ return element.id == id; })	//The object with the right calculation time is selected
			one_object_default = JSON.parse(one_object_default[0].sum_pois);
			var keys_feature = Object.keys(one_object_default);
	}
   	if ('input_'+counter in thematic_data){     		
   	var one_object_input = $.grep(thematic_data['input_'+counter], function(element){ return element.id == id; })
		one_object_input = JSON.parse(one_object_input[0].sum_pois);
		var keys_feature = Object.keys(one_object_input);
   	}
	   
	var thematic_selection = $("#main_thematic_data .content :checkbox:checked");
	var array_pois = [];


	for (var i=0; i < thematic_selection.length; i++){
								
		var poi = thematic_selection[i].id.replace('check_','')
		if (keys_feature.includes(poi)){
			array_pois.push(poi);
		
		}				
					
			
	} 	

	keys_feature = array_pois;       
    keys_feature.push('population')   
	var attribute = ''
	var extra_column = ''

	//Depending on the input data the table is created & Keep old loop
	for (var element in keys_feature){
		console.log(keys_feature)
		if (('default_'+counter) in thematic_data && ('input_'+counter) in thematic_data){
			
			attribute = attribute + '<tr>'+'<td>'+pois[keys_feature[element]][1]+'</td>' +'<td>'+one_object_default[keys_feature[element]]+'</td>'+'<td>'+one_object_input[keys_feature[element]]+'</td>'+ '</tr>'
			extra_column = '<th>Scenario</th>'				
		}				
		else if ('default_'+counter in thematic_data){     		
		   	attribute = attribute + '<tr>'+'<td>'+pois[keys_feature[element]][1]+'</td>' +'<td>'+one_object_default[keys_feature[element]]+'</td>'+ '</tr>'
	   	}
	   	else if ('input_'+counter in thematic_data){     		
				attribute = attribute + '<tr>'+'<td>'+pois[keys_feature[element]][1]+'</td>' +'<td>'+one_object_input[keys_feature[element]]+'</td>'+ '</tr>'
	
		}	
    			    
	}
	attribute = attribute.replace('undefined','-');
	var table = '<table id="table_thematic_data_'+counter+'"><tr><th>Point of Interest</th><th>Default</th>'+extra_column+'</tr>' + attribute +'</table>'
	
	$('#content_thematic_data_'+counter).append($(table));
		
})

export {thematic_data};
   
    
