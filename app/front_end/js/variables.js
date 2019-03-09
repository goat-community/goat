import {number_calculations,dynamicVars} from './interaction';

var dropdown_slider;    
var header_array = ['header_legend_','header_additional_layer_','header_thematic_data_','header_index_calculation_','header_download_data_'];
var content_array = ['content_legend_','content_additional_layer_','content_thematic_data_','content_index_calculation_','content_download_data_'];

var append_dropdown_slider = function(){
 	var number = number_calculations.toString();
 	var radio_index = `<input type="radio" class="index_radio" name="index_input_number" value="speed" checked="checked">Speed [km/h]<br>
  	<input type="radio" class="index_radio" name="index_input_number" value="distance">Distance [m]<br>`
	
	var number = number_calculations.toString();
 	var radio_index = '<input type="radio" class="index_radio" name="index_input_'+number+'" value="speed" checked="checked">Speed [km/h]<br>'
  	+'<input type="radio" class="index_radio" name="index_input_'+number+'" value="distance">Distance [m]<br>'
	
	dropdown_slider =`<div class ="container" > 
	   <div class="header" id="calculation_${number}"><i class="fa fa-chevron-down" style="font-size:24px">
	   <span class="calculationTreeItems" style="font-weight: bold;font-size: 16px;">Calculation ${number}</span></i>			     
		<i class="cross_layer fa fa-times"  style="font-size:20px"></i>	     
	      <div id="checkbox_container_"> 
	     		<div id="checkbox_container_default_${number}"> 
	      	</div> 
	      	<div id="checkbox_container_input_${number}"> 
	      	</div>          
	    </div>
	    </div> 
	    <div class="header1" id="header_legend_${number}"><i class="fa fa-caret-right" style="font-size:24px"><span class="calculationTreeItems">Legend</span></i>	
	    </div>
	    <div class="content" id="content_legend_${number}"> 
	    	<div class="legend_container" id = "legend_container_${number}"> 
	    	</div>
	    </div>
	    <div class="header1" id="header_additional_layer_${number}"><i class="fa fa-caret-right" style="font-size:24px"><span class="calculationTreeItems">Additional Layer</span></i>
	    </div>
	    <div class="content" id="content_additional_layer_${number}">
			<div class="additional_layer_container" id = "additional_layer_container_default_${number}"> 
	    	</div>
	    	<div class="additional_layer_container" id = "additional_layer_container_input_${number}"> 
	    	</div>
	    </div>
	   <div class="header1" id="header_thematic_data_${number}"><i class="fa fa-caret-right" style="font-size:24px"><span class="calculationTreeItems">Thematic Data</span></i>
	    </div>
	    <div class="content" id="content_thematic_data_${number}">    	
	</div> 
	
	<div class="header1" id="header_index_calculation_${number}"><i class="fa fa-caret-right" style="font-size:24px"><span class="calculationTreeItems">Calculation Accessibility Index</span></i>
	    </div>
	    <div class="content" id="content_index_calculation_${number}"><span style="margin-left:5px;"><b>Cost sensitivity parameter</b></span>
	    <input style="margin-left:5px;" type="text" id ="y_value_${number}" value="-0.1"><br>	
	    <a class="waves-effect waves-light btn btnCustom" style="visibility: visible; width:auto !important; font-size: 13px !important;margin-left:5px !important;margin-bottom:5px !important;padding-right: 3px !important; padding-left: 3px !important;" id="btnIndex">Calculate</a>	  	    	
		</div>

	<div class="header1" id="header_download_data_${number}"><i class="fa fa-caret-right" style="font-size:24px"><span class="calculationTreeItems">Download Isochrones and Ways</span></i> 
	</div>
	<div class="content" id="content_download_data_${number}">
	<select style="margin-left:7px; margin-bottom: 5px;" class="dropdown_thematic" id="select_dowload_format.${dynamicVars.objectid}">
		<option value="" selected="" disabled="" hidden="">Choose format</option>
		<option value="1">JSON</option>
		<option value="2">Shapefile</option>
	</select>
	</div>	

	</div>`


	$(".dropdown").append(dropdown_slider)
	
	$(".fa-chevron-down").click();

}



var categories_db_style = {
'Education':{'kindergarten':['kindergarten','Kindergarten'],'primary_school':['primary_school','Primary school'],'secondary_school':['secondary_school','Secondary school'],'library':['library','Library']},
'Food___Drink':{'bar':['bar','Bar'],'biergarten':['biergarten','Biergarten'],'cafe':['cafe','Café'],'pub':['pub','Pub'],'fast_food':['fast_food','Fast food'],
'ice_cream':['ice_cream','Ice cream'],'restaurant':['restaurant','Restaurant'],'nightclub':['nightclub','Night-Club']},
'Transport':{'bicycle_rental':['bicycle_rental','Bicycle rental'],'car_sharing':['car_sharing','Car sharing'],'charging_station':['charging_station','Charging station'],
'bus_stop':['bus_stop','Bus'],'tram_stop':['tram_stop','Tram Stop'],
'subway_entrance':['subway_entrance','U-Bahn station'],'rail_station':['rail_station','Rail Station'],'taxi':['taxi','Taxi']},
'Services':{'hairdresser':['hairdresser','Hairdresser'],'atm':['atm','ATM'],'bank':['bank','Bank'],'dentist':['dentist','Dentist']
,'doctors':['doctors','Doctor'],'pharmacy':['pharmacy','Pharmacy'],
'post_box':['post_box','Post box'],'fuel':['fuel','Fuel'],'recycling':['recycling','Recycling']},
'Shop':{'bakery':['bakery','Bakery'],'butcher':['butcher','Butcher'],'clothes':['clothes','Clothing store']
,'convenience':['convenience','Convenience store']
,'greengrocer':['greengrocer','Greengrocer'],'kiosk':['kiosk','Kiosk'],'mall':['mall','Mall'],'shoes':['shoes','Shoes'],
'supermarket':['supermarket','Supermarket'],'marketplace':['marketplace','Marketplace']},
'Tourism___Leisure':{"cinema":['cinema','Cinema'],"theatre":['theatre','Theatre'],"museum":['museum','Museum'],
"hotel":['hotel','Hotel'],"hostel":['hostel','Hostel'],
"guest_house":['guest_house','Guest house'],"gallery":['gallery','Gallery']}}



var pois ={};
var c;
for (c in categories_db_style){
	
		
	pois = Object.assign(pois,categories_db_style[c]);
}

var population ={
	"Population":{'population': ['population','Population']}
}

pois = Object.assign(pois,population["Population"]);

function GetPoiCategory(amenityType) {
	var AmenityCategory;
	var CategoriesKeys = Object.keys(categories_db_style);
		CategoriesKeys.forEach(ck => {
			var value = categories_db_style[ck];
			var subKeys = Object.keys(value);
			subKeys.forEach(sk => {
				if (sk == amenityType){
					AmenityCategory = ck;
				}
			});
		});
		return AmenityCategory;
  }




var dictionary = {
	'input':'Scenario',
	'default' : 'Default'


}
export {dropdown_slider,append_dropdown_slider,categories_db_style,pois,dictionary,header_array,content_array,GetPoiCategory};