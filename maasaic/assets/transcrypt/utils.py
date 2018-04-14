import re
margin_pattern = '^[+-]?[0-9]+.?([0-9]+)?(px)$'


def get_position_dict_from_margin(margin):
    margin_parts = margin.split(' ')
    margin_parts = [part for part in margin_parts
                    if re.match(margin_pattern, part)]
    if len(margin_parts) == 4:
        top = margin_parts[0]
        right = margin_parts[1]
        bottom = margin_parts[2]
        left = margin_parts[3]
    elif len(margin_parts) == 3:
        top = margin_parts[0]
        right = margin_parts[1]
        bottom = margin_parts[2]
        left = margin_parts[1]
    elif len(margin_parts) == 2:
        top = margin_parts[0]
        right = margin_parts[1]
        left = margin_parts[1]
        bottom = margin_parts[0]
    elif len(margin_parts) == 1:
        top = margin_parts[0]
        right = margin_parts[0]
        left = margin_parts[0]
        bottom = margin_parts[0]
    else:
        top, right, bottom, left = '0', '0', '0', '0'
    return {'top': int(top.replace('px', '')),
            'right': int(right.replace('px', '')),
            'bottom': int(bottom.replace('px', '')),
            'left': int(left.replace('px', ''))}


def get_position_string_from_dict(margin):
    return 'top: {top}px; right: {right}px; ' \
           'bottom: {bottom}px; left: {left}px;'.format(**margin)
