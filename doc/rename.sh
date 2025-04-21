#!/bin/bash

API_DIR="source/api"
PREFIX="fastlob."

cd "$API_DIR" || exit 1

# Rename files by removing the prefix
for file in ${PREFIX}*.rst; do
    new_name="${file#$PREFIX}"
    echo "Renaming $file -> $new_name"
    mv "$file" "$new_name"

    # Optional: Replace heading title inside the file
    sed -i "s/^$PREFIX//" "$new_name"
done

echo "Done stripping '$PREFIX' prefix from filenames and file contents."

