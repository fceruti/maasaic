function bindModalEvents() {
    $('.modal-close-btn').click(function(){
        $(this).closest('.modal').addClass('hidden');
    });
}

function displayAddWebsiteModal() {
    console.log('ADD WEBSITE MODAL');
}

function displayEditWebsiteModal() {
    console.log('EDIT WEBSITE MODAL');
}

function displayAddPageModal() {
    console.log('ADD PAGE MODAL');
}

function displayEditPageModal() {
    console.log('EDIT PAGE MODAL');
}


EventBus.subscribe(HTML_INJECTED, bindModalEvents);

EventBus.subscribe(WEBSITE_ADD_CLICKED, displayAddWebsiteModal);
EventBus.subscribe(WEBSITE_EDIT_CLICKED, displayEditWebsiteModal);

EventBus.subscribe(PAGE_ADD_CLICKED, displayAddPageModal);
EventBus.subscribe(PAGE_EDIT_CLICKED, displayEditPageModal);
