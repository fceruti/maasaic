

function onCellModalRequest(sectionCellProperties, cellObj) {
    console.log('onCellModalRequest', sectionCellProperties, cellObj)

    var cellWidth = sectionCellProperties['colWidth'] * cellObj['w'],
        cellHeight = sectionCellProperties['rowHeight'] * cellObj['h'],
        defaultPadding = sectionCellProperties['defaultPadding'],
        defaultBackground = sectionCellProperties['defaultBackground'];

    // Initial values
    var initialBackground = defaultBackground;
    if(cellObj.hasOwnProperty('css') && cellObj['css'].hasOwnProperty('background')){
        initialBackground = cellObj['css']['background'];
    }
    var initialPadding= defaultPadding;
    if(cellObj.hasOwnProperty('css') && cellObj['css'].hasOwnProperty('padding')){
        initialPadding = cellObj['css']['padding'];
    }

    // Form url
    var formUrl;
    if (cellObj['id'] == null) {
        formUrl = '/sites/' + cellObj['subdomain'] +
                  '/pages/' + cellObj['pageId'] +
                  '/sections/' + cellObj['sectionId'] +
                  '/cells/create';
    } else {
        formUrl = '/sites/' + cellObj['subdomain'] +
                  '/pages/' + cellObj['pageId'] +
                  '/sections/' + cellObj['sectionId'] +
                  '/cells/' + cellObj['id'] + '/update';
    }

    if(cellObj['cellType'] == 'TEXT') {
        // Initialize modal
        var modalHtml =
            '<div class="modal-header">' +
                '<h5 class="modal-title"><i class="fa fa-font"></i> New Text cell</h5>' +
                '<button type="button" class="close" data-dismiss="modal" aria-label="Close">' +
                    '<span aria-hidden="true">&times;</span>' +
                '</button>' +
            '</div>' +
            '<form class="ajax-form" method="POST" action="' + formUrl + '">' +
                '<div class="modal-body">' +
                    '<div id="summernote"></div>' +
                    '<input    name="csrfmiddlewaretoken" value="' + csrfmiddlewaretoken + '"   type="hidden" />' +
                    '<input    name="id"                  value="' + cellObj['id'] + '"         type="hidden" />' +
                    '<input    name="cell_type"           value="' + cellObj['cellType'] + '"   type="hidden" />' +
                    '<input    name="section"             value="' + cellObj['sectionId'] + '"  type="hidden" />' +
                    '<input    name="x"                   value="' + cellObj['x'] + '"          type="hidden" />' +
                    '<input    name="y"                   value="' + cellObj['y'] + '"          type="hidden" />' +
                    '<input    name="w"                   value="' + cellObj['w'] + '"          type="hidden" />' +
                    '<input    name="h"                   value="' + cellObj['h'] + '"          type="hidden" />' +
                    '<textarea name="content" id="cell-form-content" class="hidden">' + cellObj['content'] + '</textarea>' +
                '</div>' +
                '<div class="modal-footer">' +
                    '<button type="button" class="btn btn-link text-danger" data-dismiss="modal">Cancel</button>' +
                    '<button type="submit" class="btn btn-success" id="modal-btn"><i class="fa fa-plus-circle"></i> Create text cell</button>' +
                '</div>' +
            '</form>';
        $('#insert-cell-modal .modal-content').html(modalHtml);
        $('#insert-cell-modal').modal('show');

        // Callbacks
        function onSummernoteChange() {
            $('#cell-form-content').val($('.note-editable').html());
        }

        // Summernote
        $('#summernote').summernote({
            dialogsInBody: true,
            height: cellHeight,
            toolbar: [
                ['style', ['bold', 'italic', 'underline', 'clear']],
                ['font', ['strikethrough', 'superscript', 'subscript']],
                ['fontsize', ['fontname', 'fontsize']],
                ['color', ['color']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['height', ['height']],
                ['custom', ['padding', 'backgroundColor']],
            ],
            fontNames: fontNames,
            lineHeights: ['0.5', '0.8', '1.0', '1.2', '1.4', '1.5', '1.6', '1.8', '2.0', '3.0'],
            fontSizes: ['8', '10', '12', '13', '14', '16', '18', '20', '24', '30', '32', '36', '42', '56', '64', '72', '92'],
            callbacks: {
                onChange: onSummernoteChange,
                onPaste: onSummernoteChange
            }
        });
        $('.note-editing-area').css({
            'height': cellHeight + 'px',
            'width': cellWidth + 'px',
            'margin': '20px auto',
            'border': '1px solid #333',
            'background': initialBackground});
        $('.note-statusbar').css({'display': 'none'});

        // Padding plugin
        $('.note-editable').css({'padding': initialPadding});
        $('#summernote-padding-input').attr('value', initialPadding);
        $('#summernote-padding-input').on('keyup', function(){
            $('.note-editable').css({'padding': $(this).val()});
        });

        // Background plugin
        $('#summernote-bg-color-input').colorpicker({'color': initialBackground});
        $('#summernote-bg-color-input').on('change', function(){
            $('.note-editing-area').css({'background': $(this).val()})
        });

        // Bind ajax form
    }
}

EventBus.subscribe(CELL_MODAL_REQUEST, onCellModalRequest)
