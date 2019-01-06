import {Icon,Circle as Circle, Fill, RegularShape, Stroke, Style, Text} from 'ol/style';


 

var defaultStyle_isochrones = new Style({
	  fill: new Fill({
	    color: [0, 0, 0, 0]
	  }),
	  stroke: new  Stroke({
	    color: '#0d0d0d',
	    width: 7
	  })
	});

var boundaryStyle = new Style({
	  fill: new  Fill({
	    color: [0, 0, 0, 0]
	  }),
	  stroke: new Stroke({
	    color: '#707070',
	    width: 5.5
	  })
	});
	

var vector_style = new Style({
				fill: new Fill({
					color: 'rgb(0, 102, 255)'
				}),
				stroke: new  Stroke({
					color: '#FF0000',
					width: 10
				}),
				image: new Circle({
					radius: 10,
					fill: new Fill({
						color: '#FF0000'
					})
				})
			});
			
		var colors_isochrones_input ={
					"1":'#22D329',
					"2":'#20C830',
					"3":'#1EBD38',
					"4":'#1CB340',
					"5":'#1AA848',
					"6":'#199E50',
					"7":'#179358',
					"8":'#158860',
					"9":'#137E68',
					"10":'#117370',
					"11":'#106977',
					"12":'#0E5E7F',
					"13":'#0C5487',
					"14":'#0A498F',
					"15":'#083E97',
					"16":'#07349F',
					"17":'#0529A7',
					"18":'#031FAF',
					"19":'#0114B7',
					"20":'#000ABF'    	    	
		    
		      };     
      
      var colors_isochrones_default = {
			"1":'#ffffe0',
			"2":'#fff2c7',
			"3":'#ffe4b1',
			"4":'#ffd69d',
			"5":'#ffc88e',
			"6":'#ffb981',
			"7":'#ffaa76',
			"8":'#ff9a6e',
			"9":'#fc8968',
			"10":'#f77a63',
			"11":'#f16b5f',
			"12":'#e95d5a',
			"13":'#e14f55',
			"14":'#d8404e',
			"15":'#cd3346',
			"16":'#c2263d',
			"17":'#b61832',
			"18":'#a80c25',
			"19":'#9b0316',
			"20":'#8b0000'    	    	
    
      };        
      
       
      var colors_way_types = {
       	'Bridge':'#4842f4',
       	'Street':'#f44141'
       }
      var color_diff_default = [6.10,13.42,11.789];
      var color_1_default = [255,255,224];
      var color_diff_input = [1.789,10.578,-9.631];
      var color_1_input = [34,211,41];

      function set_color(time,color_diff,color_1){
      	
      	if (time < 1){
      		var color = color_1
      	}
      	else{
      		let diff_time = time-1
      		var color = [color_1[0]-color_diff[0]*diff_time,color_1[1]-color_diff[1]*diff_time,color_1[2]-color_diff[2]*diff_time]      

      	}
      	return color
      }
  
      function drawing_style(feature, resolution) {
        let color = feature.get('way_type');
        let line_type = feature.get('line_type');
        if (line_type == 'solid'){
        	var dash_type = [1,1]

        }
        else{
        	dash_type=[10,10]
        }
        color = colors_way_types[color];
        let style = new  Style({
					  stroke: new  Stroke({
					    color: color,
					    width: 5,
					    lineDash: dash_type
					  })
					});
		  
	  
		  return [style];
      }    
		
 
    

        function iconStyle(feature, resolution) {
        		var number = feature.get('number_calculation');
        		var path = 'http://www.open-accessibility.org/accessibility/markers/marker-'+number+'.png';
		
				console.log(feature);

        var style = new  Style({
		      image: new  Icon(/** @type {olx.style.IconOptions} */ ({
		        anchor: [0.4, 40],
		        anchorXUnits: 'fraction',
		        anchorYUnits: 'pixels',
		        //opacity: 0.75,
		        src: path,
		        scale:0.5
		      }))})
		  
	  
		  return [style];
      }      
      
	var array_pois = [];	
	var _pois;
	var setStyle_pois = function (pois_geom,pois){
		array_pois = [];
		var thematic_selection = $("#main_thematic_data .content :checkbox:checked");
		for (var i=0; i < thematic_selection.length; i++){
			array_pois.push(thematic_selection[i].id.replace('check_',''));
			
		} 	
	
	  _pois = pois
		var j;
		for (j in pois_geom){
			pois_geom[j].setStyle(poisStyle); 
		}
	
	
	
	}
	
	
	function poisStyle(feature, resolution) {
			
				
				
			
        		var amenity = feature.get('amenity');
        		
        		if ($.inArray(amenity,array_pois) != -1){
					console.log(_pois);
					var amenity = _pois[amenity][0]
					console.log(amenity);
	        		
	        		var path = '../pois/'+amenity+'.png';
	        		
	        		var style = new  Style({
			      		image: new  Icon(/** @type {olx.style.IconOptions} */ ({
			       		//anchor: [0.4, 40],
			        anchorXUnits: 'fraction',
			        anchorYUnits: 'pixels',
			        src: path,
			        scale:1.5
			      }))})
		      }
		      
		      
		      else{
		      	style = defaultStyle_isochrones
		      
		      }
		  
	  
		  return [style];
      }      
      
      
       var styleCache_default = {};  
		 
		 var styleCache_input = {};
      
      
      

		
      function styleFunction1(feature, resolution) {
        // get the incomeLevel from the feature properties
        var level = feature.get('step');
        

		       
        var parent_id = feature.get('parent_id');
    	  var output;	
    	  //If the parent_id is one it is a default isochrone
        if (parent_id == 1){       
      	 
      		
				if (!styleCache_default[level]) {
          		styleCache_default[level] = new  Style({
            	stroke: new  Stroke({
	    				color: colors_isochrones_default[level],
	    				width: 5
         		 })   
         		    		    		       
        })
				      
        }
        		var output =   styleCache_default[level];
        }
        //If the parent_id is not one it is a input isochrone
        else{        
				
				if (!styleCache_input[level]) {
          		styleCache_input[level] = new  Style({
            	stroke: new Stroke({
	    				color: colors_isochrones_input[level],
	    				width: 5
         		 })          
        })
				        
        }
        		var output =   styleCache_input[level]; 
        }
 
        return [defaultStyle_isochrones,output];
			}  
			      
    var  styleCache_input_network = {};
    var  styleCache_default_network = {};
      
      function network_style(feature, resolution) {
        // get the incomeLevel from the feature properties
        var modus = feature.getProperties().modus;
        //let level = 1;
		var level = feature.get('cost');   
		var speed = document.getElementById('travel_speed').value;   
        
    	  //If the parent_id is one it is a default isochrone
        if (modus == 1 || modus == 3){       
      	 
      			
				var color =  set_color(level/speed,color_diff_default,color_1_default);  
          		var style = new Style({
            	stroke: new Stroke({
	    				color: `rgb(${Math.round(color[0])},${Math.round(color[1])},${Math.round(color[2])})`,
	    				width: 2
         			 	})   
         		})

        }
        		
        
        //If the parent_id is not one it is a input isochrone
        else {        

				var color =  set_color(level/speed,color_diff_input,color_1_input);  
				
				var style = new Style({
            	stroke: new Stroke({
	    				color: `rgb(${Math.round(color[0])},${Math.round(color[1])},${Math.round(color[2])})`,
	    				width: 2
         		 		})          
        		})
				        
        }
        		
        return style;
			}



	////////Ways Styling based on feature attributes//////////
			//Ways original features
			var waysDefaultStyle = new Style({
				fill: new  Fill({
					color: [0, 0, 0, 0]
				}),
				stroke: new Stroke({
					color: '#707070',
					width: 4
				})
			});
			//Ways modified features 
			var waysModifiedStyle = new Style({
				fill: new  Fill({
					color: [0, 0, 0, 0]
				}),
				stroke: new Stroke({
					color: '#FF0000',
					width: 4
				})
			});
			//Ways new Road features
			var waysNewRoadStyle = new Style({
				fill: new  Fill({
					color: [0, 0, 0, 0]
				}),
				stroke: new Stroke({
					color: '#6495ED',
					width: 4
				})
			});
			//Ways new Bridge features
			var waysNewBridgeStyle = new Style({
				fill: new  Fill({
					color: [0, 0, 0, 0]
				}),
				stroke: new Stroke({
					color: '#FFA500',
					width: 4
				})
			});
			function waysStyle (feature,resolution){
				var props = feature.getProperties();			
				if ((props.hasOwnProperty('type') && props['original_id'] == null) || Object.keys(props).length == 1){
					//Distinguish Roads from Bridge features
					if (props.type == 'bridge'){
						return[waysNewBridgeStyle]
					} else {
						return[waysNewRoadStyle];
					}
				} else if (!props.hasOwnProperty('original_id') && Object.keys(props).length > 1) {
					return [waysDefaultStyle]; //Features are from original table
				} else {
					return [waysModifiedStyle]; //Feature are modified
				}
			}    
      
  	export {boundaryStyle,styleFunction1,iconStyle,drawing_style,network_style,colors_isochrones_default,poisStyle,setStyle_pois,vector_style,waysStyle};