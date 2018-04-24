
function onCellModalRequest(cellProperties, cellObj) {
    console.log('onCellModalRequest', cellProperties, cellObj)

    var cellWidth = cellProperties['colWidth'] * cellObj['w'],
        cellHeight = cellProperties['rowHeight'] * cellObj['h'],
        initialPadding = cellProperties['padding'],
        initialMargin = cellProperties['margin'],
        initialBackground = cellProperties['background'],
        initialBorder = cellProperties['border'],
        initialBorderRadius = cellProperties['borderRadius'],
        initialShadow = cellProperties['shadow'];

    // Initial values
    var background = initialBackground;
    if(cellObj.hasOwnProperty('css') && cellObj['css'].hasOwnProperty('background')){
        background = cellObj['css']['background'];
    }
    var padding = initialPadding;
    if(cellObj.hasOwnProperty('css') && cellObj['css'].hasOwnProperty('padding')){
        padding = cellObj['css']['padding'];
    }
    var margin = initialMargin;
    if(cellObj.hasOwnProperty('css') && cellObj['css'].hasOwnProperty('margin')){
        margin = cellObj['css']['margin'];
    }
    var border = initialBorder;
    if(cellObj.hasOwnProperty('css') && cellObj['css'].hasOwnProperty('border')){
        border = cellObj['css']['border'];
    }
    var borderRadius = initialBorderRadius;
    if(cellObj.hasOwnProperty('css') && cellObj['css'].hasOwnProperty('borderRadius')){
        borderRadius = cellObj['css']['borderRadius'];
    }
    var shadow = initialShadow;
    if(cellObj.hasOwnProperty('css') && cellObj['css'].hasOwnProperty('shadow')){
        shadow = cellObj['css']['shadow'];
    }

    // Form url
    var formUrl, submitText;
    if (cellObj['id'] == null) {
        formUrl = '/cells/create';
        submitText = 'Create cell';
    } else {
        formUrl = '/cells/' + cellObj['id'] + '/update';
        submitText = 'Update cell';
    }
    $('#insert-cell-modal .modal-dialog')
        .removeClass('modal-huge')
        .removeClass('modal-lg');

    if(cellObj['cellType'] == 'TEXT') {
        // Initialize modal
        if(cellWidth > 700){
            $('#insert-cell-modal .modal-dialog').addClass('modal-huge');
        } else {
            if(cellWidth > 500) {
            $('#insert-cell-modal .modal-dialog').addClass('modal-lg');
            }
        }

        var cellProperties = $('#cell-properties-template').html();
        var modalHtml =
            '<div class="modal-header">' +
                '<h5 class="modal-title"><i class="fa fa-font"></i> New Text cell</h5>' +
                '<button type="button" class="close" data-dismiss="modal" aria-label="Close">' +
                    '<span aria-hidden="true">&times;</span>' +
                '</button>' +
            '</div>' +
            '<form class="ajax-form" method="POST" action="' + formUrl + '">' +
                '<div class="modal-body">' +
                    cellProperties +
                    '<br/><h5>Content</h5>' +
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
                    '<button type="submit" class="btn btn-success" id="modal-btn">' + submitText + '</button>' +
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
            'border': '1px solid #333'});
        $('.note-statusbar').css({'display': 'none'});

        if(cellObj['content'] != null && cellObj['content'] != undefined) {
        console.log($(cellObj['content']))
            $('#summernote').summernote('code', $(cellObj['content']));
        }

        $noteWrapper = $('<div></div>')
        $noteWrapper.addClass('note-editable-wrapper');
        var noteWrapperStyle = window['utils']['get_position_dict_from_margin'](margin);
        noteWrapperStyle['position'] = 'absolute';
        noteWrapperStyle['background'] = background;
        noteWrapperStyle['shadow'] = shadow;
        noteWrapperStyle['border'] = border;
        noteWrapperStyle['borderRadius'] = borderRadius;
        $noteWrapper.css(noteWrapperStyle);
        $('.note-editable').wrap($noteWrapper);
        $('.note-editable').css({'height': '100%'});

        // Padding
        $('.note-editable').css({'padding': padding});
        $('.modal-body input[name=css_padding]').attr('value', padding);
        $('.modal-body input[name=css_padding]').on('keyup', function(){
            $('.note-editable').css({'padding': $(this).val()});
        });

        // Margin
        $('.modal-body input[name=css_margin]').attr('value', margin)
        $('.modal-body input[name=css_margin]').on('keyup', function(){
            var newPositions = window['utils']['get_position_dict_from_margin']($(this).val());
            $('.note-editable-wrapper').css(newPositions);
        });

        // Background
        $('.modal-body input[name=css_background]').parent().colorpicker({'color': background});
        $('.modal-body input[name=css_background]').on('keyup change', function(){
            $('.note-editable-wrapper').css({'background': $(this).val()})
        });

        // Border
        $('.modal-body input[name=css_border]').attr('value', border);
        $('.modal-body input[name=css_border]').on('keyup', function(){
            $('.note-editable-wrapper').css({'border': $(this).val()})
        });

        // Border Radius
        $('.modal-body input[name=css_border_radius]').attr('value', borderRadius);
        $('.modal-body input[name=css_border_radius]').on('change', function(){
            $('.note-editable-wrapper').css({'border-radius': $(this).val()})
        });

        // Border
        $('.modal-body input[name=css_shadow]').attr('value', shadow);
        $('.modal-body input[name=css_shadow]').on('change', function(){
            $('.note-editable').css({'box-shadow': $(this).val()})
        });

        // TODO: Bind ajax form

        return
    }
    if(cellObj['cellType'] == 'IMAGE') {
        // Initialize modal
        $('#insert-cell-modal .modal-dialog').addClass('modal-lg');
        var modalHtml =
            '<div class="modal-header">' +
                '<h5 class="modal-title"><i class="fa fa-camera"></i> New Image cell</h5>' +
                '<button type="button" class="close" data-dismiss="modal" aria-label="Close">' +
                    '<span aria-hidden="true">&times;</span>' +
                '</button>' +
            '</div>' +
            '<div class="modal-body">' +
                '<h5>Select image</h5>' +
                '<ul class="nav nav-tabs" id="myTab" role="tablist">'+
                    '<li class="nav-item">'+
                        '<a class="nav-link active" data-toggle="tab" href="#insert-image-gallery" role="tab" aria-controls="home" aria-selected="true"><i class="fa fa-picture-o"></i>  My Gallery</a>'+
                    '</li>'+
                    '<li class="nav-item">'+
                        '<a class="nav-link" data-toggle="tab" href="#insert-image-unsplash" role="tab"><i class="fa fa-camera-retro"></i> Unsplash</a>'+
                    '</li>'+
                    '<li class="nav-item">'+
                        '<a class="nav-link" data-toggle="tab" href="#insert-image-google" role="tab"><i class="fa fa-google"></i> Google search</a>'+
                    '</li>'+
                '</ul>'+
                '<div class="tab-content" id="myTabContent">'+
                    '<div class="insert-image-modal-tab-pane tab-pane fade show active" id="insert-image-gallery"  role="tabpanel">My Gallery</div>'+
                    '<div class="insert-image-modal-tab-pane tab-pane fade"             id="insert-image-unsplash" role="tabpanel">Unsplash</div>'+
                    '<div class="insert-image-modal-tab-pane tab-pane fade"             id="insert-image-google"   role="tabpanel">Google</div>'+
                '</div>'+
            '</div>' +
            '<div class="modal-footer">' +
                '<button type="button" class="btn btn-link text-danger" data-dismiss="modal">Cancel</button>' +
                '<button type="submit" class="btn btn-success" id="modal-btn"><i class="fa fa-plus-circle"></i> Create image cell</button>' +
            '</div>';
        $('#insert-cell-modal .modal-content').html(modalHtml);
        $.get('/sites/' + subdomain + '/images', function( data ) {
            $('#insert-image-gallery').html( data );
        });

        $('#insert-cell-modal').modal('show');

    }
}

function onEditSectionModalRequest(sectionAttr) {
    var $createModal = $($('#create-section-modal').html());
    console.log(sectionAttr)
    $createModal.find('.modal-title').text('Edit section')
    $createModal.find('form').attr('action', '/sections/' + sectionAttr['id'] + '/update');;
    $createModal.find('input[name=name]').attr('value', sectionAttr['name']);
    $createModal.find('input[name=html_id]').attr('value', sectionAttr['htmlId']);
    $createModal.find('input[name=section_n_rows]').attr('value', sectionAttr['nRows']);
    $createModal.find('input[name=section_n_cols]').attr('value', sectionAttr['nCols']);
    $createModal.find('input[name=section_background]').attr('value', sectionAttr['cssBackground']);
    $createModal.find('input[name=section_padding_top]').attr('value', sectionAttr['cssPaddingTop']);
    $createModal.find('input[name=section_padding_bottom]').attr('value', sectionAttr['cssPaddingBottom']);
    $createModal.find('.btn-success').text('Save changes');

    $('#edit-section-modal').html($createModal);
    $('<form id="delete-section-form" method="POST" action="/sections/' + sectionAttr['id'] + '/delete"><button type="submit" class="btn btn-link text-danger mr-auto"><i class="fa fa-times"></i> Delete</button></form>').insertBefore('#edit-section-modal .btn-success');
    $('#edit-section-modal').modal('show');

    $('#edit-section-modal').find('input[name=section_background]').colorpicker();

    bindFormEventsWithSelector('.modal.show form')
}


EventBus.subscribe(CELL_MODAL_REQUEST, onCellModalRequest);
EventBus.subscribe(SECTION_EDIT_MODAL_REQUEST, onEditSectionModalRequest);
