//import map, point,linestring,Overlay
import {map} from './map';
import Point from 'ol/geom/Point';
import LineString from 'ol/geom/LineString';
import Overlay from 'ol/Overlay';


var helpTooltip;
var listener_start;
var listener_end;
var tool_tip = function(interaction,modus){
    var sketch;  
		map.getOverlays().getArray().slice(0).forEach(function(overlay) {
						if (overlay.getProperties().element.id !='startaddresse'){																	
		 					map.removeOverlay(overlay);
						}		
		});
      var helpTooltipElement;
      var continueLineMsg = '<b>Single click to draw <br> Double click to finish</b>';
      var pointerMoveHandler = function(evt) {
        if (evt.dragging && modus != 'modify') {
          return;
        }
        /** @type {string} */
        var helpMsg = '<b>Click for starting to draw<b>';
		  if(modus=='point'){
				helpMsg = '<b>Click for Calculation</b>'          	
        }
      if (modus == 'modify'){
        helpMsg = '<b>Click and drag the features to modify</b>' 
      }
      if (modus == 'delete'){
        helpMsg = '<b>Click on feature to delete it</b>' 
      }
        if (sketch) {
          var geom1 = (sketch.getGeometry());
          if (geom1 instanceof Point) {
            helpMsg = '<b>Click button again <br> for new calculation</b>';
          } else if (geom1 instanceof LineString) {
            helpMsg = continueLineMsg;
          }
         
        }
        helpTooltipElement.innerHTML = helpMsg;
        helpTooltip.setPosition(evt.coordinate);
        helpTooltipElement.classList.remove('hidden');
      };
      map.on('pointermove', pointerMoveHandler);
      map.getViewport().addEventListener('mouseout', function() {
        helpTooltipElement.classList.add('hidden');
      });
      var typeSelect = document.getElementById('type');
      function createHelpTooltip() {
        if (helpTooltipElement) {
          helpTooltipElement.parentNode.removeChild(helpTooltipElement);
        }
        helpTooltipElement = document.createElement('div');
        helpTooltipElement.className = 'tooltip hidden';
        helpTooltip = new Overlay({
          element: helpTooltipElement,
          offset: [15, 0],
          positioning: 'center-left'
        });
        map.addOverlay(helpTooltip);
      }
      createHelpTooltip();
      if (interaction){ 
        listener_start = interaction.on('drawstart',
        function(evt) {
          // set sketch
          sketch = evt.feature;
        }, this);

        listener_end =  interaction.on('drawend',
              function() {
                if (modus != 'point'){
                sketch = null;
            }
              }, this);
      }

};

 
export {tool_tip};





var tool_info = {"Starting point calculation ":`You can press this button and click<br> 
                                at any visible place on the map for<br>
                                starting a calculation.`,
           "Load network":`You can load a subset of the road network into your map<br>
                                 by clicking the button and simply drawing a circle.<br>
                                 These streets can be used to modify the transport network.`,          
                      "Modify network":`There are existing three ways of modifying the network.<br>
                                 You can draw a new way feature, delete an existing feature <br>
                                 or modify the shape of an existing feature.<br>`,
  "Add network modification":`Once this button is clicked the drawn<br>
                                  lines are inserted into the routing<br>
                                  network. Depending on the number of drawn<br>
                                  features the calculation in the back-end<br> 
                                  can take a couple of seconds.`,
              "Travel Time (min) ":`The chosen travel time is the maximum<br>
                                  travel time of the drawn isochrone and<br>
                                  is the maximum travel time when the dynamic<br>
                                  accessibility index (not the heat-map) get calculated`, 
                 "Walking Speed ":`The average walking speed is<br>
                                  around 5 km/h, but it can vary depending<br>
                                  on the person. You are free to customize this value<br>`,
              "Number isochrones ":`The number of isochrones<br>
                                  defines how many isochrones are drawn,<br> 
                                  the division of the the selected travel time<br>
                                  and the number of isochrones is defining<br>
                                  the travel time interval.`,
           "Concavity isochrones ":`An isochrone (in this context) is defining<br> 
                                   the area, which can be reached in a certain<br>
                                   time. The input for creating the isochrone is the<br> 
                                   reached network. For the calculating of a convex<br> 
                                   isochrone an polygon get spanned, like a rubber<br> 
                                   band around some nails. Although this method is<br> 
                                   the fastest for calculating an isochrone, it can be the<br> 
                                   least accurate.<br> 
                                   Therefore it is possible to calculate concave hulls<br> 
                                   instead. Depending on the concavity the<br>
                                   area of the polygon is following more closely<br>
                                   the reached network. As the algorithm can only be an<br>
                                   approximation it might be that when calculating<br> 
                                   an scenario GOAT indicates that some areas, which<br> 
                                   should not be affected by the network are showing<br> 
                                   a different shape. Accordingly for some<br>
                                   representation the convex hull can deliver<br>
                                   more consistent and understandable results.`,
              "Calculation modus ":`Once new links and nodes are added to<br>
                                   the network, it is possible to perform a<br> 
                                   calculation on the default network, on<br>
                                   the modified network or on both networks<br> 
                                   at the same time.`,
          "Accessibility basemap":`By selecting the thematic data you want to analyse<br>
                                   and by selecting the walkability basemap in the<br>
                                   dropdown menu you can visualize an dynamic and<br>
                                   customizable heat-map. For allowing a high<br> 
                                   performance the heat-map uses precalculated<br>
                                   travel times, the index however get calculated<br>
                                   interactively. This means you can assess the<br>
                                   accessibility to different amenities interactively<br>
                                   but you cannot built scenarios.`,
                           "GOAT":`<b>Geo Open Accessibility Tool (GOAT)</b><br>
                                    This is tool could be developed thanks to powerful open source<br>
                                    software and the OpenStreetMap-project. For the population numbers<br>
                                    data from the Statistikamt München and the German Zensus 2011 are used.<br>
                                    Icons are used from: Maps Icons Collection, <a href="https://mapicons.mapsmarker.com">https://mapicons.mapsmarker.com</a>.`,
                  "Choose basemap ":`You can choose betweeen different basemaps,<br>
                                     please consider if you want to select the<br> 
                                     most up-to-date basemap choose OSM-Standard,<br>
                                     OSM-Carto-DB-Light, OSM-Carto-DB-Dark or <br>
                                     PublicTransport.`        
};

                             
$("body").on('click','.fa-info-circle',function(){
  $('#tool_info').remove();
  var position_top = $(this).offset().top -70;
  $("body").append(`<div id="tool_info" style="border:#2FAC45 solid 1px;:margin-right:0px;position: absolute; z-index: 10001;left:14%;
   top: ${position_top}px; "><div style="background-color:#f8f8f8;padding:10px;"><i id="tool_info_cross" class="fa fa-times"style="font-size:16px"></i></div>
   <div style="font-family: Open Sans;background-color: #f8f8f8;padding: 10px;">${tool_info[$(this).parent().text()]}</div></div>`);
  
})

$("body").on('click','#tool_info_cross',function(){
  $("#tool_info").remove();
})


