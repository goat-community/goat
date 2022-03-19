import ApiService from "../services/api.service";
import store from "../store/modules/scenarios";
import { geojsonToFeature } from "../utils/MapUtils";
/**
 * Util class for OL Edit layers.
 */

const editLayerHelper = {
  // Cancel Request
  cancelReq: undefined,
  featuresIDsToDelete: [],
  deletedFeatures: [],
  selectedLayer: null,
  selectedWayType: "road",
  original_id() {
    if (editLayerHelper.selectedLayer["name"] === "poi") {
      return "uid";
    } else if (editLayerHelper.selectedLayer["name"] === "building") {
      return "building_id";
    } else if (editLayerHelper.selectedLayer["name"] === "way") {
      return "way_id";
    } else {
      return "";
    }
  },
  filterResults(response, source, bldEntranceLayer, storageSource) {
    let editFeatures = [];
    if (response.first) {
      editFeatures = geojsonToFeature(response.first.data, {
        dataProjection: "EPSG:4326",
        featureProjection: "EPSG:3857"
      });
    }
    const editFeaturesModified = geojsonToFeature(response.second.data, {
      dataProjection: "EPSG:4326",
      featureProjection: "EPSG:3857"
    });
    source.addFeatures(editFeatures);
    const userInputFeaturesWithOriginId = [];
    const originIdsArr = [];
    const userInputFeaturesNoOriginId = [];

    editFeaturesModified.forEach(feature => {
      const id = parseInt(feature.getId().split(".")[1]);
      feature.setId(id);
      if (feature.getProperties()[editLayerHelper.original_id()] != null) {
        userInputFeaturesWithOriginId.push(feature);
        originIdsArr.push(
          feature.getProperties()[editLayerHelper.original_id()]
        );
      } else {
        userInputFeaturesNoOriginId.push(feature);
      }
    });

    if (response.third) {
      bldEntranceLayer.getSource().addFeatures(
        geojsonToFeature(response.third.data, {
          dataProjection: "EPSG:4326",
          featureProjection: "EPSG:3857"
        })
      );
    }

    editFeatures.forEach(feature => {
      let originId;
      const props = feature.getProperties();
      if (props.id) {
        originId = props.id;
      }

      if (
        originIdsArr.includes(originId) ||
        editLayerHelper.featuresIDsToDelete.includes(originId.toString())
      ) {
        //check if feature already exist.
        if (
          editLayerHelper.deletedFeatures.filter(
            f => f.getId() === feature.getId()
          ).length === 0
        ) {
          const clonedFeature = feature.clone();
          const layerName = editLayerHelper.selectedLayer["name"];
          clonedFeature.set("layerName", layerName);
          clonedFeature.set("deletedId", originId);
          editLayerHelper.deletedFeatures.push(feature.clone());
        }
        source.removeFeature(feature);
        if (storageSource.hasFeature(feature)) {
          storageSource.removeFeature(feature);
        }
      }
    });

    source.addFeatures([
      ...userInputFeaturesWithOriginId,
      ...userInputFeaturesNoOriginId
    ]);
  },
  deleteFeature(feature, source, storageSource) {
    const props = feature.getProperties();
    const beforeStatus = feature.get("status");
    feature.set("status", null);
    feature.set("scenario_id", store.state.activeScenario);
    if (feature.get("layerName") === "poi") {
      feature.set("status", 1);
    }
    if (props.hasOwnProperty([editLayerHelper.original_id()])) {
      if (props[editLayerHelper.original_id()] !== null) {
        const fid = feature
          .getProperties()
          [editLayerHelper.original_id()].toString();
        editLayerHelper.featuresIDsToDelete.push(fid);
        editLayerHelper.deletedFeatures.push(feature);
        editLayerHelper.commitDelete("delete_feature", props.id);
        editLayerHelper.commitDelete("update_deleted_features");
      } else {
        if (beforeStatus !== null) {
          editLayerHelper.deletedFeatures.push(feature);
        }
        editLayerHelper.commitDelete(
          "delete_feature",
          props.id || feature.getId()
        );
      }
    } else {
      let fid;
      if (
        !props.hasOwnProperty(editLayerHelper.original_id()) &&
        !props.hasOwnProperty("id")
      ) {
        fid = feature.getId().toString();
        editLayerHelper.commitDelete("delete_feature", fid);
      } else {
        fid = feature.getProperties().id.toString();
        editLayerHelper.featuresIDsToDelete.push(fid);
        editLayerHelper.deletedFeatures.push(feature);
        editLayerHelper.commitDelete("update_deleted_features");
      }
    }
    source.removeFeature(feature);
    if (storageSource.hasFeature(feature)) {
      storageSource.removeFeature(feature);
    }
  },
  commitDelete(mode, drawn_fid) {
    //mode = delete_feature, update_deleted_features, read_deleted_features
    const layerName = editLayerHelper.selectedLayer["name"];
    let promise;
    if (mode === "delete_feature") {
      promise = ApiService.delete(
        `/scenarios/${store.state.activeScenario}/${layerName}/features/${drawn_fid}`
      );
    }
    if (mode === "update_deleted_features") {
      promise = ApiService.patch(
        `/scenarios/${store.state.activeScenario}/${layerName}`,
        editLayerHelper.featuresIDsToDelete
      );
    }

    if (mode === "read_deleted_features") {
      promise = ApiService.get(
        `/scenarios/${store.state.activeScenario}/${layerName}/deleted`
      );
    }

    promise.then(response => {
      if (response.data) {
        if (mode == "read_deleted_features") {
          editLayerHelper.featuresIDsToDelete =
            response.data && Array.isArray(response.data) ? response.data : [];
        }
      }
    });
  },

  uploadFeatures(source, onUploadCb) {
    ApiService.get(`/scenarios/${store.state.activeScenario}/upload`)
      .then(function(response) {
        if (response.status === 200) {
          //Set status of delete features as well
          editLayerHelper.deletedFeatures = editLayerHelper.deletedFeatures.filter(
            feature => {
              if (feature.get("scenario_id") !== store.state.activeScenario) {
                return false;
              }
              feature.setProperties({
                status: 1
              });

              //If there are any user drawn feature remove those.
              if (feature.get(editLayerHelper.original_id()) === null) {
                return false;
              } else {
                return true;
              }
            }
          );
          const bldFeatureIds = [];
          //Update Feature Line type
          source.getFeatures().forEach(feature => {
            if (feature.get("scenario_id") !== store.state.activeScenario) {
              return;
            }
            if (feature.get("layerName") === "building") {
              bldFeatureIds.push(feature.getId());
            }
            const prop = feature.getProperties();
            if (
              prop.hasOwnProperty("status") ||
              prop.hasOwnProperty(editLayerHelper.original_id())
            ) {
              feature.setProperties({
                status: 1
              });
            }
          });
          // Refetch building features  to update the properties (used for population)...
          ApiService.get(
            `/scenarios/${store.state.activeScenario}/building_modified/features}`
          ).then(response => {
            if (response.data) {
              const olFeatures = geojsonToFeature(response.data);
              olFeatures.forEach(feature => {
                if (feature.get("id")) {
                  const id = parseInt(feature.get("id"));
                  const editFeature = source.getFeatureById(id);
                  var keys = Object.keys(feature.getProperties());
                  const properties = feature.getProperties();
                  keys.forEach(key => {
                    if (!["geom", "geometry"].includes(key)) {
                      const value = properties[key];
                      if (value) {
                        editFeature.set(key, value);
                      }
                    }
                  });
                }
              });
            }
          });
          onUploadCb("success");
        }
      })
      .catch(() => {
        onUploadCb("error");
      });
  }
};

export default editLayerHelper;
