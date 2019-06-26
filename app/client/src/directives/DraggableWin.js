import Vue from "vue";

/**
 * Directive to make a window component draggable by dragging it's header.
 * Proudly inspired by and most of the essential code taken from
 * https://github.com/branu-ws/v-drag/blob/master/src/index.js
 */
export const DraggableWin = {
  dragConfig: {
    // if this is present, only a specific area of the draggable will respond to
    // dragging (e. g. header bar).
    draggableElementSelector: null,
    down: false,
    height: 0,
    width: 0,
    initialX: 0,
    initialY: 0,
    constraintToWindow: true,
    cursorPreviousX: 0,
    cursorPreviousY: 0,
    draggerOffsetLeft: 0,
    draggerOffsetTop: 0,
    overlay: null,
    draggableEl: null,
    initialZIndex: undefined
  },
  bind(elmnt, binding, vnode) {
    if (binding.value === false) {
      // disable this directive if set to v-draggable-win="false"
      return;
    }
    // get the header element to bind the events on it
    var header = elmnt.querySelector("div.wgu-win-title");
    if (!header) {
      return;
    }
    const dragConfig = DraggableWin.dragConfig;
    // restrict the dragging at least to window title
    dragConfig.draggableElementSelector = binding.arg || "wgu-win-title";

    // set cursor so it's signal that the user can drag the window
    header.style.cursor = "move";

    elmnt.addEventListener("mouseup", e => mouseup(e, elmnt, dragConfig));
    elmnt.addEventListener("mousedown", e => mousedown(e, elmnt, dragConfig));
    elmnt.addEventListener("mousemove", e => mousemove(e, elmnt, dragConfig));
    setDraggerOffset(elmnt, dragConfig);
    dragConfig.initialZIndex = elmnt.style.zIndex;

    /**
     * Creates an overlay in order to bind the mouse events to it.
     */
    function createOverlay(e, el, _data) {
      const overlay = document.createElement("div");
      overlay.setAttribute(
        "style",
        `
        width: 100vw;
        height: 100vh;
        position: absolute;
        top: 0;
        left: 0;
        z-index: 10000;
      `
      );
      overlay.addEventListener("mouseup", e => mouseup(e, el, _data));
      overlay.addEventListener("mousedown", e => mousedown(e, el, _data));
      overlay.addEventListener("mousemove", e => mousemove(e, el, _data));
      document.body.appendChild(overlay);

      return overlay;
    }

    /**
     * Checks if the given selector (id or class) occurs in the given path
     */
    function checkIfSelectorInPath(selector, path) {
      for (let i = 0; i < path.length; i++) {
        // check for ID
        if (path[i].id === selector) {
          return true;
        }
        // also check for a class name
        if (path[i].classList && path[i].classList.contains(selector)) {
          return true;
        }
      }
      return false;
    }

    /**
     * Adjusts element's z-index.
     */
    function adjustElementZIndex(el, index) {
      el.style.zIndex = index;
    }

    /**
     * Event handler for mouse down.
     */
    function mousedown(e, el, _data) {
      // if the user set a argument to v-drag,
      // it means they only want a specific area to be draggable
      // eg: `v-drag:drag-header` means only the element with
      // id="drag-header" or class="drag-header" should be draggable.
      // If the user clicked another area, do nothing.
      // By default it is restricted to class="wgu-win-title"
      if (
        _data.draggableElementSelector &&
        !checkIfSelectorInPath(_data.draggableElementSelector, e.path)
      ) {
        return;
      }

      if (_data.overlay) {
        _data.overlay.remove();
      }
      // set the width each click
      // just in case it changed since last time (by external plugin, for example)
      _data.width = el.offsetWidth;
      _data.height = el.offsetHeight;
      _data.down = true;
      _data.initialX = e.clientX;
      _data.initialY = e.clientY;
      const overlay = createOverlay(e, el, _data);
      _data.overlay = overlay;
      adjustElementZIndex(el, 10001);
    }

    /**
     * Event handler for mouse up.
     */
    function mouseup(e, el, _data) {
      _data.down = false;
      if (!_data.overlay) {
        return;
      }

      _data.overlay.removeEventListener("mouseup", mouseup);
      _data.overlay.removeEventListener("mousedown", mousedown);
      _data.overlay.removeEventListener("mousemove", mousemove);
      _data.overlay.remove();
      adjustElementZIndex(el, _data.initialZIndex);

      setDraggerOffset(el, _data);

      // preserve the current position as property of the vue / Wegue window
      // so it can be restored when the window is re-opened
      vnode.componentInstance.$parent.top = _data.draggerOffsetTop + "px";
      vnode.componentInstance.$parent.left = _data.draggerOffsetLeft + "px";
    }

    /**
     * Checks if left window boundary is reached.
     */
    function reachedLeft(el, _data, movingLeft) {
      return el.offsetLeft + _data.width >= window.innerWidth && !movingLeft;
    }

    /**
     * Checks if right window boundary is reached.
     */
    function reachedRight(el, _data, movingRight) {
      return el.offsetLeft <= 0 && !movingRight;
    }

    /**
     * Checks if top window boundary is reached.
     */
    function reachedTop(el, _data, movingUp) {
      return el.offsetTop <= 0 && !movingUp;
    }

    /**
     * Checks if bottom window boundary is reached.
     */
    function reachedBottom(el, _data, movingDown) {
      return el.offsetTop + _data.height >= window.innerHeight && !movingDown;
    }

    /**
     * Event handler for mouse move.
     */
    function mousemove(e, el, _data) {
      if (_data.down) {
        const movingLeft = _data.cursorPreviousX > e.clientX;
        const movingRight = _data.cursorPreviousX < e.clientX;
        const movingUp = _data.cursorPreviousY < e.clientY;
        const movingDown = _data.cursorPreviousY > e.clientY;

        if (
          _data.constraintToWindow &&
          (reachedLeft(el, _data, movingLeft) ||
            reachedRight(el, _data, movingRight))
        ) {
          // do now allow moving outside the window horizontally
        } else {
          el.style.left =
            _data.draggerOffsetLeft + (e.clientX - _data.initialX) + "px";
        }
        if (
          _data.constraintToWindow &&
          (reachedTop(el, _data, movingUp) ||
            reachedBottom(el, _data, movingDown))
        ) {
          // do now allow moving outside the window vertically
        } else {
          el.style.top =
            _data.draggerOffsetTop + (e.clientY - _data.initialY) + "px";
        }
      }
      _data.cursorPreviousX = e.clientX;
      _data.cursorPreviousY = e.clientY;
    }

    /**
     * Applies the offset values of the element.
     */
    function setDraggerOffset(el, _data) {
      _data.draggerOffsetLeft = el.offsetLeft;
      _data.draggerOffsetTop = el.offsetTop;
    }
  }
};

// Make directive available globally
Vue.directive("draggable-win", DraggableWin);
