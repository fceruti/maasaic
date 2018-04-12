
function onCellHoverStart(sectionId, cellId) {
    console.log(onCellHoverStart, sectionId, cellId)
    $('.cell-list-item[data-section-id="' + sectionId + '"][data-cell-id="' + cellId + '"] .sidebar-item').addClass('hover');
}

function onCellHoverEnd(sectionId, cellId) {
    $('.cell-list-item[data-section-id="' + sectionId + '"][data-cell-id="' + cellId + '"] .sidebar-item').removeClass('hover');
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
}

EventBus.subscribe(HTML_INJECTED, bindSidebarEvents);
EventBus.subscribe(CELL_HOVERING_START, onCellHoverStart);
EventBus.subscribe(CELL_HOVERING_END, onCellHoverEnd);
