import re

from django.conf import settings
from django.urls import reverse

margin_pattern = '^([\d]*)(px|%|em|)$'


def resolve_url(name, args=None, private_domain=None):
    schema = 'https' if settings.SECURE_SCHEMA else 'http'
    domain = private_domain if private_domain else settings.DEFAULT_SITE_DOMAIN
    if args is None:
        args = []
    path = reverse(name, args=args)
    return '{schema}://{domain}{path}'\
        .format(schema=schema, domain=domain, path=path)


def get_position_dict_from_margin(margin: str) -> dict:
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


def get_position_string_from_position(position: dict) -> str:
    return 'top: {top}px; right: {right}px; ' \
           'bottom: {bottom}px; left: {left}px;'.format(**position)


def get_margin_string_from_position(position: dict) -> str:
    top = position['top']
    right = position['right']
    bottom = position['bottom']
    left = position['left']

    top_and_bottom_equal = top == bottom
    left_and_right_equal = left == right

    if top_and_bottom_equal:
        if left_and_right_equal:
            if top == left:
                tmpl = '{top}px'
            else:
                tmpl = '{top}px {left}px'
        else:
            tmpl = '{top}px {right}px {bottom}px {left}px'
    else:
        if left_and_right_equal:
            tmpl = '{top}px {left}px {bottom}px'
        else:
            tmpl = '{top}px {right}px {bottom}px {left}px'
    return tmpl.format(**position)


def clean_path(input_str: str) -> str:
    if input_str is None:
        input_str = ''
    parts = input_str.split('/')
    cleaned_parts = [part for part in parts if part]
    return '/%s' % '/'.join(cleaned_parts)
