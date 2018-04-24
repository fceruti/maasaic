
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

    $('.js-sidebar-option-btn-edit').click(function(){
        $section = $('.section[data-section-id="' + $(this).attr('data-section-id') + '"]')
        var sectionAttr = {
            id: $section.attr('data-section-id'),
            name: $section.attr('data-name'),
            htmlId: $section.attr('data-html_id'),
            nRows: $section.attr('data-n_rows'),
            nCols: $section.attr('data-n_cols'),
            cssBackground: $section.attr('data-css_background'),
            cssPaddingTop: $section.attr('data-css_padding_top'),
            cssPaddingBottom: $section.attr('data-css_padding_bottom')
        }

        EventBus.fire(SECTION_EDIT_MODAL_REQUEST, sectionAttr);
    });
}

EventBus.subscribe(HTML_INJECTED, bindSidebarEvents);
EventBus.subscribe(CELL_HOVERING_START, onCellHoverStartSidebar);
EventBus.subscribe(CELL_HOVERING_END, onCellHoverEndSidebar);
