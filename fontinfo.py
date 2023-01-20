# Install FontForge
# Add FontForge bin directory to path.
# Run: fontforge -script fontinfo.py -f path/to/font.woff2

import fontforge
import argparse

# Parse input arguments
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", help="font file path", type=str, required=True)
parser.add_argument("-c", "--charcodes", help="a comma separated list of hex char codes for which to print info", type=str)
parser.add_argument("-s", "--start", help="hex char code from which to start info printing", type=str)
parser.add_argument("-e", "--end", help="hex char code at which to end info printing", type=str)
parser.add_argument("-n", "--name", help="name of the character to be printed", type=str)
args = parser.parse_args()

if args.charcodes != None and args.charcodes != "":
    charcodes = [int(charcode.strip(),16) for charcode in args.charcodes.split(",") if charcode.strip() != ""]
else:
    charcodes = None

if args.start != None and args.start != "":
    start = int(args.start, 16)
else:
    start = None

if args.end != None and args.end != "":
    end = int(args.end, 16)
else:
    end = None

if charcodes == None and start == None and end == None and (args.name == None or args.name == ""):
    print_all = True
else:
    print_all = False

font = fontforge.open(args.file)
print("Font em: %s, ascent=%s, descent=%s," % (font.em, font.ascent, font.descent))

for glyph in font.glyphs():
    if print_all \
        or (charcodes != None and glyph.unicode in charcodes) \
        or (start != None and glyph.unicode >= start and (end == None or glyph.unicode <= end)) \
        or (start == None and end != None and glyph.unicode <= end) \
        or (args.name != None and args.name == glyph.glyphname):
        print("Char code: %x (%d), name: %s, bbox: %s" % (glyph.unicode, glyph.unicode, glyph.glyphname, glyph.boundingBox()))

font.close()