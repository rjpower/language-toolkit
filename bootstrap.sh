#!/bin/bash

./virtualenv.py --clear --distribute .

# local symlinks confuse things
rm -rf ./local/
