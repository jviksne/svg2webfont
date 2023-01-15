# svg2cssfont

FontForge Python script for converting a list of SVG files into CSS web font for use as icons.

Each SVG file will be interpreted as representing a single character with the file name (without extension) becoming a CSS class with a custom ("ico-" by default) prefix. The SVG files do not need to be structed in any specific way.

Script generates a CSS file and two font files in WOFF and WOFF 2.0 formats that need to be uploaded to the web server's public directory. To use the fonts as icons the CSS file needs to be included. Sample icon HTML tag format:
`<i class="ico ico-settings"></i>`

By default the script generates also a preview HTML file that lists all of the icons. Preview file for the three sample Feather Icon (https://feathericons.com/, https://github.com/feathericons/feather) icons included in the repository: https://jviksne.github.io/svg2cssfont/dist/preview.html

## Setup and usage

1. Install FontForge https://fontforge.org/ (consider donation https://fontforge.org/en-US/donate/ ).
2. Add "bin" directory (e.g. "C:\Program Files (x86)\FontForgeBuilds\bin") of FontForge installation to system path (optional).
3. Download this repository and extract to some directory.
4. Replace the three sample Feather Icon (https://feathericons.com/, https://github.com/feathericons/feather) SVG files in "src" directory with the final list of SVG files, each file representing a single character. Files must have ".svg" extension. File name (without extensions) will be used as the name of the CSS class for the specific character.
5. Delete the sample CSS and font files from "dist/css" and "dist/font" directories.
6. Run the script from command line with the following command (optional arguments listed below):
`fontforge --script svg2cssfont.py`
7. Copy the directories with generated files under "dist" directory to the public dictory of your web server.
8. Include the css file into your HTML files:
`<link href="/css/font.css" rel="stylesheet">`
Note that by default the css file expected the font files to be located under "fonts" subdirectory of it's parent directory (../font/font.)
9. The HTML tag format for using the icon within the web page is:
 `<i class="ico ico-settings></i>`

## Arguments

The following arguments can be passed after the `--script svg2cssfont.py` argument:

```
  -h, --help            show this help message and exit
  -st START, --start START
                        Unicode index in hexadecimal form to start from, default: "EA01"
  -src SRCDIR, --srcdir SRCDIR
                        path to the directory with SVG files, default: "./src/"
  -ff FONTFAMILY, --fontfamily FONTFAMILY
                        CSS font family name, default: "Icon Font"
  -gc GENCSSCLASS, --gencssclass GENCSSCLASS
                        name for the generic CSS class shared by all element instances, default: "ico"
  -pr CSSCLASSPREFIX, --cssclassprefix CSSCLASSPREFIX
                        prefix for the individual font CSS classes, default: "ico-"
  -csc CSSFILE, --cssfile CSSFILE
                        path to the generated CSS file, default: "./dist/css/font.css"
  -w1 WOFF1FILE, --woff1file WOFF1FILE
                        name of the WOFF v1 file, must have ".woff" extension, default: "./dist/fonts/font.woff"
  -w2 WOFF2FILE, --woff2file WOFF2FILE
                        name of the WOFF v2 file, must have ".woff2" extension, default: "./dist/fonts/font.woff2"
  -htm HTMLFILE, --htmlfile HTMLFILE
                        path to an HTML preview file listing all characters, default: "./dist/preview.html"
  -fs PREVIEWFONTSIZE, --previewfontsize PREVIEWFONTSIZE
                        default font size for HTML preview file, default: "24px"
  -cfp CSS2FONTPATH, --css2fontpath CSS2FONTPATH
                        override relative path from CSS file to the font files; if empty then will be calculated based
                        on output file paths; pass "./" to override to same directory
```

## Sample call with arguments

The following call will generate all files in the same (current) directory with the generic CSS class named "ff" and all icon CSS classes having "ff-" prefix:

```
fontforge --script svg2cssfont.py --fontfamily "Feather Icons" --cssfile "feather-icons.css" --woff1file "feather-icons.woff" --woff2file "feather-icons.woff2" --htmlfile "preview.html" --gencssclass "ff" --cssclassprefix "ff-"
```