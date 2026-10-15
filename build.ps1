make -C sphinx clean
make -C sphinx html
rm ./docs/* -r -fo

# Create .nojekyll to prevent GitHub Pages from ignoring files and directories that start with an underscore
echo "" > ./docs/.nojekyll
cp -r sphinx/_build/html/* ./docs/
cp CNAME ./docs/

# robots.txt / sitemap.xml are copied from sphinx/_extra/ into the build root by
# html_extra_path; regenerate the sitemap so lastmod stays current.
python gen_sitemap.py

# Remove ?v=<hash> cache-busting query strings from HTML files.
# GitHub Pages serves static files directly and does not handle query strings,
# which causes 404 errors for .css/.js resources that carry ?v=... suffixes.
# python strip_query_strings.py ./docs