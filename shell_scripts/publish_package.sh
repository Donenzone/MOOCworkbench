#!/bin/bash
cd "$1"
zip -r "$3" "$2"
rm -r "$2"