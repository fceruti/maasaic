// This is called after document ready and after every ajax success / failure
var HTML_INJECTED = 'HTML_INJECTED'

// AppState
var STATE_CHANGED = 'STATE_CHANGED';

// Sections
var SECTION_EDIT_MODAL_REQUEST = 'SECTION_EDIT_MODAL_REQUEST';
var SECTION_HOVERING_START = 'SECTION_HOVERING_START';
var SECTION_HOVERING_END = 'SECTION_HOVERING_END';

// Cells
var CELL_MODAL_REQUEST = 'CELL_MODAL_REQUEST';
var CELL_HOVERING_START = 'CELL_HOVER_START';
var CELL_HOVERING_END = 'CELL_HOVER_END';

var CELL_INVISIBILITY_CLICKED = 'CELL_INVISIBILITY_CLICKED';
var CELL_EDIT_CLICKED = 'CELL_EDIT_CLICKED';
var CELL_EDIT_CLOSED = 'CElL_EDIT_CLOSED';

// Loading
var WAITING_SERVER_RESPONSE_STARTED = 'WAITING_SERVER_RESPONSE_STARTED';
var WAITING_SERVER_RESPONSE_ENDED = 'WAITING_SERVER_RESPONSE_ENDED';



var EventBus = {
  keys: {},

  subscribe: function(key, listener) {
    // create the topic if not yet created
    if(!this.keys[key]) this.keys[key] = [];

    // add the listener
    this.keys[key].push(listener);
  },

  fire: function(key, ...data) {
    // return if the topic doesn't exist, or there are no listeners
    if(!this.keys[key] || this.keys[key].length < 1) return;

    if (DEBUG) {
        console.log('EventBus:fire', key, data)
    }

    // send the event to all listeners
    this.keys[key].forEach(function(listener) {
      listener(...data || {});
    });
  }
};
