    

var dropdown_slider;    
 
var append_dropdown_slider = function(){
 	var number = number_calculations.toString();
 	var radio_index = `<input type="radio" class="index_radio" name="index_input_number" value="speed" checked="checked">Speed [km/h]<br>
  	<input type="radio" class="index_radio" name="index_input_number" value="distance">Distance [m]<br>`
	
	var number = number_calculations.toString();
 	var radio_index = '<input type="radio" class="index_radio" name="index_input_'+number+'" value="speed" checked="checked">Speed [km/h]<br>'
  	+'<input type="radio" class="index_radio" name="index_input_'+number+'" value="distance">Distance [m]<br>'
	
	dropdown_slider =`<div class ="container" > 
	   <div class="header" id="calculation_${number}"><i class="fa fa-chevron-down" style="font-size:24px">
	   </i><span>Calculation ${number}</span> 			     
		<i class="cross_layer fa fa-times"  style="font-size:20px"></i>	     
	      <div id="checkbox_container_"> 
	     		<div id="checkbox_container_default_${number}"> 
	      	</div> 
	      	<div id="checkbox_container_input_${number}"> 
	      	</div>          
	    </div>
	    </div> 
	    <div class="header1" id="header_legend_${number}"><i class="fa fa-caret-right" style="font-size:24px"></i><span>Legend</span>		
	    </div>
	    <div class="content" id="content_legend_${number}"> 
	    	<div class="legend_container" id = "legend_container_${number}"> 
	    	</div>
	    </div>
	    <div class="header1" id="header_additional_layer_${number}"><i class="fa fa-caret-right" style="font-size:24px"></i><span>Additional Layer</span>
	    </div>
	    <div class="content" id="content_additional_layer_${number}">
			<div class="additional_layer_container" id = "additional_layer_container_default_${number}"> 
	    	</div>
	    	<div class="additional_layer_container" id = "additional_layer_container_input_${number}"> 
	    	</div>
	    </div>
	   <div class="header1" id="header_thematic_data_${number}"><i class="fa fa-caret-right" style="font-size:24px"></i><span>Thematic Data</span> 
	    </div>
	    <div class="content" id="content_thematic_data_${number}">    	
	</div>   
	<div class="header1" id="header_index_calculation_${number}"><i class="fa fa-caret-right" style="font-size:24px"></i><span>Calculation Accessibility Index</span>
	    </div>
	    <div class="content" id="content_index_calculation_${number}"><span style="margin-left:5px;"><b>Cost sensitivity parameter</b></span>
	    <input style="margin-left:5px;" type="text" id ="y_value_${number}" value="-0.1"><br>	
	    <button style="margin-left:5px;margin-bottom:5px;"id="btnIndex">Calculate</button>	  	    	
	    </div>
	</div>`


	
	
	
	header_array = ['header_legend_','header_additional_layer_','header_thematic_data_','header_index_calculation_'];
	content_array = ['content_legend_','content_additional_layer_','content_thematic_data_','content_index_calculation_'];
	
	

	$(".dropdown").append(dropdown_slider)
	
	$(".fa-chevron-down").click();
}











var categories_db_style = {
'Education':{'kindergarten':['kindergarten','Kindergarten'],'primary_school':['school-15','Primary school'],'secondary_school':['school-15','Secondary school']},
'Gastronomy':{'bar':['bar-15','Bar'],'biergarten':['biergarten','Biergarten'],'cafe':['cafe-15','Café'],'pub':['pub','Pub'],'fast_food':['fast-food-15','Fast food'],
'ice_cream':['ice-cream-15','Ice cream'],'restaurant':['restaurant-15','Restaurant']},
'Population':{'address':['','Addresses'],'population':['','Population']},
'Other':{'library':['library-15','Library'],'night_club':['night-club','Night-Club'],'recycling':['recycling-15','Recycling']},
'Transport':{'bicycle_rental':['bicycle-share-15','Bicycle rental'],'car_sharing':['car-15','Car sharing'],'charging_station':['charging-station','Charging station'],
'bus_stop':['bus-15','Bus'],'tram_stop':['rail-light-15','Tram station'],
'subway_entrance':['rail-metro-15','U-Bahn station'],'sbahn_regional':['rail-15','S-Bahn station'],'taxi':['taxi','Taxi']},
'Services':{'hairdresser':['hairdresser-15','Hairdresser'],'atm':['atm','ATM'],'bank':['bank-15','Bank'],'dentist':['dentist-15','Dentist']
,'doctors':['doctor-15','Doctor'],'pharmacy':['pharmacy-15','Pharmacy'],
'post_box':['post_box','Post box'],'post_office':['post-15','Post office'],'fuel':['fuel-15','Fuel']},
'Shop':{'alcohol':['alcohol-shop-15','Alcohol shop'],'bakery':['bakery-15','Bakery'],'butcher':['butcher','Butcher'],'clothes':['clothing-store-15','Clothing store']
,'convenience':['grocery-15','Convencience store']
,'greengrocer':['grocery-15','Greengrocer'],'kiosk':['marker-15','Kiosk'],'mall':['marker-15','Mall'],'shoes':['shoes','Shoes'],
'supermarket':['supermarket','Supermarket'],'marketplace':['marker-15','Marketplace']},
'TourismLeisure':{"cinema":['cinema-15','Cinema'],"theatre":['theatre-15','Theatre'],"museum":['museum-15','Museum'],"picnic_site":['picnic','Picnic-site'],
"hotel":['hotel','Hotel'],"hostel":['hostel','Hostel'],
"guest_house":['guest_house','Guest house'],"attraction":['attraction-15','Attraction']
,"viewpoint":['viewpoint','Viewpoint'],"gallery":['art-gallery-15','Gallery']}}



var pois ={};
for (i in categories_db_style){
	
		
	pois = Object.assign(pois,categories_db_style[i]);
}



var dictionary = {
	'input':'Scenario',
	'default' : 'Default'


}