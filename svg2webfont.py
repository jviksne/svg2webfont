# Install FontForge
# Add FontForge bin directory to path.
# Run: fontforge -script svg2webfont.py

import fontforge
import argparse
import sys
import os
import argparse
import xml.etree.ElementTree as ET

def assert_dst_file_path(filepath:str, param:str):
    
    (path, file) = os.path.split(filepath)
    
    if file == "":
        print("%s does not point to a file" % (param,))
        sys.exit(-1)
    
    if path != "" and not os.path.isdir(path):
        print("directory %s of %s does not exist or is not a valid directory" % (path, param,))
        sys.exit(-1)

def get_rel_path(from_file:str, to_file:str, to_url:bool):
    
    (from_path, _) = os.path.split(from_file)
    (to_path, to_filename) = os.path.split(to_file)
    
    path = os.path.relpath(os.path.abspath(to_path), os.path.abspath(from_path))
    
    if to_url:
        return join_url_path(path.replace("\\", "/"), to_filename)
    
    return os.path.join(path, to_file)

def join_url_path(path:str, file:str):
    
    if path == "":
        return file
    
    if path.endswith("/"):
        return path + file
    
    return path + "/" + file

def esc_html_dq_str(s:str):
    return s.replace('"', '\\"')

def format_font_file_src_css(font_file_fs_path:str, css_fs_path:str, override_url_path:str, font_file_param:str, require_font_file_ext:str, css_format:str):
    
    if not font_file_fs_path.endswith(require_font_file_ext):
        print("%s file name must end with .%s extension" % (font_file_param, require_font_file_ext))
        sys.exit(-1)
    
    if override_url_path != "":
        (_, filename) = os.path.split(font_file_fs_path)
        url = join_url_path(args.css2fontpath, filename)
    else:
        url = get_rel_path(css_fs_path, font_file_fs_path, True)
    
    return 'url("%s") format("%s")' % (esc_html_dq_str(url), esc_html_dq_str(css_format))

def get_svg_viewbox(path):
    tree = ET.parse(path)
    root = tree.getroot()
    if 'viewBox' in root.attrib:
        parts = root.attrib['viewBox'].split()
        if len(parts) == 4:
            return [float(parts[0]), float(parts[1]), float(parts[2]), float(parts[3])]
    if 'width' in root.attrib and 'height' in root.attrib:
        return [0.0, 0.0, float(root.attrib['width']), float(root.attrib['height'])]
    return None

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

def print_debug(info:str, char_name:str = None):
    global args
    if args.debug:
        if char_name != None:
            print("%s: %s" % (char_name, info))
        else:
            print(info)

# Parse input arguments
parser = argparse.ArgumentParser()
parser.add_argument("-st", "--start", help="Unicode index in hexadecimal form to start from, default: \"EA01\"", default="EA01", type=str)
parser.add_argument("-src", "--srcdir", help="path to the directory with SVG files, default: \"./src/\"", default="./src/", type=str)
parser.add_argument("-ff", "--fontfamily", help="CSS font family name, default: \"Icon Font\"", default="Icon Font", type=str)
parser.add_argument("-gc", "--gencssclass", help="name for the generic CSS class shared by all element instances, default: \"ico\"", default="ico", type=str)
parser.add_argument("-pr", "--cssclassprefix", help="prefix for the individual font CSS classes, default: \"ico-\"", default="ico-", type=str)
parser.add_argument("-csc", "--cssfile", help="path to the generated CSS file, default: \"./dist/css/font.css\"", default="./dist/css/font.css", type=str)
parser.add_argument("-w1", "--woff1file", help="name of the WOFF v1 file, must have \".woff\" extension, default: \"./dist/fonts/font.woff\"", default="./dist/fonts/font.woff", type=str)
parser.add_argument("-w2", "--woff2file", help="name of the WOFF v2 file, must have \".woff2\" extension, default: \"./dist/fonts/font.woff2\"", default="./dist/fonts/font.woff2", type=str)
parser.add_argument("-htm", "--htmlfile", help="path to an HTML preview file listing all characters, default: \"./dist/preview.html\"", default="./dist/preview.html", type=str)
parser.add_argument("-fs", "--previewfontsize", help="default font size for HTML preview file, default: \"24px\"", default="24px", type=str)
parser.add_argument("-cfp", "--css2fontpath", help="override relative path from CSS file to the font files; if empty then will be calculated based on output file paths; pass \"./\" to override to same directory", default="", type=str)
parser.add_argument("-vh", "--height", help="to what to align the SVG view-box height, can be 'em' for the whole em, 'ascdesc' for ascent-descent or a number, default 'ascdesc'", default="ascdesc", type=str)
parser.add_argument("-min", "--minwidth", help="minimal advance width (how much space the font takes) in font units, besides a number can be 'auto' to match the drawing width or 'em', default 'auto'", default="auto", type=str)
parser.add_argument("-max", "--maxwidth", help="maximal advance width (how much space the font takes) in font units, besides a number can be 'auto' to match the drawing width or 'em', default 'auto'", default="auto", type=str)
parser.add_argument("-sw", "--separation", help="separation width in font units between characters, default 0", default=0, type=int)
parser.add_argument("-em", "--emsize", help="custom em size, default 1000", default=1000, type=int)
parser.add_argument("-d", "--debug", help="print additional information (e.g. size of each character in font units) helpful for debugging and tuning the font", action="store_true")
args = parser.parse_args()

if args.start == "":
    print("-st or --start is required")
    sys.exit(-1)

# Ensure all directories exist
if not os.path.exists(args.srcdir):
    print("svg file directory %s does not exist", args.srcdir)
    sys.exit(-1)

if args.cssfile != "":
    assert_dst_file_path(args.cssfile, "cssfile")

if args.woff1file != "":
    assert_dst_file_path(args.woff1file, "woff1file")

if args.woff2file != "":
    assert_dst_file_path(args.cssfile, "woff2file")

if args.htmlfile != "":
    assert_dst_file_path(args.htmlfile, "htmlfile")

# Format font-face src property value
if args.cssfile != "":

    if args.fontfamily == "":
        print("-ff or --fontfamily is required")
        sys.exit(-1)

    if args.gencssclass == "":
        print("-gc or --gencssclass is required")
        sys.exit(-1)

    if args.cssclassprefix == "":
        print("-pr or --cssclassprefix is required")
        sys.exit(-1)

    src = []
    
    if args.woff2file != "":
        src.append(format_font_file_src_css(args.woff2file, args.cssfile, args.css2fontpath, "woff2file", "woff2", "woff2"))

    if args.woff1file != "":
        src.append(format_font_file_src_css(args.woff1file, args.cssfile, args.css2fontpath, "woff1file", "woff", "woff"))

    if len(src) == 0:
        sys.exit("woff 2.0 or woff file name must be specified")

    fontfamily = args.fontfamily.replace('"', '\\"')

   # Store css rules in a string array
    css = ["""
@font-face {
  font-family: "%s";
  src: %s;
}

.%s {
    font-style: normal;
    text-rendering: auto;
    display: inline-block;
    font-variant: normal;
    -moz-osx-font-smoothing: grayscale;
    -webkit-font-smoothing: antialiased;
}
""" % (fontfamily, ",\n       ".join(src), args.gencssclass)]

    if args.htmlfile != "":
        html = [\
"""<html>
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
                font-size: 1rem;
            }
        </style>
    </head>
    <body>
    Icon font size: <input type="text" id="font-size" value="%s" onchange="document.getElementById('font-list').style.fontSize=this.value">
    <div id="font-list" style="font-size: %s; ">
""" % (esc_html_dq_str(get_rel_path(args.htmlfile, args.cssfile, True)),
        esc_html_dq_str(args.previewfontsize),
        esc_html_dq_str(args.previewfontsize))]
    else:
        html = None

else:
    css = None
    html = None

# Create a new font
font = fontforge.font()

font.em = args.emsize

print_debug("font.em=%s, font.ascent=%s, font.descent=%s," % (font.em, font.ascent, font.descent))

if args.height == "ascdesc":
    max_viewbox_height = font.ascent-font.descent
elif args.height == "em":
    max_viewbox_height = args.emsize
else:
    try:
        max_viewbox_height = int(args.height)
    except ValueError:
        print("height %s is not a number" % (args.height,))
        sys.exit(-1)

print_debug("max_viewbox_height: %s" % (max_viewbox_height,))


if args.minwidth == "em":
    adv_min_width = font.em
elif args.minwidth != "auto":
    try:
        adv_min_width = int(args.minwidth)
    except ValueError:
        print("minwidth %s is not a number" % (args.minwidth,))
        sys.exit(-1)
else:
    adv_min_width = None

if args.maxwidth == "em":
    adv_max_width = font.em
elif args.maxwidth != "auto":
    try:
        adv_max_width = int(args.maxwidth)
    except ValueError:
        print("maxwidth %s is not a number" % (args.maxwidth,))
        sys.exit(-1)
else:
    adv_max_width = None

# Set the starting Unicode value
curr_unicode = int(args.start, 16)

# Get the list of SVG files in the directory
svg_dir = args.srcdir
if not svg_dir.endswith("/"):
    svg_dir += "/"
svg_files = os.listdir(svg_dir)
svg_files = [f for f in svg_files if f.endswith('.svg')]
svg_files.sort()

max_width = 0.0
max_height = 0.0

# Iterate through the list of SVG files
for svg_file in svg_files:

    glyph_name = svg_file[0:-len('.svg')]
    if len(glyph_name) == 0:
        continue

    # Create a glyph
    glyph = font.createChar(curr_unicode)

    svg_file_path = os.path.join(svg_dir, svg_file)

    # Import the svg
    glyph.importOutlines(svg_file_path, scale=False) # Some paths do not get scaled by importOutlines with scale=True

    # Set name
    glyph.glyphname = glyph_name

    # Try to read the viewbox info from the SVG
    viewbox = get_svg_viewbox(svg_file_path)
    print_debug('svg viewbox read: %s' % (viewbox,), glyph_name)

    # Get the bounding box in the glyph
    bbox = glyph.boundingBox()
    print_debug("bbox before scale: %s, width: %d, height: %d" % (bbox, bbox[2]-bbox[0], bbox[3]-bbox[1]), glyph_name)

    # If viewbox could not be imported from the XML, use the bounding box
    if viewbox == None:
        viewbox = [float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])]
    else:
        # If viewbox could be imported from the XML, reposition it        
        # (0, 0) point of SVG is positioned at position (0, font.ascent)
        viewbox[1] = float(font.ascent) - (viewbox[3] - viewbox[1])
        viewbox[3] = float(font.ascent)

    print_debug('svg viewbox adjusted to: %s' % (viewbox,), glyph_name)

    initial_viewbox_width = viewbox[2] - viewbox[0]
    initial_viewbox_height = viewbox[3] - viewbox[1]

    # Some paths do not get scaled by importOutlines with scale=True
    # (TODO: figure out why exactly - possibly if they lack viewBox)
    # so scale manually to fit into em square

    # Calculate the scale
    scale = float(max_viewbox_height) / max(float(initial_viewbox_width), float(initial_viewbox_height))

    # Generate PostScript transformation matrix for scaling
    matrix = (scale, 0, 0,
              scale, 0, 0)
    print_debug("scale matrix: %s" % (matrix,), glyph_name)

    # Apply scaling matrix to outlines
    glyph.transform(matrix)

    # Apply scaling matrix to viewBox
    viewbox = transform(matrix, viewbox)

    bbox = glyph.boundingBox()

    # Calculate the scaled dimensions
    outline_width = bbox[2] - bbox[0]
    outline_height = bbox[3] - bbox[1]

    viewbox_width = viewbox[2] - viewbox[0]
    viewbox_height = viewbox[3] - viewbox[1]

    print_debug("bbox after scale: %s, width: %d, height: %d" % (bbox, outline_width, outline_height), glyph_name)
    print_debug("viewbox after scale: %s, width: %d, height: %d" % (viewbox, viewbox_width, viewbox_height), glyph_name)

    # Calculate the advance width of the font (the space it takes, not the space it is drawn in)
    advance_width = outline_width
    if adv_min_width != None and advance_width < adv_min_width:
        advance_width = adv_min_width
    
    if adv_max_width != None and advance_width > adv_max_width:
        advance_width = adv_max_width

    print_debug("advance_width=%s" % (advance_width,), glyph_name) 

    # Move the center of the viewbox to be in the center of the advance_width horizontally
    x_move = (float(advance_width) - viewbox_width) / 2.0 - viewbox[0]

    # Move the center of the viewbox to be in the center of the em vertically
    y_move = (float(font.em) - viewbox_height) / 2.0 - viewbox[1]

    print_debug("x_move: %d, y_move: %d" % (x_move, y_move), glyph_name)

    matrix = (1, 0, 0,
              1, x_move, y_move)
    print_debug("move matrix: %s" % (matrix,), glyph_name)

    glyph.transform(matrix)

    # Set the new width after the transform because transform would transform also the width
    glyph.width = int(round(advance_width))

    bbox = glyph.boundingBox()
    print_debug("bbox after move: %s" % (bbox,), glyph_name)
    
    if css != None:
        css.append(\
""".%s%s::before {
  content: "\\%s";
  font-family: "%s";
}
""" % (args.cssclassprefix, glyph_name, hex(curr_unicode)[2:], fontfamily))

        if html != None:
            html.append('<div><i class="%s %s%s"></i><br><span>%s</span></div>' % (
                args.gencssclass, args.cssclassprefix, glyph_name, glyph_name))

    # Increment the Unicode value for the next character
    curr_unicode += 1

# Set the font's encoding to Unicode
font.encoding = "unicode"

'''
if args.width == 'auto':
    font.selection.all()
    font.autoWidth(args.separation)
elif args.width == 'max':
    if args.debug:
        print("max_height=%d, max_width=%d" % (max_height, max_width))
    if max_height > max_width:
        max_width = max_height
    for glyph in font.glyphs():
        #glyph.transform((1, 0, 0, 1, int(round((max_width - initial_viewbox_width)/2.0 - float(bbox[0]))), 0))
        glyph.transform((1, 0, 0, 1, int(round((max_width - initial_viewbox_width)/2.0 - float(bbox[0]))), 0))
        # Set the new width after the transform because transform would transform also the width
        glyph.width = int(round(max_width))
'''
if args.debug:
    print("font.em: %s, font.ascent=%s, font.descent=%s," % (font.em, font.ascent, font.descent))
    for glyph in font.glyphs():
        bbox = glyph.boundingBox()
        print("%s, adv_width=%d, bbox=%s" % (glyph.glyphname, glyph.width, bbox))

# Generate the css file
if args.cssfile != "":
    f = open(args.cssfile, "w")
    f.write("\n".join(css))
    f.close()

    if args.htmlfile != "":
        f = open(args.htmlfile, "w")
        f.write("\n".join(html) +
"""
</div>
</body>        
""")
        f.close()

# Generate the font files
if args.woff1file != "":
    font.generate(args.woff1file)
if args.woff2file != "":
    font.generate(args.woff2file)

# Close the font
font.close()
