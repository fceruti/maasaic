/*******************************************************************************
* Globals
*******************************************************************************/
var STATE_INSERT_AREA_DRAWING = 'STATE_INSERT_AREA_DRAWING';
var STATE_INSERT_AREA_SELECTED = 'STATE_INSERT_AREA_SELECTED'
var STATE_MOVE = 'MOVE';
var STATE_VIEW = 'VIEW';
var appState = STATE_VIEW;


/*******************************************************************************
* Utils functions
*******************************************************************************/
$.fn.removeClassStartingWith = function (filter) {
    $(this).removeClass(function (index, className) {
        return (className.match(new RegExp("\\S*" + filter + "\\S*", 'g')) || []).join(' ')
    });
    return this;
};

function getCellPosition(cell) {
    return [parseInt($(cell).attr('data-x')), parseInt($(cell).attr('data-y'))]
}

function getCell(layer, sectionId, x, y) {
   return $('.cell.cell--layer-' + layer +
            '[data-section-id=' + sectionId + ']' +
            '[data-x=' + x + ']' +
            '[data-y=' + y + ']');
}

function getSectionCellProperties(sectionId) {
    var $section = $('.section[data-section-id=' + sectionId + ']')
    var totalWidth = parseInt($section.attr('data-width')),
        totalCols = parseInt($section.attr('data-n_cols')),
        padding = $section.attr('data-cell_default_padding'),
        margin = $section.attr('data-cell_default_margin'),
        background = $section.attr('data-cell_default_background'),
        border = $section.attr('data-cell_default_border'),
        borderRadius = $section.attr('data-cell_default_border_radius'),
        shadow = $section.attr('data-cell_default_shadow');
    var cellHeight = totalWidth / totalCols;
    return {'colWidth': totalWidth / totalCols,
            'rowHeight': cellHeight,
            'padding': padding,
            'margin': margin,
            'background': background,
            'border': border,
            'borderRadius': borderRadius,
            'shadow': shadow};
}

function getSectionParentsUrlParts(sectionId) {
    var $section = $('.section[data-section-id=' + sectionId + ']');
    var $page = $section.closest('.page');
    var websiteSubdomain = $page.attr('data-website-subdomain'),
        pageId = $page.attr('data-page-id');
    return {'websiteSubdomain': websiteSubdomain,
            'pageId': pageId};
}


/*******************************************************************************
* Insert cells
*******************************************************************************/
var insertOptions = {
    sectionId: null,
    startPos: null,  // Array of the form [x, y]
    stopPos: null  // Array of the form [x, y]
}

function getInsertAreaDimensions(){
    var startX = Math.min(insertOptions['startPos'][0], insertOptions['stopPos'][0]),
        stopX = Math.max(insertOptions['startPos'][0], insertOptions['stopPos'][0]),
        startY = Math.min(insertOptions['startPos'][1], insertOptions['stopPos'][1]),
        stopY = Math.max(insertOptions['startPos'][1], insertOptions['stopPos'][1]);
    return {'startX': startX,
            'stopX': stopX,
            'startY': startY,
            'stopY': stopY};
}

function startInsert(cell) {
    clearInsertOptions();
    appState = STATE_INSERT_AREA_DRAWING;
    EventBus.fire(STATE_CHANGED);
    insertOptions['sectionId'] = parseInt($(cell).attr('data-section-id'));
    var initialPos = getCellPosition(cell);
    insertOptions['startPos'] = initialPos;
    insertOptions['stopPos'] = initialPos;
    $('.insert-layer[data-section-id=' + insertOptions['sectionId'] + ']').addClass('is-inserting');
    drawInsertArea();
    drawInsertControls();
}

function moveInsert(cell) {
    if(appState != STATE_INSERT_AREA_DRAWING ||
       $(cell).attr('data-section-id') != insertOptions['sectionId'])
        return
    insertOptions['stopPos'] = getCellPosition(cell);
    drawInsertArea();
}

function stopInsert(cell) {
    appState = STATE_INSERT_AREA_SELECTED;
    EventBus.fire(STATE_CHANGED);
    insertOptions['stopPos'] = getCellPosition(cell);
    drawInsertArea();
    drawInsertControls();
}

function clearInsertOptions() {
    insertOptions['sectionId'] = null;
    insertOptions['startPos'] = null;
    insertOptions['stopPos'] = null;
}

function drawInsertArea() {
    if (appState != STATE_INSERT_AREA_DRAWING) return;

    // Calculate start & stop positions
    var insertAreaDimensions = getInsertAreaDimensions();
    var startX = insertAreaDimensions['startX'],
        stopX = insertAreaDimensions['stopX'],
        startY = insertAreaDimensions['startY'],
        stopY = insertAreaDimensions['stopY'];
    var sectionId = insertOptions['sectionId'];

    // Remove any previous left overs
    $('.cell.cell--layer-insert').removeClass('is-inserting').removeClassStartingWith('edge-');

    // Add is-inserting and edge-* to selected cells
    $('.cell.cell--layer-insert[data-section-id=' + sectionId + ']').each(function(){
        $tmpCell = $(this);
        var x = $tmpCell.attr('data-x'),
            y = $tmpCell.attr('data-y');
        if(startX <= x && x <= stopX && startY <= y && y <= stopY){
            $tmpCell.addClass('is-inserting');
            if(x == startX){$tmpCell.addClass('edge-left');}
            if(x == stopX){$tmpCell.addClass('edge-right');}
            if(y == startY){$tmpCell.addClass('edge-top');}
            if(y == stopY){$tmpCell.addClass('edge-bottom');}
        }
    });
}

function clearInsertArea() {
    $('.insert-layer[data-section-id=' + insertOptions['sectionId'] + ']').removeClass('is-inserting');
    $('.cell.cell--layer-insert').removeClass('is-inserting').removeClassStartingWith('edge-');
    $('.insert-cell-ctrl').addClass('hidden');
}

function drawInsertControls() {
    var sectionId = insertOptions['sectionId'];
    $insertCellCtrl = $('.insert-cell-ctrl[data-section-id=' + sectionId + ']');
    if(sectionId != null &&
       appState != STATE_INSERT_AREA_DRAWING &&
       insertOptions['startPos'] != null &&
       insertOptions['stopPos'] != null) {
        var insertAreaDimensions = getInsertAreaDimensions();
        var startX = insertAreaDimensions['startX'],
            stopX = insertAreaDimensions['stopX'],
            startY = insertAreaDimensions['startY'],
            stopY = insertAreaDimensions['stopY'];
        var $startInsertCell = getCell('insert', sectionId, startX, startY);
        var $stopInsertCell = getCell('insert', sectionId, stopX, stopY);
        var startInsertTop = $startInsertCell.position().top;
        var stopInsertBottom = $stopInsertCell.position().top + $stopInsertCell.outerHeight(true);
        var startInsertLeft = $startInsertCell.position().left;
        var stopInsertRight = $stopInsertCell.position().left + $stopInsertCell.outerWidth(true);
        var insertCellCtrlTop = startInsertTop + ((stopInsertBottom - startInsertTop) / 2) - 65;
        var insertCellCtrlLeft = startInsertLeft + ((stopInsertRight - startInsertLeft) / 2) - 90;
        $insertCellCtrl
            .css({top: insertCellCtrlTop, left: insertCellCtrlLeft})
            .removeClass('hidden');
    } else {
        $insertCellCtrl.addClass('hidden');
    }
}

function onInsertCellBtnClicked(target) {
    var cellType = $(target).closest('.js-insert-cell-btn').attr('data-cell-type');
    var sectionId = insertOptions['sectionId'];
    var areaDimensions = getInsertAreaDimensions();
    var sectionCellProperties= getSectionCellProperties(sectionId);

    var startX = areaDimensions['startX'],
        stopX = areaDimensions['stopX'],
        startY = areaDimensions['startY'],
        stopY = areaDimensions['stopY'];
    var x = startX,
        y = startY,
        w = stopX - startX + 1,
        h = stopY - startY + 1;

    var cellObj = {
        id: null,
        cellType: cellType,
        sectionId: sectionId,
        x: x, y: y, w: w, h: h,
        content: '',
        css: {}
    };

    EventBus.fire(CELL_MODAL_REQUEST, sectionCellProperties, cellObj);
}


function bindInsertEvents (){
    EventBus.subscribe(STATE_CHANGED, function(){
        if (appState != STATE_INSERT_AREA_SELECTED) {
            clearInsertArea();
            clearInsertOptions();
        }
        drawInsertControls();
    })

    $('.cell.cell--layer-insert').mousedown(function(){
        if(insertOptions['startPos'] != null || insertOptions['stopPos'] != null){
            clearInsertArea();
            clearInsertOptions();
            drawInsertControls();
        }else{
            startInsert(this);
        }
    });

    $('.cell.cell--layer-insert').mouseover(function(){
        if(appState != STATE_INSERT_AREA_DRAWING) return
        moveInsert(this);
    });

    $(document).mouseup(function(event){
        $target = $(event.target);

        // User has lifted the mouse inside a valid area
        if(appState == STATE_INSERT_AREA_DRAWING &&
           $target.hasClass('cell--layer-insert')) {
           return stopInsert(event.target);
        }

        // Is inserting but lifted elsewhere
        if (appState == STATE_INSERT_AREA_DRAWING) {
            clearInsertArea();
            clearInsertOptions();
            drawInsertControls();
            appState = STATE_VIEW;
            EventBus.fire(STATE_CHANGED);
            return
        }

        // User clicked an insert button
        if(appState == STATE_INSERT_AREA_SELECTED &&
            ($target.hasClass('js-insert-cell-btn') ||
             $target.parent().hasClass('js-insert-cell-btn') ||
             $target.parent().parent().hasClass('js-insert-cell-btn'))){
            return onInsertCellBtnClicked($target);
        }
    });

}
EventBus.subscribe(HTML_INJECTED, bindInsertEvents);



/*******************************************************************************
* Hover cells & sections
*******************************************************************************/
function onCellHoverStart(sectionId, cellId) {
    $('.cell.cell--layer-edit[data-section-id="' + sectionId + '"][data-cell-id="' + cellId + '"]').addClass('hover');
}

function onCellHoverEnd(sectionId, cellId) {
    $('.cell.cell--layer-edit[data-section-id="' + sectionId + '"][data-cell-id="' + cellId + '"]').removeClass('hover');
}


function onSectionHoverStart(sectionId){
    $('.section[data-section-id=' + sectionId + ']').addClass('hover');
}

function onSectionHoverEnd(sectionId){
    $('.section[data-section-id=' + sectionId + ']').removeClass('hover');
}


function bindHoverEvents() {
    $('.cell.cell--layer-edit').hover(
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


EventBus.subscribe(CELL_HOVERING_START, onCellHoverStart);
EventBus.subscribe(CELL_HOVERING_END, onCellHoverEnd);
EventBus.subscribe(SECTION_HOVERING_START, onSectionHoverStart);
EventBus.subscribe(SECTION_HOVERING_END, onSectionHoverEnd);
EventBus.subscribe(HTML_INJECTED, bindHoverEvents);


/*******************************************************************************
* Move cell
*******************************************************************************/
var moveOptions = {
    cellId: null,
    sectionId: null,
    h: null,
    w: null
};

function startMovingCell(btn){
    appState = STATE_MOVE;
    EventBus.fire(STATE_CHANGED);
    $cell = $(btn).closest('.cell.cell--layer-edit');

    moveOptions['cellId'] = parseInt($cell.attr('data-cell-id'));
    moveOptions['sectionId'] = parseInt($cell.attr('data-section-id'));
    moveOptions['h'] = parseInt($cell.attr('data-h'));
    moveOptions['w'] = parseInt($cell.attr('data-w'));

    doMoveCell($cell);
    $('.move-layer').removeClass('hidden');
}

function doMoveCell(cell){
    $('.cell--layer-move.is-moving').removeClass('is-moving')
    var x = parseInt($(cell).attr('data-x')),
        y = parseInt($(cell).attr('data-y'));

    var sectionId = $(cell).attr('data-section-id');
    for(var i = 0; i < moveOptions['w']; i++) {
        for(var j = 0; j < moveOptions['h']; j++) {
            $('.cell--layer-move[data-x=' + (x + i) + '][data-y=' + (y + j) + '][data-section-id=' + sectionId +  ']')
                .addClass('is-moving')
        }
    }
}

function stopMoveCell(cell){
    var url = '/cells/' + moveOptions['cellId'] + '/move';
    var data = {'x': parseInt($(cell).attr('data-x')),
                'y': parseInt($(cell).attr('data-y'))};
    performPost(url, data);
    clearMoveArea();
    clearMoveOptions();
}

function clearMoveOptions() {
    moveOptions['moving'] = null;
    moveOptions['cellId'] = null;
    moveOptions['sectionId'] = null;
    moveOptions['h'] = null;
    moveOptions['w'] = null;
}

function clearMoveArea() {
    $('.moving-cell')
        .addClass('hidden')
        .removeClassStartingWith('cell--');
}

function userCancelMove() {
    clearMoveArea();
    clearMoveOptions();
    appState = STATE_VIEW;
    EventBus.fire(STATE_CHANGED);
}


function bindMoveCellEvents() {
    EventBus.subscribe(STATE_CHANGED, function(){
        if (appState != STATE_MOVE) {
            $('.move-layer').addClass('hidden');
        }
    })

    $('.js-edit-cell-ctrl-btn-move').mousedown(function(){
        startMovingCell(this);
    });
    $('.cell--layer-move').mouseover(function(){
        if(appState == STATE_MOVE) {
            doMoveCell(this);
        }
    });

    $(document).mouseup(function(event){
        $target = $(event.target)
        // User has lifted the mouse inside a valid area
        if(appState == STATE_MOVE &&
           $target.hasClass('cell--layer-move')) {
           return stopMoveCell(event.target);
        }

        // Is moving but lifted elsewhere
        if (appState == STATE_MOVE) {
            return userCancelMove();
        }

        // Cleanup
        clearMoveArea();
        clearMoveOptions();
    });

    $('[data-toggle="tooltip"]').tooltip()

}

EventBus.subscribe(HTML_INJECTED, bindMoveCellEvents);

/*******************************************************************************
* Edit cell
*******************************************************************************/
function getCellCss($cell) {
    var padding = $cell.attr('data-padding'),
        margin = $cell.attr('data-margin'),
        background = $cell.attr('data-background'),
        border = $cell.attr('data-border'),
        borderRadius = $cell.attr('data-border_radius'),
        shadow = $cell.attr('data-shadow');

    return {'padding': padding,
            'margin': margin,
            'background': background,
            'border': border,
            'borderRadius': borderRadius,
            'shadow': shadow};
}


function bindEditCellEvents() {
    $('.js-edit-cell-ctrl-btn-edit').mousedown(function(){
        $cell = $(this).closest('.cell.cell--layer-edit');
        var cellId = $cell.attr('data-cell-id');
        var sectionId = $cell.attr('data-section-id');
        var sectionCellProperties= getSectionCellProperties(sectionId);
        var cellObj = {
            id: cellId,
            sectionId: sectionId,
            cellType: $cell.attr('data-type'),
            x: $cell.attr('data-x'),
            y: $cell.attr('data-y'),
            w: $cell.attr('data-w'),
            h: $cell.attr('data-h'),
            content: $('.cell.cell--layer-view[data-cell-id=' + cellId + '] .cell-inner').html(),
            css: getCellCss($cell)
        };
        console.log($('.cell.cell--layer-view[data-cell-id=' + cellId + '] .cell-inner').html())
        console.log('.cell.cell--layer-view[data-cell-id=' + cellId + '] .cell-inner')
        EventBus.fire(CELL_MODAL_REQUEST, sectionCellProperties, cellObj);
    });
}

EventBus.subscribe(HTML_INJECTED, bindEditCellEvents);


/*******************************************************************************
* Delete cell
*******************************************************************************/
function bindDeleteCellEvents() {
    $('.js-edit-cell-ctrl-btn-delete').mousedown(function(){
        $cell = $(this).closest('.cell.cell--layer-edit');
        var cellId = $cell.attr('data-cell-id');
        var url = '/cells/' + cellId + '/delete'
        performPost(url, {});
    });
}

EventBus.subscribe(HTML_INJECTED, bindDeleteCellEvents);
