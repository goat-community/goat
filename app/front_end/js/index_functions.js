
import {map} from './map';
import {pois,categories_db_style,dictionary,header_array,content_array} from './variables';
import {isochrones,network} from './isochrones';
import {addRemoveAccesibilityLayer} from './layers';
import {pois_geom} from './other_layers';
import {drawnLine} from './interaction';





let index_function = function () {
	  
 	 function isUneven(n) {
  		return n % 2 == 1;
	 } 
	 
	 //Is building the Thematic Data Selection
	 	
    $(document).ready(function(e) {
    	let keys_categories = Object.keys(categories_db_style);		
    	let thematic_select_html = '<div class="header" id="select_thematic_data" ><i class="fa fa-chevron-down" style="font-size:24px" ><span style="font-size:14px;font-family: Open Sans;margin-left:5px;">Select Thematic Data</span></i></div>';     
		
    	for (let key in keys_categories) {
    		let pre_html_thematic = `<div class="header1 category" id="select_${keys_categories[key]}"><i class="fa fa-caret-right" style="font-size:24px"></i>
    								<input type="checkbox" class ="filled-in thematic_check" id="check_${keys_categories[key]}" unchecked></input>
									<label for="check_${keys_categories[key]}">${keys_categories[key]}</label>
									</div>  	
									<div class="content" id="content_select_${keys_categories[key]}"><table class=table_item_select>content_replace</table></div> 
									</div>`  
								 
			thematic_select_html = thematic_select_html + pre_html_thematic.replace(/xxx/g,keys_categories[key])	    	     
			
			//It is building the table with the help of the object for thematic_data		
			let items_thematic_html='';	
			let array = Object.keys(categories_db_style[keys_categories[key]]).sort();		
			let row;			
			for (let key_1 in array){
				  let cell = `<input type="checkbox" class ="filled-in thematic_item_check thematic_item_checkShared" id="check_${array[key_1]}" unchecked></input>`
								  +`<label for="check_${array[key_1]}" style="padding-left:25px;height:16px;"></label>`
				  				  +`<img style="padding-right:5px;" for="check_${array[key_1]}" src="../pois/${pois[array[key_1]][0]}.png">`
			     				  +`<label style="cursor:pointer;" for="check_${array[key_1]}">${pois[array[key_1]][1]}</label>`	
								  + `<input name="n" class="thematic_data_weight"type="number" min="1" max="5" step="1" value="1"/>`
				  
				  if (isUneven(parseInt(key_1)+1)){
				  
				  	row = '<tr><td>xxx</td><td>yyy</td></tr>';
				  	row = row.replace('xxx',cell);
				  	
				  	if(parseInt(key_1)+1 == array.length){
				   		row = row.replace('yyy','');
				   		items_thematic_html = items_thematic_html + row;	
				  	}
				  }

				  else{
					row = row.replace('yyy',cell);
					items_thematic_html = items_thematic_html + row;				  
				  }
								
			}
    		
    		thematic_select_html = thematic_select_html.replace('content_replace',items_thematic_html);
    		
    	} 

    	$("#main_thematic_data").append(thematic_select_html);
	});
   
   	
	//Switching on an off the isochrones Layers
		
	$("body").on('change','.isochrones_check', function () { 
			let id = this.id;
			id = id.replace('isochrones_','')     		
			if (this.checked){		   			
				isochrones[id].setVisible(true); 	
			}
			else {	
				isochrones[id].setVisible(false); 
			}
	});


	//Toogle the the pois_elements if one category is clicked

	$("body").on('change','.category :checkbox', function () { 
		let category = this.id;
		let elements = Object.keys(categories_db_style[category.replace('check_','')]); //Selects the pois, which are belonging to one category 
		for (let i in elements){ 	
			$('#check_'+elements[i]).prop("checked", $('#'+category).is(":checked")); 	
		}
		if ($('#accessibility_basemap_select').val() != 'no_basemap'){
			addRemoveAccesibilityLayer.add(map);
  		}  
	});
	$('.thematic_item_checkShared').click(function(){
		
		var pid = $(this).parent().closest('div').attr('id');
		pid = pid.slice(pid.indexOf('_')+1,pid.length);
		console.log(pid);
		let category = pid.replace('select_','check_');
		let elements = Object.keys(categories_db_style[category.replace('check_','')]); //Selects the pois, which are belonging to one category 
		var len = elements.length,counter=0;
		for (let i in elements){ 	
			if($('#check_'+elements[i]).is(":checked")){
				counter++;
			} 	
		}
		if(counter == 0){
			$('#'+category).prop('checked',false);
		}
		else if(counter == len){
			$('#'+category).prop('checked',true);
		}
		else if(counter < len){
			$('#'+category).prop('checked',true);
		}
	});
	 
	 
	$("body").on('click','#toogle_left',function () {
		$('#controls').toggle("slide", { direction: "left" }, 1000);
	})		
	
	$("body").on('click','#toogle_right',function () {
		$('#container_right').toggle("slide", { direction: "right" }, 1000);
	})		
		
		
	//Toogles the network Layers	
	$("body").on('change','.network', function () { 
			let id = this.id;
    		id = id.replace('network_','')   		
    		if (this.checked){	
 			
				network[id].setVisible(true); 
    		} 			
				
			else {
				
    			network[id].setVisible(false);
			}
	});
	
	
	$("body").on('change','#input_network', function () { 
						
			
    		if (this.checked){		
				map.addLayer(drawnLine); 
    		} 			
				
			else {			
    			map.removeLayer(drawnLine);
			}
	});
	
	//Toogle function for the Select_thematic_data section
	$("body").on('click','.fa-chevron-right, .fa-chevron-down',function () {
		let keys_categories = Object.keys(categories_db_style);
		let id = $(this).parent().attr('id')
		$(this).toggleClass("fa-chevron-right fa-chevron-down");
		if (id == 'select_thematic_data'){	
			for (let key in keys_categories){
				$('#select_'+keys_categories[key]).toggle();					
				
			}
		}
		else{
		    let number = $(this).parent().attr('id').replace('calculation_','');
	var i;
			 //When clicked all the sub_headers and the content, which is visible is toogled  
			 for (i in header_array){
			 
			 	$('#'+header_array[i]+number).toggle();
			 	
			 	if($('#'+content_array[i]+number).is(':visible')){
		    		$('#'+content_array[i]+number).toggle()
		    		$('#'+header_array[i]+number).children('i').toggleClass("fa-caret-down fa-caret-right"); //Icon is also toogled
		   		}		  
			}

		}
	});




	$("body").on('click','.fa-caret-right, .fa-caret-down',function () {
	
    	var $header = $(this).parent();
    //getting the next element
    	var $content = $header.next();
    //open up the content needed - toggle the slide- if visible, slide up, if not slidedown.
		$(this).toggleClass("fa-caret-right fa-caret-down");    	
    	$content.slideToggle();


	});
}	


$(window).load(index_function);



//Removes the complete layer when cross of the calculation is
$("body").on('click','.cross_layer',function () {
	let layers = $(this).siblings().children().children()
	$.each(layers,function(key,value){
		let id = value.id.replace('isochrones_','')		

		
		map.removeLayer(isochrones[id])
		map.removeLayer(network[id])
		map.removeLayer(pois_geom[id])
	})
	let number = layers[0].id.split('_')[2];
	$('#calculation_'+number).parent().remove()
});