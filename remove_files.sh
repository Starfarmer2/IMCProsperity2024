# Create a file list from .gitignore
grep -v '^#' .gitignore | grep -v '^$' > files_to_remove.txt

# Run git filter-repo for each file
while IFS= read -r file; do
    git filter-repo --path "$file" --invert-paths
done < files_to_remove.txt
