import {GeoJSON,WFS,GML} from 'ol/format';
import {intersects as intersectsFilter,equalTo as equalToFilter, and as andFilter} from 'ol/format/filter';
import {fromCircle} from 'ol/geom/Polygon';
import {Vector as VectorLayer} from 'ol/layer';
import {Vector as VectorSource} from 'ol/source'; 
import ApiConstants from './secrets';	
import {bbox as bboxStrategy} from 'ol/loadingstrategy';
import {map} from './map';
import {iconStyle,drawing_style,boundaryStyle} from './style';
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




//--- WAYS LAYER USER INTERACTION ---//
var staticUserId = 1; //temporary
function WfsRequestFunction (srsName,namespace,workspace,layerName,filter){
    console.log(srsName,namespace,workspace,layerName,filter);
    var wfs = new WFS().writeGetFeature({
        srsName: srsName,
        featureNS: namespace,
        featurePrefix: workspace,
        featureTypes: [layerName],
        outputFormat: 'application/json',
        filter: filter
    });
    var xmlparser = xs.serializeToString(wfs);
    return xmlparser;
}


    //Add the query layer to the map
var QueryLayerSouce = new VectorSource({wrapX: false});
var QueryLayer = new VectorLayer({
        source: QueryLayerSouce,
        style: drawing_style
    });
    QueryLayer.setMap(map);

    //Ways Layer
var ExtractStreetsSource = new VectorSource({wrapX: false});
var ExtractStreetsLayer = new VectorLayer({
    source: ExtractStreetsSource,
    style: boundaryStyle
});

ExtractStreetsLayer.setMap(map);

var searchInteraction = {
    interaction: null,
    drawStartEvent: function (evt){
       
    },
    drawStopEvent: function (evt){
     
        $('#mySpinner').addClass('spinner');

        //1 - SPATIAL INTERSECT WITH ORIGINAL DATA
        var circle = evt.feature.getGeometry();  
       var circleGeom = fromCircle(circle);
       var filterIntersect = intersectsFilter('geom', circleGeom, 'EPSG:3857');

        //Get the feature that intersect with geometry
       var wfsRequestXmlStringOriginalTable = WfsRequestFunction('EPSG:3857',ApiConstants.geoserver_namespaceURI, ApiConstants.geoserver_workspace,'ways',filterIntersect);
       var originalTableRequest = fetch(ApiConstants.wfs_url,{
            method: 'POST',
            body: wfsRequestXmlStringOriginalTable,
            headers: {
                'Content-Type': 'application/xml',
                'Accept': 'application/xml'
            }
        }).then(function(response){
            return response.json();
        })

         //2 - USER INPUT FILTER BASED ON USER ID
       var filterUserInputTable = equalToFilter('userid', staticUserId);
       var combinedFilter = andFilter(filterUserInputTable,filterIntersect)
       var wfsRequestXmlStringUserInputTable = WfsRequestFunction('EPSG:3857',ApiConstants.geoserver_namespaceURI, ApiConstants.geoserver_workspace,'ways_userinput',combinedFilter);
        var userInputTableRequest = fetch(ApiConstants.wfs_url,{
            method: 'POST',
            body: wfsRequestXmlStringUserInputTable,
            headers: {
                'Content-Type': 'application/xml',
                'Accept': 'application/xml'
            }
        }).then(function(response){
            return response.json();
        });

        //3- START THE REQUESTS AND FILTER THE RESULTS
        Promise.all([originalTableRequest,userInputTableRequest]).then(function(values){
            $('#mySpinner').removeClass('spinner');
            var originalFeatures = new GeoJSON().readFeatures(values[0]); 
            var userInputFeatures = new GeoJSON().readFeatures(values[1]);
            ExtractStreetsSource.clear();
            ExtractStreetsSource.addFeatures(originalFeatures);
            searchInteraction.stop();
            ///Filter out original features from user drawned features
            var userInputFeaturesWithOriginalId  = [];
            var originalIdsArr = []
            var userInputFeaturesWithoutOriginalId = [];

            var i;

            for (i=0;i<userInputFeatures.length;i++){
                var currentFeature = userInputFeatures[i];
                var id = parseInt(currentFeature.getId().split(".")[1]);
                currentFeature.setId(id);
                if (currentFeature.getProperties().original_id != null){
                    userInputFeaturesWithOriginalId.push(currentFeature)
                    originalIdsArr.push(currentFeature.getProperties().original_id);
                } else {
                    userInputFeaturesWithoutOriginalId.push(currentFeature);
                }
                console.log(currentFeature.getId());
            }

            for (var i=0;i<originalFeatures.length;i++){
                var currentFeature = originalFeatures[i];
                var original_id = currentFeature.getProperties().id;
                if (originalIdsArr.includes(original_id)){
                    ExtractStreetsSource.removeFeature(currentFeature);
                }
            }
            ExtractStreetsSource.addFeatures(userInputFeaturesWithOriginalId);
            ExtractStreetsSource.addFeatures(userInputFeaturesWithoutOriginalId);

            console.log(originalFeatures);
            console.log(userInputFeaturesWithOriginalId);
            console.log(userInputFeaturesWithoutOriginalId);
        });


    },
    init: function(){
        this.stop();
        waysInteraction.remove();
        QueryLayer.getSource().clear();
        ExtractStreetsSource.clear();
        //Add circle interaction to search for the geojson features on the map
        var circleDraw = new Draw({
            source: QueryLayer.getSource(),
            type: 'Circle'
        });
        this.interaction = circleDraw;
        map.addInteraction(circleDraw);
        circleDraw.on('drawend',this.drawStopEvent);
        circleDraw.on('drawstart',this.drawStartEvent);
    },
    stop: function (){
        if (this.interaction != null){
            map.removeInteraction(this.interaction);
        }
        this.interaction = null;
    }
}

ExtractStreetsSource.on('changefeature',function (evt){
    if (waysInteraction.interactionType == 'modify'){
       
        var index = waysInteraction.featuresToCommit.findIndex(i => i.ol_uid == evt.feature.ol_uid )
        if (index == -1){
            waysInteraction.featuresToCommit.push(evt.feature)
        } else {
            waysInteraction.featuresToCommit[index]=evt.feature;
        }
    }
});



//BUTTON EVENT HANDLERS

var waysInteraction = {
    featuresToCommit: [],
    featuresIDsToDelete: [],
    currentInteraction: null,
    interactionType: null,
    snapInteraction: null,
    interactionStart: function (evt) {
        waysInteraction.featuresToCommit = [];
       
        
    },
    interactionEnd: function (evt){
        if (waysInteraction.interactionType == 'draw'){
            var feature = evt.feature;
            waysInteraction.featuresToCommit.push(feature);
        }
     console.log(waysInteraction.featuresToCommit);
     waysInteraction.transact();
    },
    remove: function(){
     if (this.snapInteraction != null){
         map.removeInteraction(this.snapInteraction);
     }
     if (this.currentInteraction != null){
         map.removeInteraction(this.currentInteraction);
     }
     this.featuresToCommit = [];
    },
    add: function (interaction,type){
        this.remove();
        map.addInteraction(interaction);
        var snap = new Snap({source: ExtractStreetsSource});
        map.addInteraction(snap);
        this.currentInteraction = interaction;
        this.interactionType = type;
        interaction.on(type+'start',this.interactionStart);
        interaction.on(type+'end',this.interactionEnd);
        this.snapInteraction = snap
    },
    transact: function (){
        // 1- Get the features, transform geometry and properties


        var featuresToAdd = [];
        var featuresToUpdate = [];

//        var transformedBackArr = [];
        var featuresToRemoveArr = [];
        //There is the case on update interaction when some features needs to be added
        //and the features that are already in table needs to be updated
        var i;
        for (i=0;i<this.featuresToCommit.length;i++){
            var f = this.featuresToCommit[i];
            //Feature Properties
            var props = f.getProperties();
            //Transform the feature
            var geometry = f.getGeometry().clone();
            geometry.transform("EPSG:3857", "EPSG:4326");
            var transformed = new Feature({	
                userid : staticUserId,                
                geom: geometry,
                class_id: f.getProperties().class_id,
                original_id: f.getProperties().id
            });
            transformed.setGeometryName("geom");

            if ((typeof f.getId() == 'undefined' && Object.keys(props).length == 1) || !props.hasOwnProperty('original_id')){
                featuresToAdd.push(transformed);
                featuresToRemoveArr.push(f);

            } else if((props.hasOwnProperty('original_id')) && (this.interactionType == 'modify')) {
                transformed.setId(f.getId());
                featuresToUpdate.push(transformed);
            }
        }
        console.log('-------------')
        console.log(featuresToAdd);
        console.log(featuresToUpdate);
        console.log('-------------')

    console.log(ApiConstants.geoserver_workspace);
    formatGML = {
        featureNS: ApiConstants.geoserver_namespaceURI,
        featureType: 'ways_userinput',
        srsName: 'urn:x-ogc:def:crs:EPSG:4326'
    };
       var node;
   
    switch (this.interactionType) {
            case 'draw':
                node = formatWFS.writeTransaction(featuresToAdd, null, null, formatGML);       
                break;
            case 'modify':
                node = formatWFS.writeTransaction(featuresToAdd,featuresToUpdate,null,formatGML);
                break;
            case 'delete':
                node = formatWFS.writeTransaction(null, null, null, formatGML);
                break;
        }
        console.log(node);
     var payload = xs.serializeToString(node);
    
    $.ajax({
        type: "POST",
        url: ApiConstants.wfs_url,
        data: new XMLSerializer().serializeToString(node),
        contentType: 'text/xml',
        success: function(data) {
            console.log(data);
            var result = formatWFS.readTransactionResponse(data);
            var FIDs = result.insertIds;
            console.log(result);
            if (FIDs != undefined && FIDs[0]!="none"){
                var i;
                for (i=0;i<FIDs.length;i++){
                    var id = parseInt(FIDs[i].split(".")[1]);
                    ExtractStreetsSource.removeFeature(featuresToRemoveArr[i])
                    featuresToAdd[i].setId(id);
                    featuresToAdd[i].getGeometry().transform("EPSG:4326", "EPSG:3857")
                    ExtractStreetsSource.addFeature(featuresToAdd[i]);
                }
            }
        },
        error: function(e) {
         
        },
        context: this
    });


    }


}


//Button click events
$('.expert_draw').click(function () {
    let buttonID = this.id;
    if (buttonID == 'btnQuery'){
        searchInteraction.init();
        return;
    }

    switch(buttonID){
        case 'btnDraw':
       var drawInteraction = new Draw({
                source: ExtractStreetsSource,
                type: 'LineString'
                });
        waysInteraction.add(drawInteraction,'draw');
        tool_tip(drawInteraction,'line');
        break;
        case 'btnModify':
        var modifyInteraction = new Modify({
                source: ExtractStreetsSource,
                });
                console.log('modify executed');
        waysInteraction.add(modifyInteraction,'modify');
        break
        case 'btnDelete':
        // ADD BUTTON DELETE
        break;
    }

 


})








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

