make -C sphinx html
rm -rf ./docs/*
cp -r sphinx/_build/html/* ./docs/