#!/bin/bash

ORIG_DIR="$1"
cd "$ORIG_DIR" || exit 1

curl -LO https://www.cs.kent.ac.uk/~djb/pgn-extract/pgn-extract-25-01.zip -P .
cd .
unzip pgn-extract-25-01
cd pgn-extract
make
ln -s -v "$PWD/pgn-extract/pgn-extract" /usr/local/bin/pgn-extract
echo "pgn-extract installed successfully."
echo "You can now run pgn-extract from anywhere in your terminal."