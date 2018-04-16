;function showLoading(){$('#loading-overlay').removeClass('hidden');}
function hideLoading(){$('#loading-overlay').addClass('hidden');}
EventBus.subscribe(WAITING_SERVER_RESPONSE_STARTED,showLoading);EventBus.subscribe(WAITING_SERVER_RESPONSE_ENDED,hideLoading);