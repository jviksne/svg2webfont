# Install FontForge
# Add Font Forge bin directory to path.
# Run:
# fontforge -script svg2cssfont.py

import fontforge
import argparse
import sys
import os
import argparse
import subprocess

# Parse input arguments
parser = argparse.ArgumentParser()
parser.add_argument("-st", "--start", help="unicode index to start from, default: 0xEA01", default=0xEA01, type=int)
parser.add_argument("-src", "--srcdir", help="path to the directory with SVG files, default: \"./src/\"", default="./src/", type=str)
parser.add_argument("-fp", "--fontpath", help="relative path from css file to font files, default: \"../fonts/\"", default="../fonts/", type=str)
parser.add_argument("-ff", "--fontfamily", help="css font family name, default: \"Icon Font\"", default="Icon Font", type=str)
parser.add_argument("-css", "--cssfile", help="name of the woff file, default: \"font.css\"", default="font.css", type=str)
parser.add_argument("-wf1", "--woff1file", help="name of the woff 2.0 file, must have \".woff2\" extnesion, default: \"font.woff\"", default="font.woff", type=str)
parser.add_argument("-wf2", "--woff2file", help="name of the woff2 file, must have \".woff\" extnesion, default: \"font.woff2\"", default="font.woff2", type=str)
parser.add_argument("-gc", "--gencssclass", help="name for the generic css class shared by all element instances, default: \"ico\"", default="ico", type=str)
parser.add_argument("-pr", "--cssclassprefix", help="prefix for the individual font css classes, default: \"ico-\"", default="ico-", type=str)
parser.add_argument("-dc", "--destcssdir", help="destination directory where to put css files, default: \"./dist/css/\"", default="./dist/css/", type=str)
parser.add_argument("-df", "--destfontdir", help="destination directory where to put font files, default: \"./dist/fonts/\"", default="./dist/fonts/", type=str)
args = parser.parse_args()

if args.start == "":
    print("-st or --start is required")
    sys.exit(-1)

if args.fontfamily == "":
    print("-ff or --fontfamily is required")
    sys.exit(-1)

if args.gencssclass == "":
    print("-gc or --gencssclass is required")
    sys.exit(-1)

if args.cssclassprefix == "":
    print("-pr or --cssclassprefix is required")
    sys.exit(-1)

# Ensure trailing slash for a non-empty HTTP path
if args.fontpath != "" and not args.fontpath.endswith("/"):
    args.fontpath += "/"

if not os.path.exists(args.srcdir):
    print("svg file directory %s does not exist", args.srcdir)

if not os.path.exists(args.destcssdir):
    print("css file directory %s does not exist", args.destcssdir)

if not os.path.exists(args.destfontdir):
    print("font file directory %s does not exist", args.destfontdir)

# Format font-face src property value
src = []
if args.woff2file != "":
    if not args.woff2file.endswith(".woff2"):
        sys.exit("woff 2.0 file name must end with .woff2 extension")
    src.append('url("%s%s") format("woff2")' % (args.fontpath.replace('"', '\\"'), args.woff2file.replace('"', '\\"')))
if args.woff1file != "":
    if not args.woff1file.endswith(".woff"):
        sys.exit("woff file name must end with .woff extension")
    src.append('url("%s%s") format("woff")' % (args.fontpath.replace('"', '\\"'), args.woff1file.replace('"', '\\"')))

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

# Create a new font
font = fontforge.font()

# Set the starting Unicode value
curr_unicode = args.start

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

    css.append(\
""".%s%s::before {
  content: "\\%s";
  font-family: "%s";
}
""" % (args.cssclassprefix, char_name, hex(curr_unicode)[2:], fontfamily))

    # Increment the Unicode value for the next character
    curr_unicode += 1

"""     # Open the SVG file
    print(os.path.join(svg_dir, svg_file))
    svg = fontforge.open(os.path.join(svg_dir, svg_file))

    # Iterate through the characters in the SVG file
    for char in svg.glyphs():
        # Add the character to the new font
        font.createChar(curr_unicode)
        font[curr_unicode].importOutlines(char)

        css.append(\
" "".%s%s::before {
  content: "%s";
  font-family: "%s";
}
" "", )

        # Increment the Unicode value for the next character
        curr_unicode += 1 """

    # Close the SVG file
    #svg.close()

# Set the font's encoding to Unicode
font.encoding = "unicode"

# Generate css file
if args.cssfile != "":
    f = open(os.path.join(args.destcssdir, args.cssfile), "w")
    f.write("\n".join(css))
    f.close()

if args.woff1file != "":
    font.generate(os.path.join(args.destfontdir, args.woff1file))

# Generate the font files
if args.woff2file != "":
    font.generate(os.path.join(args.destfontdir, args.woff2file))

# Close the font
font.close()
