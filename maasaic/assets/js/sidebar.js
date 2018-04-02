function DropDown(el) {
    this.dd = el;
    this.placeholder = this.dd.children('span');
    this.opts = this.dd.find('ul.sidebar-dropdown > li');
    this.val = '';
    this.index = -1;
    this.initEvents();
}
DropDown.prototype = {
    initEvents : function() {
        var obj = this;

        obj.dd.on('click', function(event){
            $(this).toggleClass('active');
            return false;
        });

        obj.opts.on('click',function(){
            var opt = $(this);
            obj.val = opt.text();
            obj.index = opt.index();
            obj.placeholder.text(obj.val);
        });
    },
    getValue : function() {
        return this.val;
    },
    getIndex : function() {
        return this.index;
    }
}



function bindSidebarEvents() {
    new DropDown($('#js-website-select-dropdown'));
    new DropDown($('#js-page-select-dropdown'));

    $('#js-sidebar-add-website-btn').click(function(){
        EventBus.fire(WEBSITE_ADD_CLICKED);
    });

    $('#js-sidebar-edit-website-btn').click(function(){
        EventBus.fire(WEBSITE_EDIT_CLICKED);
    });

    $('#js-sidebar-add-page-btn').click(function(){
        EventBus.fire(PAGE_ADD_CLICKED);
    });

    $('#js-sidebar-edit-page-btn').click(function(){
        EventBus.fire(PAGE_EDIT_CLICKED);
    });
}

EventBus.subscribe(HTML_INJECTED, bindSidebarEvents);
