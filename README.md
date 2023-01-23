# svg2webfont

FontForge Python script for converting a list of SVG files into CSS web font for use as icons.

Each SVG file will be interpreted as representing a single character with the file name (without extension) becoming a CSS class with a custom ("ico-" by default) prefix. The SVG files do not need to be structured in any specific way.

Script generates a CSS file and two font files in WOFF and WOFF 2.0 formats that need to be uploaded to the web server's public directory. To use the fonts as icons the CSS file needs to be included. Sample icon HTML tag format:
`<i class="ico ico-settings"></i>`

By default the script generates also a preview HTML file that lists all of the icons. Preview file for the three sample Feather Icon (https://feathericons.com/, https://github.com/feathericons/feather) icons included in the repository: https://jviksne.github.io/svg2webfont/dist/preview.html

## Setup and usage

1. Install FontForge https://fontforge.org/ (consider donation https://fontforge.org/en-US/donate/ ).
2. Add "bin" directory (e.g. "C:\Program Files (x86)\FontForgeBuilds\bin") of FontForge installation to system path (optional).
3. Download this repository and extract to some directory.
4. Replace the three sample Feather Icon (https://feathericons.com/, https://github.com/feathericons/feather) SVG files in "src" directory with the final list of SVG files, each file representing a single character. Files must have ".svg" extension. File name (without extensions) will be used as the name of the CSS class for the specific character.
5. Delete the sample CSS and font files from "dist/css" and "dist/font" directories.
6. Run the script from command line with the following command (optional arguments listed below):
`fontforge --script svg2webfont.py`
7. Copy the directories with generated files under "dist" directory to the public dictory of your web server.
8. Include the css file into your HTML files:
`<link href="/css/font.css" rel="stylesheet">`
Note that by default the css file expected the font files to be located under "fonts" subdirectory of it's parent directory (../font/font.)
9. The HTML tag format for using the icon within the web page is:
 `<i class="ico ico-settings></i>`

## Arguments

The following arguments can be passed after the `--script svg2webfont.py` argument:

```
  -h, --help            show this help message and exit
  -st START, --start START
                        Unicode index in hexadecimal form to start from, default: 'EA01'
  -src SRCDIR, --srcdir SRCDIR
                        path to the directory with SVG files, default: './src/'
  -ff FONTFAMILY, --fontfamily FONTFAMILY
                        CSS font family name, default: 'Icon Font'
  -gc GENCSSCLASS, --gencssclass GENCSSCLASS
                        name for the generic CSS class shared by all element instances, default: 'ico'
  -pr CSSCLASSPREFIX, --cssclassprefix CSSCLASSPREFIX
                        prefix for the individual font CSS classes, default: 'ico-'
  -csc CSSFILE, --cssfile CSSFILE
                        path to the generated CSS file, default: './dist/css/font.css'
  -w1 WOFF1FILE, --woff1file WOFF1FILE
                        name of the WOFF v1 file, must have '.woff' extension, default: './dist/fonts/font.woff'
  -w2 WOFF2FILE, --woff2file WOFF2FILE
                        name of the WOFF v2 file, must have '.woff2' extension, default: './dist/fonts/font.woff2'
  -htm HTMLFILE, --htmlfile HTMLFILE
                        path to an HTML preview file listing all characters, default: './dist/preview.html'
  -fs PREVIEWFONTSIZE, --previewfontsize PREVIEWFONTSIZE
                        default font size for HTML preview file, default: '24px'
  -cfp CSS2FONTPATH, --css2fontpath CSS2FONTPATH
                        override relative path from CSS file to the font files; if empty then will be calculated based
                        on output file paths; pass './' to override to same directory
  -upm UPMSIZE, --upmsize UPMSIZE
                        units per em, default 1000
  -asc ASCENT, --ascent ASCENT
                        ascent size (distance from baseline to top), default 800
  -des DESCENT, --descent DESCENT
                        descent size (distance from baseline to bottom), default 200
  -sc SCALE, --scale SCALE
                        how to scale the SVG view-box, can be 'in_em','over_em','ascdesc', 'no' or a float scale
                        factor number, default: 'in_em'
  -ha HALIGN, --halign HALIGN
                        how to align the scaled SVG view-box relative to advance width horizontally, can be
                        'center','left','right' or a number interpreted as a center in font units, default: 'center'
  -va VALIGN, --valign VALIGN
                        how to align the scaled SVG view-box vertically, can be 'base_em_center',
                        'ascdesc_center','baseline','descent' or a number interpreted as a center in font units,
                        default: 'ascdesc_center'
  -x XMOVE, --xmove XMOVE
                        by how many units to move the scaled and aligned SVG view-box horizontally, default: 0
  -y YMOVE, --ymove YMOVE
                        by how many units to move the scaled and aligned SVG view-box vertically, default: 0
  -min MINWIDTH, --minwidth MINWIDTH
                        minimal advance width (how much space the font uses horizontally) in font units, besides a
                        number can be 'auto' to match the outline (drawing) width or 'em', default 'auto'
  -max MAXWIDTH, --maxwidth MAXWIDTH
                        maximal advance width (how much space the font uses horizontally) in font units, besides a
                        number can be 'auto' to match the outline (drawing) width or 'em', default 'auto'
  -sw SEPARATION, --separation SEPARATION
                        separation width in font units between characters, default 0
  -d, --debug           print additional information (e.g. size of each character in font units) helpful for debugging
                        and tuning the font
```

## Sample call with arguments

The following call will generate all files in the same (current) directory with the generic CSS class named "ff" and all icon CSS classes having "ff-" prefix:

```
fontforge --script svg2webfont.py --fontfamily "Feather Icons" --cssfile "feather-icons.css" --woff1file "feather-icons.woff" --woff2file "feather-icons.woff2" --htmlfile "preview.html" --gencssclass "ff" --cssclassprefix "ff-"
```
