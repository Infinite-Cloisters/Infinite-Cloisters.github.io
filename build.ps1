make -C sphinx html
rm ./docs/* -r -fo
cp -r sphinx/_build/html/* ./docs/