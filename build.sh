make -C sphinx clean
make -C sphinx html
rm -rf ./docs/*
touch ./docs/.nojekyll
cp -r sphinx/_build/html/* ./docs/