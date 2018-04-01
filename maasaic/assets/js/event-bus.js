// This is called after document ready and after every ajax success / failure
var HTML_INJECTED = 'HTML_INJECTED'

var WEBSITE_ADD_CLICKED = 'WEBSITE_ADD_CLICKED';
var WEBSITE_EDIT_CLICKED = 'WEBSITE_EDIT_CLICKED';

var PAGE_ADD_CLICKED = 'PAGE_ADD_CLICKED';
var PAGE_EDIT_CLICKED = 'PAGE_EDIT_CLICKED';

// Cells
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

  fire: function(key, data) {
    // return if the topic doesn't exist, or there are no listeners
    if(!this.keys[key] || this.keys[key].length < 1) return;

    // send the event to all listeners
    this.keys[key].forEach(function(listener) {
      listener(data || {});
    });
  }
};
