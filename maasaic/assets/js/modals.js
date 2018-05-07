var currentImage = null;
var currentCellProperties = null;
var currentCellObj = null;
var currentMargin = null;
var currentPadding = null;
var croppie = null;

function initializeCroppie(params) {
    var margin = window['utils']['get_position_dict_from_margin'](currentMargin);
    var padding = window['utils']['get_position_dict_from_margin'](currentPadding);

    $('#image-preview').croppie('destroy');
    $('#image-preview').croppie({
        viewport: {
            width: (currentCellProperties['colWidth'] * currentCellObj['w']) - (margin.left + margin.right + padding.left + padding.right),
            height: (currentCellProperties['rowHeight'] * currentCellObj['h']) - (margin.top + margin.bottom + padding.top + padding.bottom)
        },
        showZoomer: true,
        update: function(data) {
            $('.image-cell-preview-container input[name=image_cropping]').val(JSON.stringify(data));
        }
    });
    var croppieArgs = {url: currentImage.src};
    if (params!=null){
        croppieArgs['points'] = params['points'],
        croppieArgs['zoom'] = params['zoom'];
    }

    $('#image-preview').croppie('bind', croppieArgs);

}

function setCurrentImage(id, originalSrc, cropping, imageType) {
    currentImage = {
        id: id,
        src: originalSrc,
        cropping: cropping
    }

    $('.image-cell-preview-container input[name=image_id]').val(currentImage.id);
    $('.image-cell-preview-container input[name=image_type]').val(imageType);
    $('.image-cell-preview-container input[name=image_src]').val(currentImage.src);

    initializeCroppie(cropping);
}


function refreshImageGallery() {

    $.get('/sites/' + subdomain + '/images', function( data ) {

        $('#cell-modal .choose-image-form-container').html( data );

        // File selected
        $('#upload-image-form input[name=image]').on('change', function() {
            $form = $(this).closest('form');
            var data = new FormData($form[0]);
            var url = $form.attr('action');
            EventBus.fire(WAITING_SERVER_RESPONSE_STARTED);

            $.ajax({
                type: "POST",
                url: url,
                data: data,
                contentType: 'multipart/form-data',
                headers: {'X-CSRFToken': csrfmiddlewaretoken},
                cache: false,
                contentType: false,
                processData: false,
                success: function(response) {
                    refreshImageGallery();
                },
                complete: function() {
                    EventBus.fire(WAITING_SERVER_RESPONSE_ENDED);
                }
            });
        });

        // Image chosen
        $('input[name=image_file]').on('change', function(){
            setCurrentImage($(this).data('image-id'), $(this).data('original-src'), null, 'file');
        });
    });
}

function onCellModalRequest(cellProperties, cellObj) {
    currentCellObj = cellObj;
    currentCellProperties = cellProperties;

    var cellWidth = cellProperties['colWidth'] * cellObj['w'],
        cellHeight = cellProperties['rowHeight'] * cellObj['h'],
        initialPadding = cellProperties['padding'],
        initialMargin = cellProperties['margin'],
        initialBackground = cellProperties['background'],
        initialBorder = cellProperties['border'],
        initialBorderRadius = cellProperties['borderRadius'],
        initialShadow = cellProperties['shadow'],
        sectionBackground = cellProperties['sectionBackground'];

    // Initial values
    var background = initialBackground;
    if(cellObj.hasOwnProperty('css') && cellObj['css'].hasOwnProperty('background')){
        background = cellObj['css']['background'];
    }
    var padding = initialPadding;
    if(cellObj.hasOwnProperty('css') && cellObj['css'].hasOwnProperty('padding')){
        padding = cellObj['css']['padding'];
    } else {
        if(cellObj['cellType'] == 'IMAGE') {
            padding = '0';
        }
    }
    currentPadding = padding;
    var margin = initialMargin;
    if(cellObj.hasOwnProperty('css') && cellObj['css'].hasOwnProperty('margin')){
        margin = cellObj['css']['margin'];
    }
    currentMargin = margin;
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

    // Create template
    var $cellModalTmpl = $($('#cell-modal-tmpl').html());

    // Form url
    var formUrl, submitText;
    if (cellObj['id'] == null) {
        formUrl = '/cells/create';
        submitText = 'Create cell';
    } else {
        formUrl = '/cells/' + cellObj['id'] + '/update';
        submitText = 'Update cell';
    }

    // Populate form
    $cellModalTmpl.find('form').attr('action', formUrl);
    $cellModalTmpl.find('.modal-header .modal-title').html(submitText);
    $cellModalTmpl.find('.modal-footer .btn-success').html(submitText);
    $cellModalTmpl.find('input[name=x]').attr('value', cellObj['x']);
    $cellModalTmpl.find('input[name=y]').attr('value', cellObj['y']);
    $cellModalTmpl.find('input[name=w]').attr('value', cellObj['w']);
    $cellModalTmpl.find('input[name=h]').attr('value', cellObj['h']);
    $cellModalTmpl.find('input[name=cell_type]').attr('value', cellObj['cellType']);
    $cellModalTmpl.find('input[name=section]').attr('value', cellObj['sectionId']);
    $cellModalTmpl.find('input[name=id]').attr('value', cellObj['id']);

    if (cellObj['id'] == null) {
        formUrl = '/cells/create';
        submitText = 'Create cell';
    } else {
        formUrl = '/cells/' + cellObj['id'] + '/update';
        submitText = 'Update cell';
    }

    if(cellObj['cellType'] == 'TEXT') {

        // Add summernote
        $cellModalTmpl.find('.edit-content-panel').html('<h5>Content</h5><div id="summernote"></div>');

        // Build modal
        $('#cell-modal .modal-content').html($cellModalTmpl.html());
        $('#cell-modal').modal('show');

        function onSummernoteChange() {
            $('#cell-modal textarea[name=content]').val($('.note-editable').html());
        }
        $('#cell-modal #summernote').summernote({
            dialogsInBody: true,
            height: cellHeight,
            toolbar: [
                ['style', ['bold', 'italic', 'underline', 'clear']],
                ['font', ['strikethrough', 'superscript', 'subscript']],
                ['fontsize', ['fontname', 'fontsize']],
                ['color', ['color']],
                ['para', ['ul', 'ol', 'paragraph', 'link']],
                ['height', ['height']],
            ],
            fontNames: fontNames,
            fontNamesIgnoreCheck: googleFonts,
            lineHeights: ['0.5', '0.8', '1.0', '1.2', '1.4', '1.5', '1.6', '1.8', '2.0', '3.0'],
            fontSizes: ['8', '10', '12', '13', '14', '16', '18', '20', '24', '30', '32', '36', '42', '56', '64', '72', '92'],
            callbacks: {
                onChange: onSummernoteChange,
                onPaste: onSummernoteChange
            }
        });

        // Modify summernote style
        $('#cell-modal .note-editing-area').css({
            'height': cellHeight + 'px',
            'width': cellWidth + 'px',
            'margin': '20px auto',
            'border': '1px solid rgba(0, 40, 100, 0.12)'});
        $('#cell-modal .note-statusbar').css({'display': 'none'});
        $('#cell-modal .note-editor').css({'background': sectionBackground});

        $('#cell-modal .note-editable').addClass('editing-cell-inner');

        // Insert content
        if(cellObj['content'] != null && cellObj['content'] != undefined) {
            $('#cell-modal #summernote').summernote('code', cellObj['content']);
            $('#cell-modal textarea[name=content]').val(cellObj['content']);
        }
    }
    if(cellObj['cellType'] == 'IMAGE') {
        // Build modal
        $('#cell-modal .modal-content').html($cellModalTmpl.html());
        $('#cell-modal').modal('show');
        refreshImageGallery();

        var html = '<h5>Preview</h5>' +
            '<div class="image-cell-preview-container">' +
            '<div class="image-cell-preview">' +
            '<div class="editing-cell-inner">' +
            '<div id="image-preview"></div></div></div>' +
            '<input type="hidden" name="image_id" />' +
            '<input type="hidden" name="image_src" />' +
            '<input type="hidden" name="image_type" />' +
            '<input type="hidden" name="image_cropping" /></div>';

        $('#cell-modal .edit-content-panel').html(html);

        $('#cell-modal .image-cell-preview-container').css({
            'background': sectionBackground,
            'padding': '40px 0'
        });

        $('#cell-modal .image-cell-preview').css({
            'height': cellHeight + 'px',
            'width': cellWidth + 'px',
            'position': 'relative',
            'margin': '0 auto',
            'border': '1px solid rgba(0, 40, 100, 0.12)'
        });

        if(cellObj['imageId'] != null && cellObj['imageId'] != undefined &&
           cellObj['imageCropping'] != null && cellObj['imageCropping'] != undefined &&
           cellObj['imageOriginalSrc'] != null && cellObj['imageOriginalSrc'] != undefined){
            setCurrentImage(cellObj['imageId'], cellObj['imageOriginalSrc'], JSON.parse(cellObj['imageCropping'].replace(/'/g, '"')), 'file');
        }

    }

    $noteWrapper = $('<div></div>')
    $noteWrapper.addClass('editing-cell-outer');
    var noteWrapperStyle = window['utils']['get_position_dict_from_margin'](margin);
    noteWrapperStyle['position'] = 'absolute';
    noteWrapperStyle['background'] = background;
    noteWrapperStyle['shadow'] = shadow;
    noteWrapperStyle['border'] = border;
    noteWrapperStyle['borderRadius'] = borderRadius;
    noteWrapperStyle['box-sizing'] = 'content-box';
    $noteWrapper.css(noteWrapperStyle);

    $('#cell-modal .editing-cell-inner').wrap($noteWrapper);
    $('#cell-modal .editing-cell-inner').css({'height': '100%'});

    /*
    *  Sidebar item binding
    */

    // Padding
    $('#cell-modal .editing-cell-inner').css({'padding': padding});
    $('#cell-modal input[name=css_padding]').attr('value', padding);
    $('#cell-modal input[name=css_padding]').on('keyup', function(){
        var newPadding = $(this).val();
        $('#cell-modal .editing-cell-inner').css({'padding': newPadding});
        currentPadding = newPadding;
        initializeCroppie();
    });

    // Margin
    $('#cell-modal input[name=css_margin]').attr('value', margin)
    $('#cell-modal input[name=css_margin]').on('keyup', function(){
        var newMargin = $(this).val();
        var newPositions = window['utils']['get_position_dict_from_margin'](newMargin);
        $('#cell-modal .editing-cell-outer').css(newPositions);
        currentMargin = newMargin;
        initializeCroppie();
    });

    // Background
    $('#cell-modal input[name=css_background]').parent().colorpicker({'color': background});
    $('#cell-modal input[name=css_background]').on('keyup change', function(){
        $('#cell-modal .editing-cell-outer').css({'background': $(this).val()})
    });

    // Border
    $('#cell-modal input[name=css_border]').attr('value', border);
    $('#cell-modal input[name=css_border]').on('keyup', function(){
        $('#cell-modal .editing-cell-outer').css({'border': $(this).val()})
    });

    // Border Radius
    $('#cell-modal input[name=css_border_radius]').attr('value', borderRadius);
    $('#cell-modal input[name=css_border_radius]').on('change', function(){
        $('#cell-modal .editing-cell-outer').css({'border-radius': $(this).val()})
    });

    // Border
    $('#cell-modal input[name=css_shadow]').attr('value', shadow);
    $('#cell-modal input[name=css_shadow]').on('change', function(){
        $('#cell-modal .editing-cell-inner').css({'box-shadow': $(this).val()})
    });

    bindFormEventsWithSelector('#cell-modal form')

}

function onEditSectionModalRequest(sectionAttr) {
    var $createModal = $($('#create-section-modal').html());
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
