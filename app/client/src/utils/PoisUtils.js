/**
 * Util file for Pois component.
 */

export function toggleTreeLockState(node, state) {
  if (state === "activate") {
    node.locked = true;
    //To know how many time this node is locked, from different filters
    node.hasOwnProperty("queue") ? (node["queue"] += 1) : (node["queue"] = 1);
  } else {
    //Check if there are other values in queue from different filters.
    if (node["queue"] > 1) {
      node["queue"] -= 1;
    } else {
      node["queue"] = 0;
      node.locked = false;
    }
  }
}
