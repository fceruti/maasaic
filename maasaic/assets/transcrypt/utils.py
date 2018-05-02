import re
margin_pattern = '^([\d]*)(px|%|em|)$'


def get_position_dict_from_margin(margin):
    margin_split = margin.split(' ')

    margin_parts = []
    for part in margin_split:
        if part:
            try:
                match = re.match(margin_pattern, part)
                if match:
                    margin_parts.append(int(match.group(1)))
                    continue
            except (AttributeError, TypeError):
                pass

            margin_parts = []
            break

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
        top, right, bottom, left = 0, 0, 0, 0

    return {'top': top,
            'right': right,
            'bottom': bottom,
            'left': left}

def get_position_string_from_dict(margin):
    return 'top: {top}px; right: {right}px; ' \
           'bottom: {bottom}px; left: {left}px;'.format(**margin)
