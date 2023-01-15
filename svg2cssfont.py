# Install FontForge
# Add Font Forge bin directory to path.
# Run:
# fontforge -script svg2cssfont.py

import fontforge
import argparse
import sys
import os
import argparse

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

# Set the starting Unicode value
curr_unicode = int(args.start, 16)

# Get the list of SVG files in the directory
svg_dir = args.srcdir
if not svg_dir.endswith("/"):
    svg_dir += "/"
svg_files = os.listdir(svg_dir)
svg_files = [f for f in svg_files if f.endswith('.svg')]
svg_files.sort()

# Iterate through the list of SVG files
for svg_file in svg_files:

    char_name = svg_file[0:-len('.svg')]
    if len(char_name) == 0:
        continue

    # Create a glyph
    glyph = font.createChar(curr_unicode)

    # Import the svg
    glyph.importOutlines(os.path.join(svg_dir, svg_file))

    bbox = glyph.boundingBox()

    # Center horizontally
    center = (bbox[2] - bbox[0])/2

    # move the character to the center of the width
    glyph.transform((1,0,0,1,-center,0))
    
    if css != None:
        css.append(\
""".%s%s::before {
  content: "\\%s";
  font-family: "%s";
}
""" % (args.cssclassprefix, char_name, hex(curr_unicode)[2:], fontfamily))

        if html != None:
            html.append('<div><i class="%s %s%s"></i><br><span>%s</span></div>' % (
                args.gencssclass, args.cssclassprefix, char_name, char_name))

    # Increment the Unicode value for the next character
    curr_unicode += 1

# Set the font's encoding to Unicode
font.encoding = "unicode"

#font.selection.all()
#font.centerInWidth()

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
