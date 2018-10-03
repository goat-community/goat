 document.getElementById('export-png').addEventListener('click', function() {
        map.once('postcompose', function(event) {
          var canvas = event.context.canvas;
          if (navigator.msSaveBlob) {
            navigator.msSaveBlob(canvas.msToBlob(), 'map.png');
          } else {
            canvas.toBlob(function(blob) {
              saveAs(blob, 'map.png');
            });
          }
        });
        map.renderSync();
      });
   
   
        var update_link_download_shape = function(){
     			list_gid = []
     			for(var i = 0, l = thematic_data.length; i < l; i++){
						     					
     					var gid = thematic_data[0][i];
						if (gid.length != 0){     					
     					gid = gid.getProperties().gid;
     				
		     			list_gid.push(gid);
		     			}
     			}
     			
     			var url = address_geoserver+'cite/ows?service=WFS&version=1.0.0&request=GetFeature'
							 +'&typeName=cite:save_isochrones&maxFeatures=50'
							 +'&CQL_FILTER=gid in('+list_gid.toString()+')'+'&outputFormat=SHAPE-ZIP'
				
				$('#button_shapefile').attr('href',url);     			
     			return url
		     
     }