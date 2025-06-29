# Install FontForge
# Add FontForge bin directory to path.
# Run: fontforge -script svg2webfont.py

import fontforge
import argparse
import sys
import os
import xml.etree.ElementTree as ET
import json

class Rect:
    def __init__(self,
                 x1:float,
                 y1:float,
                 x2:float = None,
                 y2: float = None,
                 width:float = None,
                 height: float = None):
        
        if x2 is None:
            if width is None:
                raise Exception("Neither width nor x2 passed to Rect")
            x2 = x1 + width
        if y2 is None:
            if height is None:
                raise Exception("Neither height nor y2 passed to Rect")
            y2 = y1 + height

        self.min_x = min(x1, x2)
        self.min_y = min(y1, y2)
        self.max_x = max(x1, x2)
        self.max_y = max(y1, y2)

    @staticmethod
    def from_rect(rect):
        return Rect(
            x1=rect.min_x,
            y1=rect.min_y,
            x2=rect.max_x,
            y2=rect.max_y)
            
    @property
    def width(self):
        return self.max_x - self.min_x

    @property
    def height(self):
        return self.max_y - self.min_y

    def transform(self, matrix):
        new_xywh = transform(matrix, [self.min_x, self.min_y, self.width, self.height])
        return Rect(x1=new_xywh[0], y1=new_xywh[1], width=new_xywh[2], height=new_xywh[3])

    def move_to(self, x: float, y: float):
        self.min_x = x
        self.min_y = y
                
    def __repr__(self):
        return f"Rect(min_x={self.min_x}, min_y={self.min_y}, max_x={self.max_x}, max_y={self.max_y}, width={self.width}, height={self.height})"

def assert_dst_file_path(filepath:str, param:str):
    
    (path, file) = os.path.split(filepath)
    
    if file == '':
        print('%s does not point to a file' % (param,))
        sys.exit(-1)
    
    if path != '' and not os.path.isdir(path):
        print('directory %s of %s does not exist or is not a valid directory' % (path, param,))
        sys.exit(-1)

def get_arg_or_config(glyph_name, param: str):
    global args, config

    if glyph_name in config and param in config[glyph_name]:
        return  config[glyph_name][param]
    return vars(args)[param]

def get_int_arg_or_config(glyph_name, param: str):
    global args, config

    if config != None:
        if glyph_name in config and param in config[glyph_name] and config[glyph_name][param] != '':
            return parse_int_param(param, config[glyph_name][param])
    return parse_int_param(param, vars(args)[param])

def get_float_arg_or_config(glyph_name, param: str):
    global args, config

    if config != None:
        if glyph_name in config and param in config[glyph_name] and config[glyph_name][param] != '':
            return parse_float_param(param, config[glyph_name][param])
    return parse_float_param(param, vars(args)[param])


def parse_int_param(param, s:str|int):
    try:
        return int(s)
    except ValueError:
        print('bad %s value: %s' % (param, s))
        sys.exit(-1)

def parse_float_param(param, s:str|float|int):
    try:
        return float(s)
    except ValueError:
        print('bad %s value: %s' % (param, s))
        sys.exit(-1)

def get_rel_path(from_file:str, to_file:str, to_url:bool):
    
    (from_path, _) = os.path.split(from_file)
    (to_path, to_filename) = os.path.split(to_file)
    
    path = os.path.relpath(os.path.abspath(to_path), os.path.abspath(from_path))
    
    if to_url:
        return join_url_path(path.replace('\\', '/'), to_filename)
    
    return os.path.join(path, to_filename)

def join_url_path(path:str, file:str):
    
    if path == '':
        return file
    
    if path.endswith('/'):
        return path + file
    
    return path + '/' + file

def esc_html_dq_str(s:str):
    return s.replace('"', '\\"')

def format_font_file_src_css(font_file_fs_path:str, css_fs_path:str, override_url_path:str, font_file_param:str, require_font_file_ext:str, css_format:str):
    
    if not font_file_fs_path.endswith(require_font_file_ext):
        print('%s file name must end with .%s extension' % (font_file_param, require_font_file_ext))
        sys.exit(-1)
    
    if override_url_path != '':
        (_, filename) = os.path.split(font_file_fs_path)
        url = join_url_path(override_url_path, filename)
    else:
        url = get_rel_path(css_fs_path, font_file_fs_path, True)
    
    return 'url("%s") format("%s")' % (esc_html_dq_str(url), esc_html_dq_str(css_format))

def get_svg_viewbox(path):
    #SVG viewbox has the origin on top left with positive values going right and down
    tree = ET.parse(path)
    root = tree.getroot()
    if 'viewBox' in root.attrib:
        parts = root.attrib['viewBox'].split()
        if len(parts) == 4:
            return Rect(x1=float(parts[0]), y1=float(parts[1]), width=float(parts[2]), height=float(parts[3]))
    if 'width' in root.attrib and 'height' in root.attrib:
        return Rect(x1=0.0, y1=0.0, width=float(root.attrib['width']), height=float(root.attrib['height']))
    return None

def get_glyph_bbox_rect(glyph):
    rect = glyph.boundingBox() # xmin,ymin, xmax,ymax from baseline to ascender
    return Rect(x1=rect[0], y1=rect[1], x2=rect[2], y2=rect[3])

def transformXY(matrix, xy):
    a, b, c, d, e, f = matrix
    x, y = xy

    x1 = a*x + c*y + e
    y1 = b*x + d*y + f
    return (x1, y1)

def transform(matrix, xywh):
    x1, y1 = transformXY(matrix, (xywh[0], xywh[1]))
    x2, y2 = transformXY(matrix, (xywh[0] + xywh[2], xywh[1] + xywh[3]))
    return (x1, y1, x2 - x1, y2 - y1)

def is_glyph_empty(glyph): 
    return not glyph.isWorthOutputting()

def print_debug(info:str, char_name:str = None):
    global args
    if args.debug:
        if char_name != None:
            print('%s: %s' % (char_name, info))
        else:
            print(info)

# Parse input arguments
parser = argparse.ArgumentParser(
    
)

parser.add_argument(
    '-m', '--mode',
    choices=['class', 'ligature', 'both'],
    default='ligature',
    help=("How icons will be referenced in HTML/CSS: 'class' - generate .ico-NAME classes with \\EAXX escapes (legacy), 'ligature' - add GSUB 'liga' table so typing the icon name shows the glyph (default), or 'both'"))

parser.add_argument('-st', '--start', help='Unicode index in hexadecimal form to start from, default: \'EA01\'', default='EA01', type=str)
parser.add_argument('-src', '--srcdir', help='path to the directory with SVG files, default: \'./src/\'', default='./src/', type=str)
parser.add_argument('-ff', '--fontfamily', help='CSS font family name, default: \'Icon Font\'', default='Icon Font', type=str)
parser.add_argument('-gc', '--gencssclass', help='name for the generic CSS class shared by all element instances, default: \'ico\'', default='ico', type=str)
parser.add_argument('-pr', '--cssclassprefix', help='prefix for the individual font CSS classes, default: \'ico-\'', default='ico-', type=str)
parser.add_argument('-csc', '--cssfile', help='path to the generated CSS file, default: \'./dist/css/font.css\'', default='./dist/css/font.css', type=str)
parser.add_argument('-w1', '--woff1file', help='name of the WOFF v1 file, must have \'.woff\' extension, default: \'./dist/fonts/font.woff\'', default='./dist/fonts/font.woff', type=str)
parser.add_argument('-w2', '--woff2file', help='name of the WOFF v2 file, must have \'.woff2\' extension, default: \'./dist/fonts/font.woff2\'', default='./dist/fonts/font.woff2', type=str)
parser.add_argument('-htm', '--htmlfile', help='path to an HTML preview file listing all characters, default: \'./dist/preview.html\'', default='./dist/preview.html', type=str)
parser.add_argument('-fs', '--previewfontsize', help='default font size for HTML preview file, default: \'24px\'', default='24px', type=str)
parser.add_argument('-cfp', '--css2fontpath', help='override relative path from CSS file to the font files; if empty then will be calculated based on output file paths; pass \'./\' to override to same directory', default='', type=str)

parser.add_argument('-upm', '--upmsize', help='units per em, default 1000', default=1000, type=int)
parser.add_argument('-asc', '--ascent', help='ascent size (distance from baseline to top), default 800', default=800, type=int)
parser.add_argument('-des', '--descent', help='descent size (distance from baseline to bottom), default 200', default=200, type=int)

parser.add_argument('-sc', '--scale', help="how to scale the SVG view-box, can be 'in_em', 'over_em', 'in_ascent', 'over_ascent', 'no' or a float scale factor number, default: 'in_em'", default='in_em', type=str)
parser.add_argument('-ha', '--halign', help="how to align the scaled SVG view-box relative to advance width horizontally, can be 'center','left','right' or a number interpreted as a center in font units, default: 'center'", default='center', type=str)
parser.add_argument('-va', '--valign', help="how to align the scaled SVG view-box vertically, can be 'ascent_center', 'ascdesc_center','baseline','descent' or a number interpreted as a center in font units, default: 'ascdesc_center'", default='ascdesc_center', type=str)
parser.add_argument('-x', '--xmove', help='by how many units to move the scaled and aligned SVG view-box horizontally, default: 0', default=0, type=int)
parser.add_argument('-y', '--ymove', help='by how many units to move the scaled and aligned SVG view-box vertically, default: 0', default=0, type=int)

parser.add_argument('-min', '--minwidth', help="minimal advance width (how much space the font uses horizontally) in font units, besides a number can be 'auto' to match the outline (drawing) width or 'em', default 'em'", default='em', type=str)
parser.add_argument('-max', '--maxwidth', help="maximal advance width (how much space the font uses horizontally) in font units, besides a number can be 'auto' to match the outline (drawing) width or 'em', default 'auto'", default='auto', type=str)
parser.add_argument('-sw', '--separation', help='separation width in font units between characters, default 0', default=0, type=int)

parser.add_argument('-cf', '--configfile', help='path to a JSON configuration file for overriding parameter values for individual glyphs', type=str, default="")
parser.add_argument('-c', '--config', help='JSON configuration text for overriding parameter values for individual glyphs', type=str, default="")

parser.add_argument('-d', '--debug', help='print additional information (e.g. size of each character in font units) helpful for debugging and tuning the font', action='store_true')
args = parser.parse_args()

if args.start == '':
    print('-st or --start is required')
    sys.exit(-1)

if args.config != "" and args.configfile != "":
    print('it is not allowed to specify both configfile and config')
    sys.exit(-1)
elif args.config != "":
    print(args.config)
    config = json.loads(args.config)
elif args.configfile != "":
    with open(args.configfile, "r") as file:
        config = json.load(file)
else:
    config = {}

# Ensure all directories exist
if not os.path.exists(args.srcdir):
    print('svg file directory %s does not exist', args.srcdir)
    sys.exit(-1)

if args.cssfile != '':
    assert_dst_file_path(args.cssfile, 'cssfile')

if args.woff1file != '':
    assert_dst_file_path(args.woff1file, 'woff1file')

if args.woff2file != '':
    assert_dst_file_path(args.woff2file, 'woff2file')

if args.htmlfile != '':
    assert_dst_file_path(args.htmlfile, 'htmlfile')

# Format font-face src property value
if args.cssfile != '':

    if args.fontfamily == '':
        print('-ff or --fontfamily is required')
        sys.exit(-1)

    if args.gencssclass == '':
        print('-gc or --gencssclass is required')
        sys.exit(-1)

    if args.cssclassprefix == '':
        print('-pr or --cssclassprefix is required')
        sys.exit(-1)

    src = []
    
    if args.woff2file != '':
        src.append(format_font_file_src_css(args.woff2file, args.cssfile, args.css2fontpath, 'woff2file', 'woff2', 'woff2'))

    if args.woff1file != '':
        src.append(format_font_file_src_css(args.woff1file, args.cssfile, args.css2fontpath, 'woff1file', 'woff', 'woff'))

    if len(src) == 0:
        sys.exit('woff 2.0 or woff file name must be specified')

    fontfamily = esc_html_dq_str(args.fontfamily)
    
    ligature_css_rule = ""
    if args.mode in ('ligature', 'both'):
        ligature_css_rule='\nfont-variant-ligatures: common-ligatures;'

   # Store css rules in a string array
    css = ['''
@font-face {
	font-family: '%s';
	src: %s;
}

.%s {
	font-family: '%s';
	font-style: normal;
	text-rendering: auto;
	display: inline-block;
	font-variant: normal;
	-moz-osx-font-smoothing: grayscale;
	-webkit-font-smoothing: antialiased;%s
}
''' % (fontfamily, ',\n       '.join(src), args.gencssclass, fontfamily, ligature_css_rule)]

    if args.htmlfile != '':
        html = [\
'''<html>
    <head>
        <title>Font preview</title>
        <link href="%s" rel="stylesheet">
        <style>
            body {
                background-color: #f3f2f1;
                text-align: center;
                padding: 1rem;
                margin: 0;
            }
            #font-list {
                display: flex;
                flex-wrap: wrap;
                align-items: center;
                justify-content: center; 
                margin-top: 1rem;
                gap: 1rem;
            }
            #font-list > div {
                background-color: #fff;
                box-shadow: 0 1.6px 3.6px 0 rgba(0, 0, 0, 0.132), 0 0.3px 0.9px 0 rgba(0, 0, 0, 0.108);
                padding: 20px;
            }
            #font-list > div > span {
                display: inline-block;
                padding-top: 0.5rem;
                font-size: 1rem;
            }
        </style>
    </head>
    <body>
    Icon font size: <input type="text" id="font-size" value="%s" onchange="document.getElementById('font-list').style.fontSize=this.value">
    <div id="font-list" style="font-size: %s;">
''' % (esc_html_dq_str(get_rel_path(args.htmlfile, args.cssfile, True)),
        esc_html_dq_str(args.previewfontsize),
        esc_html_dq_str(args.previewfontsize))]
    else:
        html = None

else:
    css = None
    html = None

# Create a new font
font = fontforge.font()

font.em = args.upmsize 		# units (points) per 1 em
font.ascent = args.ascent 	# distance from baseline (where fonts are position) to top for tallest fonts
font.descent = args.descent # distance from baseline to bottom for fonts that go below baseline

print_debug('font.em=%s, font.ascent=%s, font.descent=%s,' % (font.em, font.ascent, font.descent))

# Set the starting Unicode value
next_unicode = int(args.start, 16)

# Initi used Unicode value dict
used_unicodes = {}
for glyph_name in config:
    if 'code' in config[glyph_name]:
        try:
            used_unicodes[int(config[glyph_name]['code'], 16)] = True
        except ValueError:
            print('bad character code %s specified for %s in configuration' % (config[glyph_name]['code'], glyph_name))
            sys.exit(-1)

# Get the list of SVG files in the directory
svg_dir = args.srcdir
if not svg_dir.endswith('/'):
    svg_dir += '/'
svg_files = os.listdir(svg_dir)
svg_files = [f for f in svg_files if f.endswith('.svg')]
svg_files.sort()

max_width = 0.0
max_height = 0.0

				   
svg_file_index = 0

# Iterate through the list of SVG files
for svg_file in svg_files:

    svg_file_index += 1

    glyph_name = svg_file[0:-len('.svg')]
    if len(glyph_name) == 0:
        continue

    if config != None and glyph_name in config and 'code' in config[glyph_name]:
        curr_unicode = int(config[glyph_name]['code'], 16)
    else:
        curr_unicode = next_unicode
        while curr_unicode in used_unicodes:
            curr_unicode += 1
        next_unicode = curr_unicode + 1

    # Create a glyph
    glyph = font.createChar(curr_unicode)

    svg_file_path = os.path.join(svg_dir, svg_file)

    # Import the svg
    # Some paths do not get scaled by importOutlines with scale=True, so use manual scaling below
    # (TODO: figure out why exactly - possibly if they lack viewBox)
    # The outline will get imported on top left corner right below the ascent
    try:
        glyph.importOutlines(svg_file_path, scale=False) 
    except Exception as e:
        print(f"Failed to import outlines from SVG file %s: {e}" % (svg_file_path,))
        continue
    
    if is_glyph_empty(glyph):
        print(f"Warning: The SVG file '{svg_file_path}' is either empty or FontForge failed to import outlines from it.")

    # Set name
    glyph.glyphname = glyph_name

    # Try to read the viewbox info from the SVG
    # SVG viewbox has the origin on top left with positive values going right and down
    svg_viewbox = get_svg_viewbox(svg_file_path)
    print_debug('svg viewbox read: %s' % (svg_viewbox,), glyph_name)

    # Get the bounding box in the glyph
    bbox = get_glyph_bbox_rect(glyph)
    print_debug('bbox before scale: %s' % (bbox,), glyph_name)

    # If viewbox could not be imported from the XML, use the bounding box
    if svg_viewbox == None:
        # glyph has vertical origin on the baseline with positive values above
        # going towards ascent and negative values below going towards -descent
        glyph_viewbox = Rect.from_rect(bbox)
    else:
        # If viewbox could be imported from the XML, calculate
        # it's position in Glyph coordinate system.

        # SVG has bottom right coordinate system with origin on top left;
        # Glyph has up right coordinate system with origin on baseline;
        # FontForge maps the origin of SVG to the top left corner of ascent (i.e. 0,800).

        # It appears though that at least version 20230101 does not
        # translate the positions if top left of the viewbox in the SVG is not 0, 0.
        # E.g. if the viewbox starts at 0, -960 and a dot is down in the middle
        # of the viewbox - 0,-460 - it will get imported at position 0, 1260
        # in glyph - way above the ascent.

        glyph_viewbox = Rect(
            x1=svg_viewbox.min_x,
            y1=float(font.ascent) - svg_viewbox.min_y, #-960 in SVG should become 800 + 960 in glyph
            width=svg_viewbox.width,
            height=-svg_viewbox.height
        )

    print_debug('viewbox in glyph: %s' % (glyph_viewbox,), glyph_name)

    # Some paths do not get scaled by importOutlines with scale=True
    # so scale manually to fit into em square

    # Set or calculate the scale

    # Use exact scaling factor if such is specified
    scale = get_arg_or_config(glyph_name, "scale")
    if scale == 'in_em': # touch 1x1 em (usually 1000x1000) from inside
        scale = float(font.em) / max(glyph_viewbox.width, glyph_viewbox.height)
    elif scale == 'over_em': # touch em from outside
        scale = float(font.em) / min(glyph_viewbox.width, glyph_viewbox.height)
    elif scale == 'in_ascent':
        scale = float(font.ascent) / max(glyph_viewbox.width, glyph_viewbox.height)
    elif scale == 'over_ascent':
        scale = float(font.ascent) / min(glyph_viewbox.width, glyph_viewbox.height)
    elif scale != 'no' and scale != '':
        scale = parse_float_param('scale', scale)
    else:
        scale = None

    if scale != None:
        # Generate PostScript transformation matrix for scaling
        matrix = (scale, 0, 0,
                scale, 0, 0)
        print_debug('scale matrix: %s' % (matrix,), glyph_name)

        # Apply scaling matrix to outlines
        glyph.transform(matrix)

        # Apply scaling matrix to viewBox
        glyph_viewbox = glyph_viewbox.transform(matrix)

        bbox = get_glyph_bbox_rect(glyph)

    print_debug('bbox after scale: %s' % (bbox,), glyph_name)
    print_debug('viewbox after scale: %s' % (glyph_viewbox,), glyph_name)

    # Calculate the advance width of the font (the space it takes, not the space it is drawn in)
    adv_min_width = get_arg_or_config(glyph_name, "minwidth")
    if adv_min_width == 'em':
        adv_min_width = font.em
    elif adv_min_width == 'auto':
        adv_min_width = None
    else:
        adv_min_width = parse_int_param("minwidth", adv_min_width)

    adv_max_width = get_arg_or_config(glyph_name, "maxwidth")
    if adv_max_width == 'em':
        adv_max_width = font.em
    elif adv_max_width == 'auto':
        adv_max_width = None
    else:
        adv_max_width = parse_int_param("maxwidth", adv_max_width)

    advance_width = bbox.width
    if adv_min_width != None and advance_width < adv_min_width:
        advance_width = adv_min_width
    
    if adv_max_width != None and advance_width > adv_max_width:
        advance_width = adv_max_width

    print_debug('advance_width=%s' % (advance_width,), glyph_name) 

    halign = get_arg_or_config(glyph_name, "halign")
    print_debug('halign: %s' % (halign,), glyph_name)

    if halign == 'center':
        # Move the center of the viewbox to be in the center of the advance_width horizontally
        x_move = (float(advance_width) - glyph_viewbox.width) / 2.0 - glyph_viewbox.min_x
    elif halign == 'right':
        x_move = float(advance_width) - glyph_viewbox.width
    elif halign == 'left':
        x_move = -glyph_viewbox.min_x
    elif halign != '':
        center = parse_int_param('halign', halign)
        x_move = -glyph_viewbox.min_x + center + glyph_viewbox.width / 2.0
    else:
        x_move = 0

    x_move += get_int_arg_or_config(glyph_name, "xmove")

    # Move the center of the viewbox to be in the center of the em vertically
    valign = get_arg_or_config(glyph_name, "valign")
    print_debug('valign: %s' % (valign,), glyph_name)

    if valign == 'ascdesc_center':
        center = (float(font.ascent) + float(font.descent)) / 2.0 - font.descent #e.g. origin = 0, ascent=800 above, descent=200 below
        y_move = -glyph_viewbox.max_y + center + glyph_viewbox.height / 2.0
    elif valign == 'ascent_center':
        center = float(font.ascent) / 2.0
        y_move = -glyph_viewbox.max_y + center + glyph_viewbox.height / 2.0
    elif valign == 'baseline':
        y_move = -glyph_viewbox.min_y
    elif valign == 'descent':
        y_move = -glyph_viewbox.min_y - float(font.descent)
    elif valign != '':
        center = parse_int_param('valign', valign)
        y_move = -glyph_viewbox.max_y + center + glyph_viewbox.height / 2.0 

    y_move += get_int_arg_or_config(glyph_name, "ymove")

    print_debug('x_move: %d, y_move: %d' % (x_move, y_move), glyph_name)

    matrix = (1, 0, 0,
              1, x_move, y_move)

    print_debug('move matrix: %s' % (matrix,), glyph_name)

    glyph.transform(matrix)

    # Set the new width after the transform because transform would transform also the width
    glyph.width = int(round(advance_width))

    bbox = get_glyph_bbox_rect(glyph)

    print_debug('bbox after move: %s' % (bbox,), glyph_name)
    
    if css != None:
    
        if args.mode in  ('class', 'both'):
            css.append(\
'''.%s%s::before {
  content: "\\%s";
  font-family: "%s";
}
''' % (esc_html_dq_str(args.cssclassprefix), esc_html_dq_str(glyph_name), hex(curr_unicode)[2:], esc_html_dq_str(fontfamily)))

        if html != None:
            if args.mode == 'class' or (args.mode == 'both' and svg_file_index % 2 == 1):
                html.append('<div><i class="%s %s%s"></i><br><span>%s</span></div>' % (
                    esc_html_dq_str(args.gencssclass), esc_html_dq_str(args.cssclassprefix), esc_html_dq_str(glyph_name), esc_html_dq_str(glyph_name)))
            else:
                html.append('<div><i class="%s">%s</i><br><span>%s</span></div>' % (
                    esc_html_dq_str(args.gencssclass), esc_html_dq_str(glyph_name), esc_html_dq_str(glyph_name)))

# Set the font's encoding to Unicode
font.encoding = 'unicode'

if args.debug:
    print('font.em: %s, font.ascent=%s, font.descent=%s,' % (font.em, font.ascent, font.descent))
    for glyph in font.glyphs():
        bbox = get_glyph_bbox_rect(glyph)
        print('%s, adv_width=%d, bbox=%s' % (glyph.glyphname, glyph.width, bbox))

# ------------------------------------------------------------------
# ADD LIGATURE SUPPORT
# ------------------------------------------------------------------

if args.mode in ('ligature', 'both'):
    # 1. Create zero-width glyphs for every character that appears
    safe_chars = "abcdefghijklmnopqrstuvwxyz0123456789_-"
    icon_chars = set("".join(g.glyphname for g in font.glyphs()))        # names of icons
    flat_chars = {ch for name in icon_chars for ch in name if ch in safe_chars}     # every letter/_/digit…
    dummy_blank_chars = set()

    for ch in flat_chars:
        cp = ord(ch)
        if cp not in font:
            blank = font.createChar(cp)
            blank.width = 0          # invisible placeholder
            dummy_blank_chars.add(ch)

    # 2. Build the lookup
    font.addLookup('Ligatures', 'gsub_ligature', (),
                (('liga', (('DFLT', ('dflt')),)),))
    font.addLookupSubtable('Ligatures', 'LigaturesSub')

    for g in font.glyphs():
        icon_name = g.glyphname                      # e.g. 'arrow_back'

        if icon_name in dummy_blank_chars: # do not add ligature mapping for blank characters
            continue

        # Translate every char → glyph-name FontForge uses
        comps = tuple(fontforge.nameFromUnicode(ord(c)) for c in icon_name)
        # Guard: skip if any component name is '.notdef'
        if all(c != '.notdef' for c in comps):
            g.addPosSub('LigaturesSub', comps)

# ------------------------------------------------------------------

# Generate the css file
if args.cssfile != '':
    f = open(args.cssfile, 'w')
    f.write('\n'.join(css))
    f.close()

    if args.htmlfile != '':
        f = open(args.htmlfile, 'w')
        f.write('\n'.join(html) +
'''
</div>
</body>        
''')
        f.close()

# Generate the font files
if args.woff1file != '':
    font.generate(args.woff1file)
if args.woff2file != '':
    font.generate(args.woff2file)

# Close the font
font.close()
