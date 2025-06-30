#!/bin/bash

rm -rf source/api

sphinx-apidoc -o source/api ../fastlob

bash rename.sh

rm source/api/fastlob.rst source/api/modules.rst

make clean

make html
