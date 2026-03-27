make -C sphinx clean
make -C sphinx html
rm -rf ./docs/*
touch ./docs/.nojekyll
cp -r sphinx/_build/html/* ./docs/
cp CNAME ./docs/

# Remove ?v=<hash> cache-busting query strings from HTML files.
# GitHub Pages serves static files directly and does not handle query strings,
# which causes 404 errors for .css/.js resources that carry ?v=... suffixes.
python strip_query_strings.py ./docs