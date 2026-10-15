make -C sphinx clean
make -C sphinx html
rm -rf ./docs/*
touch ./docs/.nojekyll
cp -r sphinx/_build/html/* ./docs/
cp CNAME ./docs/

# robots.txt / sitemap.xml 由 sphinx/_extra/ 经 html_extra_path 复制到构建产物根，
# 上面的 cp -r 已一并带入 docs/；此处重新生成 sitemap 以保证 lastmod 最新。
python gen_sitemap.py

# Remove ?v=<hash> cache-busting query strings from HTML files.
# GitHub Pages serves static files directly and does not handle query strings,
# which causes 404 errors for .css/.js resources that carry ?v=... suffixes.
# python strip_query_strings.py ./docs