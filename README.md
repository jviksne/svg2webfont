# svg2cssfont
 FontForge Python script for converting a list of SVG files into CSS web font for use as icons.
 
 Each SVG file will be interpreted as representing a single character with the file name (without extension) becoming a CSS class with a custom ("ico-" by default) prefix. The SVG files do not need to be structed in any specific way.

 Script generates a CSS file and two font files in WOFF and WOFF 2.0 formats that need to be uploaded to the web server's public directory. To use the fonts as icons the CSS file needs to be included. Sample icon HTML tag format:
 `<i class="ico ico-settings></i>`

## Setup and usage

1. Install FontForge https://fontforge.org/ (consider donation https://fontforge.org/en-US/donate/ ).
2. Add "bin" directory (e.g. "C:\Program Files (x86)\FontForgeBuilds\bin") of FontForge installation to system path (optional).
3. Download this repository and extract to some directory.
4. Replace the three sample Feather Icon (https://feathericons.com/ , https://github.com/feathericons/feather) SVG files in "src" directory with the final list of SVG files, each file representing a single character. Files must have ".svg" extension. File name (without extensions) will be used as the name of the CSS class for the specific character. 
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

```
  -h, --help            show help message and exit
  -st START, --start START
                        unicode index to start from, default 0xEA01
  -src SRCDIR, --srcdir SRCDIR
                        path to the directory with SVG files, default "./src/"
  -fp FONTPATH, --fontpath FONTPATH
                        relative path from css file to font files, default: "../fonts/"
  -ff FONTFAMILY, --fontfamily FONTFAMILY
                        css font family name
  -css CSSFILE, --cssfile CSSFILE
                        name of the woff file, default "font.css"
  -wf1 WOFF1FILE, --woff1file WOFF1FILE
                        name of the woff 2.0 file, must have ".woff2" extnesion, default "font.woff"
  -wf2 WOFF2FILE, --woff2file WOFF2FILE
                        name of the woff2 file, must have ".woff" extnesion, default "font.woff2"
  -gc GENCSSCLASS, --gencssclass GENCSSCLASS
                        name for the generic css class shared by all element instances, default "ico"
  -pr CSSCLASSPREFIX, --cssclassprefix CSSCLASSPREFIX
                        prefix for the individual font css classes, default "ico-"
  -dc DESTCSSDIR, --destcssdir DESTCSSDIR
                        destination directory where to put css files, default "./dist/css/"
  -df DESTFONTDIR, --destfontdir DESTFONTDIR
                        destination directory where to put font files, default "./dist/fonts/"
```