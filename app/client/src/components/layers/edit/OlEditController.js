/**
 * Class holding the OpenLayers related logic for the edit tool.
 */

export default class OlEditController {
  /* the OL map we want to edit on */
  map = null;

  constructor(olMap) {
    this.map = olMap;
  }
}
