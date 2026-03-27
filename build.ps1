make -C sphinx clean
make -C sphinx html
rm ./docs/* -r -fo

# Create .nojekyll to prevent GitHub Pages from ignoring files and directories that start with an underscore
echo "" > ./docs/.nojekyll
cp -r sphinx/_build/html/* ./docs/