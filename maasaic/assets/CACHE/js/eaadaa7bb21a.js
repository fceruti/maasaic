;function findInParsed(html,selector){return $(selector,html).get(0)||$(html).filter(selector).get(0);}
function bindFormEvents(){$('.js-ajax-form').on('submit',function(event){event.preventDefault();var data=$(this).serialize();var url=$(this).attr('action');performPost(url,data);});}
var isPosting=false
function performPost(url,data){if(isPosting===false){EventBus.fire(WAITING_SERVER_RESPONSE_STARTED);isPosting=true;if(!data.hasOwnProperty('csrfmiddlewaretoken')){data['csrfmiddlewaretoken']=csrfmiddlewaretoken;}
$.ajax({type:"POST",url:url,data:data,success:function(response){var newHtml=findInParsed(response,'#js-ajax-container');$('#js-ajax-container').html(newHtml);},complete:function(){EventBus.fire(HTML_INJECTED);EventBus.fire(WAITING_SERVER_RESPONSE_ENDED);appState=STATE_VIEW;EventBus.fire(STATE_CHANGED);isPosting=false;}});}}
EventBus.subscribe(HTML_INJECTED,bindFormEvents);