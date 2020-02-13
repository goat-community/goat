import { GeoJSON } from "ol/format";
import http from "../services/http";

/**
 * Util class for OL Edit layers.
 */
const editLayerHelper = {
  featuresIDsToDelete: [],
  selectedLayer: null,
  selectedWayType: "road",
  filterResults(response, source) {
    const editFeatures = new GeoJSON().readFeatures(response.first.data);
    const editFeaturesModified = new GeoJSON().readFeatures(
      response.second.data
    );
    source.addFeatures(editFeatures);
    const userInputFeaturesWithOriginId = [];
    const originIdsArr = [];
    const userInputFeaturesNoOriginId = [];

    editFeaturesModified.forEach(feature => {
      const id = parseInt(feature.getId().split(".")[1]);
      feature.setId(id);
      if (feature.getProperties().original_id != null) {
        userInputFeaturesWithOriginId.push(feature);
        originIdsArr.push(feature.getProperties().original_id);
      } else {
        userInputFeaturesNoOriginId.push(feature);
      }
    });

    editFeatures.forEach(feature => {
      let originId;
      const props = feature.getProperties();
      if (props.id) {
        originId = props.id;
      } else if (props.gid) {
        originId = props.gid;
        feature.set("id", props.gid);
      } else if (props.osm_id) {
        originId = props.osm_id;
        feature.set("id", props.osm_id);
      }

      if (
        originIdsArr.includes(originId) ||
        editLayerHelper.featuresIDsToDelete.includes(originId.toString())
      ) {
        source.removeFeature(feature);
      }
    });

    source.addFeatures([
      ...userInputFeaturesWithOriginId,
      ...userInputFeaturesNoOriginId
    ]);
  },
  deleteFeature(feature, source, userid) {
    const props = feature.getProperties();
    if (props.hasOwnProperty("original_id")) {
      if (props.original_id !== null) {
        const fid = feature.getProperties().original_id.toString();
        editLayerHelper.featuresIDsToDelete.push(fid);
        editLayerHelper.commitDelete(
          "delete",
          userid,
          editLayerHelper.featuresIDsToDelete,
          props.id
        );
        editLayerHelper.commitDelete(
          "update",
          userid,
          editLayerHelper.featuresIDsToDelete
        );
      } else {
        editLayerHelper.commitDelete(
          "delete",
          userid,
          editLayerHelper.featuresIDsToDelete,
          props.id
        );
      }
    } else {
      let fid;
      if (!props.hasOwnProperty("original_id") && !props.hasOwnProperty("id")) {
        fid = feature.getId().toString();
        editLayerHelper.commitDelete(
          "delete",
          userid,
          editLayerHelper.featuresIDsToDelete,
          fid
        );
      } else {
        fid = feature.getProperties().id.toString();
        editLayerHelper.featuresIDsToDelete.push(fid);
        editLayerHelper.commitDelete(
          "update",
          userid,
          editLayerHelper.featuresIDsToDelete
        );
      }
    }
    source.removeFeature(feature);
  },
  commitDelete(mode, user_id, deleted_feature_ids, drawn_fid) {
    const layerName = this.selectedLayer
      .getSource()
      .getParams()
      .LAYERS.split(":")[1];

    fetch("/api/userdata", {
      method: "POST",
      body: JSON.stringify({
        mode: mode,
        user_id: user_id,
        deleted_feature_ids: deleted_feature_ids,
        drawned_fid: drawn_fid,
        layer_name: layerName
      }),
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json"
      }
    })
      .then(function(data) {
        return data.json();
      })
      .then(function(json) {
        if (mode == "read") {
          editLayerHelper.featuresIDsToDelete = json[0].deleted_feature_ids
            ? json[0].deleted_feature_ids
            : [];
        }
      })
      .catch(function() {
        editLayerHelper.insertUserInDb("insert", user_id);
      });
  },
  uploadFeatures(userId, streetSource, onUploadCb) {
    http
      .get("./geoserver/wfs", {
        params: {
          service: "WFS",
          version: " 1.1.0",
          request: "GetFeature",
          viewparams: `userid:${userId}`,
          typeNames: "cite:network_modification"
        }
      })
      .then(function(response) {
        if (response.status === 200) {
          //Update Feature Line type
          streetSource.getFeatures().forEach(feature => {
            const prop = feature.getProperties();
            if (prop.hasOwnProperty("status")) {
              feature.setProperties({
                status: 1
              });
            }
          });
          onUploadCb("success");
        }
      })
      .catch(() => {
        onUploadCb("error");
      });
  },
  insertUserInDb(mode, generatedId) {
    const layerName = this.selectedLayer
      .getSource()
      .getParams()
      .LAYERS.split(":")[1];
    fetch("/api/userdata", {
      method: "POST",
      body: JSON.stringify({
        mode: mode,
        user_id: generatedId,
        layer_name: layerName
      }),
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json"
      }
    }).then(function(data) {
      return data.json;
    });
  }
};

export default editLayerHelper;
