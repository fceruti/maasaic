	(function () {
		var re = {};
		var __name__ = '__main__';
		__nest__ (re, '', __init__ (__world__.re));
		var margin_pattern = '^([\\d]*)(px|%|em|)$';
		var get_position_dict_from_margin = function (margin) {
			var margin_split = margin.py_split (' ');
			var margin_parts = list ([]);
			var __iterable0__ = margin_split;
			for (var __index0__ = 0; __index0__ < len (__iterable0__); __index0__++) {
				var part = __iterable0__ [__index0__];
				if (part) {
					try {
						var match = re.match (margin_pattern, part);
						if (match) {
							margin_parts.append (int (match.group (1)));
							continue;
						}
					}
					catch (__except0__) {
						if (isinstance (__except0__, tuple ([AttributeError, py_TypeError]))) {
							// pass;
						}
						else {
							throw __except0__;
						}
					}
					var margin_parts = list ([]);
					break;
				}
			}
			if (len (margin_parts) == 4) {
				var top = margin_parts [0];
				var right = margin_parts [1];
				var bottom = margin_parts [2];
				var left = margin_parts [3];
			}
			else if (len (margin_parts) == 3) {
				var top = margin_parts [0];
				var right = margin_parts [1];
				var bottom = margin_parts [2];
				var left = margin_parts [1];
			}
			else if (len (margin_parts) == 2) {
				var top = margin_parts [0];
				var right = margin_parts [1];
				var left = margin_parts [1];
				var bottom = margin_parts [0];
			}
			else if (len (margin_parts) == 1) {
				var top = margin_parts [0];
				var right = margin_parts [0];
				var left = margin_parts [0];
				var bottom = margin_parts [0];
			}
			else {
				var __left0__ = tuple ([0, 0, 0, 0]);
				var top = __left0__ [0];
				var right = __left0__ [1];
				var bottom = __left0__ [2];
				var left = __left0__ [3];
			}
			return dict ({'top': top, 'right': right, 'bottom': bottom, 'left': left});
		};
		var get_position_string_from_dict = function (margin) {
			return 'top: {top}px; right: {right}px; bottom: {bottom}px; left: {left}px;'.format (__kwargtrans__ (margin));
		};
		__pragma__ ('<use>' +
			're' +
		'</use>')
		__pragma__ ('<all>')
			__all__.__name__ = __name__;
			__all__.get_position_dict_from_margin = get_position_dict_from_margin;
			__all__.get_position_string_from_dict = get_position_string_from_dict;
			__all__.margin_pattern = margin_pattern;
		__pragma__ ('</all>')
	}) ();
