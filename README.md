# svg2cssfont
 FontForge Python script for converting a list of SVG files into CSS web font for use as icons.
 Each file will be considered to represent a single character with the file name (without extension) becoming a CSS class with a custom ("ico-" by default) prefix.
 Files do not need to be structured.
 Script generates a css file and two font files in WOFF and WOFF 2.0 formats.
 To use the fonts as icons the CSS file needs to be included.
 Icon HTML tag format will look like this:
 `<i class="ico ico-settings></i>`

## Setup and usage

1. Install FontForge https://fontforge.org/ (consider donation https://fontforge.org/en-US/donate/ ).
2. Add "bin" directory (e.g. "C:\Program Files (x86)\FontForgeBuilds\bin") of FontForge installation to system path (optional).
3. Download this script and extract to some directory.
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