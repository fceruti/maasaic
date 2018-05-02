
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

    $('.section-list-item > .sidebar-item').hover(
        function() {
            var sectionId = $(this).closest('.section-list-item').attr('data-section-id');
            EventBus.fire(SECTION_HOVERING_START, sectionId);
        }, function() {
            var sectionId = $(this).closest('.section-list-item').attr('data-section-id');
            EventBus.fire(SECTION_HOVERING_END, sectionId);
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

    $('.js-sidebar-section-btn-edit').click(function(){
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

    $('.js-sidebar-cell-btn-edit').mousedown(function(){
        $cell_list_item = $(this).closest('.cell-list-item');
        var sectionId = $cell_list_item.data('section-id'),
            cellId = $cell_list_item.data('cell-id');
        $cell = $('.cell.cell--layer-edit[data-section-id=' + sectionId + '][data-cell-id=' + cellId + ']')

        var sectionCellProperties= getSectionCellProperties(sectionId);
        var cellObj = {
            id: cellId,
            sectionId: sectionId,
            cellType: $cell.data('type'),
            x: $cell.data('x'),
            y: $cell.data('y'),
            w: $cell.data('w'),
            h: $cell.data('h'),
            content: $('.cell.cell--layer-view[data-cell-id=' + cellId + '] .cell-inner').html(),
            css: getCellCss($cell)
        };
        EventBus.fire(CELL_MODAL_REQUEST, sectionCellProperties, cellObj);
    });

    $('.js-section-show-borders-btn').click(function(){
        $('.section-inner').toggleClass('show-borders');
        $(this).find('span').text($(this).find('span').html() == "Hide grid" ? "Show grid" : "Hide grid");
    })

}

EventBus.subscribe(HTML_INJECTED, bindSidebarEvents);
EventBus.subscribe(CELL_HOVERING_START, onCellHoverStartSidebar);
EventBus.subscribe(CELL_HOVERING_END, onCellHoverEndSidebar);
