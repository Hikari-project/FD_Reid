#!/bin/bash
count_lines() {
    local file_path="$1"
    local lines=$(wc -l < "$file_path")
    echo "$lines"
}

count_lines_in_directory() {
    local directory_path="$1"
    local total_lines=0

    find "$directory_path" -type f -name "*.py" | while read -r file; do
        lines=$(count_lines "$file")
        echo "$file lines: $lines"
        total_lines=$((total_lines + lines))
        echo "$total_lines"
    done

}

folder_path="./"  # your project path
count_lines_in_directory "$folder_path"

