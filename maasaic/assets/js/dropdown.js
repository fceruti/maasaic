function DropDown(el) {
    this.dd = el;
    this.isInside = false;
    this.initEvents();
}
DropDown.prototype = {
    initEvents : function() {
        var obj = this;
        obj.dd.on('click', function(event){
            $(this).toggleClass('active');
            return false;
        });
        obj.dd.on('mouseenter', function(){
            this.isInside = true;
        });
        obj.dd.on('mouseleave', function(){
            $(this).removeClass('active');
            this.isInside = false;
        });
    },
}

