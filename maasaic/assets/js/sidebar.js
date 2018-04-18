
function onCellHoverStartSidebar(sectionId, cellId) {
    $('.cell-list-item[data-section-id="' + sectionId + '"][data-cell-id="' + cellId + '"] .sidebar-item').addClass('hover');
}

function onCellHoverEndSidebar(sectionId, cellId) {
    $('.cell-list-item[data-section-id="' + sectionId + '"][data-cell-id="' + cellId + '"] .sidebar-item').removeClass('hover');
}

function onCellDragNDropEnd(evt) {
    var itemEl = evt.item;  // dragged HTMLElement
    if(evt.newIndex == evt.oldIndex) return;
    var cellId = $(itemEl).attr('data-cell-id');
    var url = '/cells/' + cellId + '/order'
    var data = {'order': evt.newIndex};
    performPost(url, data);
}

function onSectionDragNDropEnd(evt) {
    var itemEl = evt.item;  // dragged HTMLElement
    if(evt.newIndex == evt.oldIndex) return;
    var cellId = $(itemEl).attr('data-section-id');
    var url = '/sections/' + cellId + '/order'
    var data = {'order': evt.newIndex};
    performPost(url, data);
}

function bindSidebarEvents() {
    new DropDown($('#js-website-select-dropdown'));
    new DropDown($('#js-page-select-dropdown'));

    $('.cell-list-item').hover(
        function() {
            var sectionId = $(this).attr('data-section-id');
            var cellId = $(this).attr('data-cell-id');
            EventBus.fire(CELL_HOVERING_START, sectionId, cellId);
        }, function() {
            var sectionId = $(this).attr('data-section-id');
            var cellId = $(this).attr('data-cell-id');
            EventBus.fire(CELL_HOVERING_END, sectionId, cellId);
        }
    );

    Sortable.create($('#js-section-list')[0], {
        handle: '.drag-handle',
        dataIdAttr: 'data-section-id',
        animation: 150,
        onEnd: onSectionDragNDropEnd,
        draggable: '.section-list-item'
    });

    $('.cell-list').each(function(){
        Sortable.create($(this)[0], {
            handle: '.drag-handle',
            dataIdAttr: 'data-cell-id',
            draggable: '.cell-list-item',
            animation: 150,
            onEnd: onCellDragNDropEnd
        });
    });
}

EventBus.subscribe(HTML_INJECTED, bindSidebarEvents);
EventBus.subscribe(CELL_HOVERING_START, onCellHoverStartSidebar);
EventBus.subscribe(CELL_HOVERING_END, onCellHoverEndSidebar);
