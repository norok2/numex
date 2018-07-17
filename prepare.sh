#!/usr/bin/env bash

inkscape -d 300 numex_logo.svgz  --export-png=numex_logo.png
cp numex_logo.png icon.png
convert icon.png icon.xbm
convert icon.png icon.gif
