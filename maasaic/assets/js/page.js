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
            '[data-section=' + sectionId + ']' +
            '[data-x=' + x + ']' +
            '[data-y=' + y + ']');
}

function getInsertAreaDimensions(){
    var startX = Math.min(insertOptions['startPos'][0], insertOptions['stopPos'][0]),
        stopX = Math.max(insertOptions['startPos'][0], insertOptions['stopPos'][0]),
        startY = Math.min(insertOptions['startPos'][1], insertOptions['stopPos'][1]),
        stopY = Math.max(insertOptions['startPos'][1], insertOptions['stopPos'][1]);
    return [startX, stopX, startY, stopY];
}

/*******************************************************************************
* Insert cells
*******************************************************************************/
var insertOptions = {
    isInserting: false,
    sectionId: null,
    startPos: null,  // Array of the form [x, y]
    stopPos: null  // Array of the form [x, y]
}

function startInsert(cell) {
    clearInsertOptions();
    insertOptions['isInserting'] = true;
    insertOptions['sectionId'] = parseInt($(cell).attr('data-section'));
    var initialPos = getCellPosition(cell);
    insertOptions['startPos'] = initialPos;
    insertOptions['stopPos'] = initialPos;
    $('.insert-layer[data-section=' + insertOptions['sectionId'] + ']').addClass('is-inserting');
    drawInsertArea();
    drawInsertControls();
}

function moveInsert(cell) {
    if(insertOptions['isInserting'] == false ||
       $(cell).attr('data-section') != insertOptions['sectionId'])
        return
    insertOptions['stopPos'] = getCellPosition(cell);
    drawInsertArea();
}

function stopInsert(cell) {
    insertOptions['isInserting'] = false;
    insertOptions['stopPos'] = getCellPosition(cell);
    drawInsertArea();
    drawInsertControls();
}

function clearInsertOptions() {
    insertOptions['isInserting'] = false;
    insertOptions['sectionId'] = null;
    insertOptions['startPos'] = null;
    insertOptions['stopPos'] = null;
    $('.cell.cell--layer-insert').removeClass('inserting');
}

function drawInsertArea() {
    if (insertOptions['isInserting'] === false) return;

    // Calculate start & stop positions
    var insertAreaDimensions = getInsertAreaDimensions();
    var startX = insertAreaDimensions[0],
        stopX = insertAreaDimensions[1],
        startY = insertAreaDimensions[2],
        stopY = insertAreaDimensions[3];
    var sectionId = insertOptions['sectionId'];

    // Remove any previous left overs
    $('.cell.cell--layer-insert').removeClass('is-inserting').removeClassStartingWith('edge-');

    // Add is-inserting and edge-* to selected cells
    $('.cell.cell--layer-insert[data-section=' + sectionId + ']').each(function(){
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
    $('.insert-layer[data-section=' + insertOptions['sectionId'] + ']').removeClass('is-inserting');
    $('.cell.cell--layer-insert').removeClass('is-inserting').removeClassStartingWith('edge-');
    $('.insert-cell-ctrl').addClass('hidden');
    clearInsertOptions();
}

function drawInsertControls() {
    var sectionId = insertOptions['sectionId'];
    $insertCellCtrl = $('.insert-cell-ctrl[data-section=' + sectionId + ']');
    if(sectionId != null &&
       insertOptions['isInserting'] === false &&
       insertOptions['startPos'] != null &&
       insertOptions['stopPos'] != null) {
        var insertAreaDimensions = getInsertAreaDimensions();
        var startX = insertAreaDimensions[0],
            stopX = insertAreaDimensions[1],
            startY = insertAreaDimensions[2],
            stopY = insertAreaDimensions[3];
        var $startInsertCell = getCell('insert', sectionId, startX, startY);
        var $stopInsertCell = getCell('insert', sectionId, stopX, stopY);
        var startInsertTop = $startInsertCell.position().top;
        var stopInsertBottom = $stopInsertCell.position().top + $stopInsertCell.outerHeight(true);
        var startInsertLeft = $startInsertCell.position().left;
        var stopInsertRight = $stopInsertCell.position().left + $stopInsertCell.outerWidth(true);
        var insertCellCtrlTop = startInsertTop + ((stopInsertBottom - startInsertTop) / 2) - 60;
        var insertCellCtrlLeft = startInsertLeft + ((stopInsertRight - startInsertLeft) / 2) - 90;
        $insertCellCtrl
            .css({top: insertCellCtrlTop, left: insertCellCtrlLeft})
            .removeClass('hidden');
    } else {
        $insertCellCtrl.addClass('hidden');
    }
}

function bindInsertEvents (){
    $('.cell.cell--layer-insert').mousedown(function(){
        if(insertOptions['startPos'] != null || insertOptions['stopPos'] != null){
            clearInsertArea();
            drawInsertControls();
        }else{
            startInsert(this);
        }
    });

    $('.cell.cell--layer-insert').mouseover(function(){
        if(insertOptions['isInserting'] === false) return
        moveInsert(this);
    });

    $(document).mouseup(function(event){
        if($(event.target).hasClass('cell--layer-insert')) {
            if(insertOptions['isInserting'] === false) return
            stopInsert(event.target);
        } else {
            clearInsertArea();
            drawInsertControls();
        }
    });
}

/*******************************************************************************
* Move cell
*******************************************************************************/
//var moveOptions = {
//    moving: false,
//    cellId: null,
//    sectionId: null,
//    startX: null,
//    startY: null,
//    h: null,
//    w: null,
//
//}
//function startMovingCell(btn){
//    $cell = $(btn).closest('.cell.edit-cell');
//    var w = parseInt($cell.attr('data-w')),
//        h = parseInt($cell.attr('data-h')),
//        x = parseInt($cell.attr('data-x')),
//        y = parseInt($cell.attr('data-w')),
//        sectionId = parseInt($cell.attr('data-section')),
//        cellId = parseInt($cell.attr('data-id'));
//
//    moveOptions['moving'] = true;
//    moveOptions['cellId'] = cellId;
//    moveOptions['sectionId'] = sectionId;
//    moveOptions['startX'] = x;
//    moveOptions['startY'] = y;
//    moveOptions['h'] = h;
//    moveOptions['w'] = w;
//
//    $('.cell-move-cell.cannot-insert[data-section=' + sectionId + ']')
//        .removeClassStartingWith('move-');
//    $('.cell-move-cell.cannot-insert[data-section=' + sectionId + ']').each(function(cell){
//        var cellX = $cell.attr('data-x'),
//            cellY = $cell.attr('data-y');
//        if (x <= cellX && cellX <= x + w -1 &&
//            y <= cellY && cellY <= y + h -1){
//            $cell.addClass('move-ok')
//        }else{
//            $cell.addClass('move-not-ok')
//        }
//    });
//
//    $('.moving-cell[data-section=' + sectionId + ']')
//        .removeClassStartingWith('cell--')
//        .addClass('cell--w-' + w)
//        .addClass('cell--h-' + h)
//        .addClass('cell--x-' + x)
//        .addClass('cell--y-' + y)
//        .html($cell.html())
//
//    $('.move-layer').removeClass('hidden')
//
//}
//
//function doMoveCell(){
//
//}
//
//function stopMoveCell(){
//
//}
//
//function bindMoveCellEvents() {
//    $('.edit-cell-ctrl-btn-move').mousedown(function(){
//        startMovingCell(this);
//    });
//    $('.move-cell').mouseover(function(){
//        if(moveOptions['moving'] === false) return
//        doMoveCell(this);
//        drawInsertArea();
//    });
//
//    $(document).mouseup(function(event){
//        if($(event.target).hasClass('insert-cell')) {
//            if(insertOptions['inserting'] === false) return
//            stopInsert(this);
//            drawInsertArea();
//        } else {
//            clearInsertArea();
//        }
//    });
//
//}

EventBus.subscribe(HTML_INJECTED, bindInsertEvents);

//var isMoving = false;
//var startCell = null;
//var endCell = null;
//var textEditor = null;
//
//
///*****************************************************************************
//* Helpers
//*****************************************************************************/
//function removeDataAttributes(target) {
//
//    var i,
//        $target = $(target),
//        attrName,
//        dataAttrsToDelete = [],
//        dataAttrs = $target.get(0).attributes,
//        dataAttrsLen = dataAttrs.length;
//
//    // loop through attributes and make a list of those
//    // that begin with 'data-'
//    for (i=0; i<dataAttrsLen; i++) {
//        if ( 'data-' === dataAttrs[i].name.substring(0,5) ) {
//            // Why don't you just delete the attributes here?
//            // Deleting an attribute changes the indices of the
//            // others wreaking havoc on the loop we are inside
//            // b/c dataAttrs is a NamedNodeMap (not an array or obj)
//            dataAttrsToDelete.push(dataAttrs[i].name);
//        }
//    }
//    // delete each of the attributes we found above
//    // i.e. those that start with "data-"
//    $.each( dataAttrsToDelete, function( index, attrName ) {
//        $target.removeAttr( attrName );
//    })
//};
//
///*****************************************************************************
//* Active edit cells
//*****************************************************************************/
//function drawActiveEditCells(){
//    if(startCell !== null && startCell !== undefined &&
//       endCell !== null && endCell !== undefined &&
//       startCell[0] == endCell[0]) {
//
//        var sectionId = startCell[0];
//        var fromX = Math.min(startCell[1], endCell[1]);
//        var toX = Math.max(startCell[1], endCell[1]);
//        var fromY = Math.min(startCell[2], endCell[2]);
//        var toY = Math.max(startCell[2], endCell[2]);
//
//        $('.insert-cell[data-section=' + sectionId + ']')
//            .removeClass('active').removeClass('error').removeClass('border-top').removeClass('border-right').removeClass('border-bottom').removeClass('border-left');
//
//        for(var i=fromX; i <= toX; i++){
//            for(var j=fromY; j <= toY; j++){
//                $ele = $('.insert-cell[data-section=' + sectionId+ '][data-x=' + i + '][data-y=' + j + ']')
//                $ele.addClass('active');
//                if(j==fromY){$ele.addClass('border-top')}
//                if(j==toY){$ele.addClass('border-bottom')}
//                if(i==fromX){$ele.addClass('border-left')}
//                if(i==toX){$ele.addClass('border-right')}
//                if(cellHasCollision(sectionId, i, j)) {
//                    $ele.addClass('error');
//                }
//            }
//        }
//    }
//}
//
//function clearActiveEditCells() {
//    $('.insert-cell.active').removeClass('active').removeClass('error');
//}
//
///*****************************************************************************
//* Collisions
//*****************************************************************************/
//function insertHasCollision(sectionId) {
//    var hasCollision = false;
//    $('.insert-cell.active').each(function(){
//        if(cellHasCollision(sectionId, $(this).attr('data-x'), $(this).attr('data-y'))) {
//            return hasCollision = true;
//        }
//    });
//    return hasCollision;
//}
//
//function cellHasCollision(sectionId, x, y) {
//    var hasCollision = false;
//    $('.cell[data-section=' + sectionId + ']').each(function(){
//        var dataX = parseInt($(this).attr('data-x'));
//        var dataY = parseInt($(this).attr('data-y'));
//        var dataW = parseInt($(this).attr('data-w'));
//        var dataH = parseInt($(this).attr('data-h'));
//
//        if(x <= (dataX + dataW - 1) && x >= dataX &&
//           y <= (dataY + dataH - 1) && y >= dataY){
//            return hasCollision = true;
//        }
//    })
//    return hasCollision;
//}
//
//function activeCellsDimensions(sectionId){
//    var minX = 10000, maxX = 0, minY = 10000, maxY = 0;
//    $('.insert-cell.active[data-section=' + sectionId + ']').each(function(){
//        console.log(this)
//        var dataX = parseInt($(this).attr('data-x'));
//        var dataY = parseInt($(this).attr('data-y'));
//        if(dataX < minX) {minX = dataX;}
//        if(dataX > maxX) {maxX = dataX;}
//        if(dataY < minY) {minY = dataY;}
//        if(dataY > maxY) {maxY = dataY;}
//    })
//    return {x: minX, y:minY, w:maxX - minX + 1, h:maxY - minY + 1}
//}
///*****************************************************************************
//* Cell Options
//*****************************************************************************/
//function showInsertCellOptions(sectionId) {
//    var x0 = startCell[1], x1 = endCell[1],
//        y0 = startCell[2], y1 =  endCell[2];
//    var top = ((y1 - y0) * CELL_HEIGHT / 2) + ((y0 - 1) * CELL_HEIGHT) + 70;
//    var left = ((x1 - x0)  * CELL_WIDTH / 2) + ((x0 - 1) * CELL_WIDTH) + 10;
//    $('.insert-cell-panel[data-section=' + sectionId + ']').removeClass('hidden');
//    $('.insert-cell-panel[data-section=' + sectionId + ']').css({'top': top, 'left': left});
//}
//
//function clearInsertCellOptions() {
//    $('.insert-cell-panel').addClass('hidden');
//}
//
///*****************************************************************************
//* Popups
//*****************************************************************************/
//function showEditTextPopup(sectionId, cellId, x, y, w, h, content, innerCss) {
//    $('.edit-cell-popup-wrapper').addClass('hidden');
//
//    $('#editing-cell').removeClass();
//    removeDataAttributes('#editing-cell');
//    $('#editing-cell').attr('data-section-id', sectionId);
//    $('#editing-cell').attr('data-cell-id', cellId);
//    $('#editing-cell').attr('data-x', x);
//    $('#editing-cell').attr('data-y', y);
//    $('#editing-cell').attr('data-w', w);
//    $('#editing-cell').attr('data-h', h);
//    $('#editing-cell').addClass('cell-width-' + w);
//    $('#editing-cell').addClass('cell-height-' + h);
//    $('#editing-cell-inner').html(content);
//    $('#editing-cell-inner').css(innerCss)
//    textEditor.trumbowyg('html', content);
//    $('#edit-cell-popup').removeClass('hidden');
//    $('#edit-cell-popup-text').removeClass('hidden');
//}
//
//$(document).ready(function(){
//
//    $('.insert-cell').mousedown(function(){
//        isMoving = true;
//        startCell = [parseInt($(this).attr('data-section')), parseInt($(this).attr('data-x')), parseInt($(this).attr('data-y'))];
//        endCell = [parseInt($(this).attr('data-section')), parseInt($(this).attr('data-x')), parseInt($(this).attr('data-y'))];
//        drawActiveEditCells();
//        clearInsertCellOptions();
//    });
//
//    $('.insert-cell').mouseup(function(){
//        isMoving = false;
//        var sectionId = parseInt($(this).attr('data-section'));
//        endCell = [sectionId, parseInt($(this).attr('data-x')), parseInt($(this).attr('data-y'))];
//        if(insertHasCollision(sectionId)) {
//            clearActiveEditCells();
//            clearInsertCellOptions();
//        } else {
//            drawActiveEditCells();
//            showInsertCellOptions(sectionId);
//        }
//    });
//
//    $('.insert-cell').mouseover(function(){
//        if(isMoving === true){
//            var sectionId = parseInt($(this).attr('data-section'));
//            endCell = [sectionId, parseInt($(this).attr('data-x')), parseInt($(this).attr('data-y'))];
//            drawActiveEditCells();
//        }
//    });
//
//    $('#insert-cell-text-btn').click(function() {
//        var sectionId = parseInt($(this).attr('data-section'));
//        var dims = activeCellsDimensions(sectionId);
//        showEditTextPopup('', '', dims['x'], dims['y'], dims['w'], dims['h'], '<p>Add your text here</p>', {'padding': 20});
//    })
//
//    $('.close-button').click(function(){
//        $(this).closest('.closable').addClass('hidden');
//        clearInsertCellOptions();
//        clearActiveEditCells();
//    });
//
//    textEditor = $('#text-editor').trumbowyg({
//        btns: [
//            ['viewHTML'],
//            ['fontfamily', 'fontsize'],
//            ['foreColor', 'backColor'],
//            ['strong', 'em', 'del', 'superscript', 'subscript'],
//            ['lineheight'],
//            ['link'],
//            ['justifyLeft', 'justifyCenter', 'justifyRight', 'justifyFull'],
//            ['unorderedList', 'orderedList'],
//            ['removeformat'],
//        ],
//        resetCss: false,
//        autogrow: true,
//        removeformatPasted: true
//    });
//
//    textEditor.trumbowyg().on('tbwchange', function(){
//        $('#editing-cell-inner').html(textEditor.trumbowyg('html'));
//    });
//});
