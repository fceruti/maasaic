var fontSizes = [
    '8',
    '10',
    '12',
    '14',
    '16',
    '18',
    '20',
    '22',
    '24',
    '26',
    '28',
    '30',
    '32',
    '34',
    '36',
    '38',
    '40',
    '42'
];

(function ($) {
    'use strict';
    // jshint camelcase:true

    // Add dropdown with font sizes
    $.extend(true, $.trumbowyg, {
        plugins: {
            fontsize: {
                init: function (trumbowyg) {
                    trumbowyg.addBtnDef('fontsize', {
                        dropdown: buildDropdown(trumbowyg)
                    });
                }
            }
        }
    });
    function buildDropdown(trumbowyg) {
        var dropdown = [];

        $.each(fontSizes, function(index, size) {
            trumbowyg.addBtnDef('fontsize_' + size, {
                text: '<span style="font-size: ' + size + 'px;">' + size + 'px</span>',
                hasIcon: false,
                fn: function(){
                    trumbowyg.execCmd('fontSize', index+1, true);
                }
            });
            dropdown.push('fontsize_' + size);
        });

        return dropdown;
    }
})(jQuery);
