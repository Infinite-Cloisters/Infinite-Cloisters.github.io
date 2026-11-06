#!/usr/bin/env bash
# 增量构建脚本（替代 build.sh 的破坏性步骤）
# 不执行 make clean / rm -rf ./docs/*，避免触发沙箱批量删除拦截。
set -e

PY="C:/Users/28035/AppData/Local/Python/pythoncore-3.14-64"
export PATH="$PY/Scripts:$PATH"

echo "==> sphinx html (增量)"
make -C sphinx html

echo "==> 同步到 docs/"
cp -r sphinx/_build/html/* ./docs/
cp CNAME ./docs/
touch ./docs/.nojekyll

echo "==> 生成 sitemap"
"$PY/python.exe" gen_sitemap.py

echo "==> 去除缓存查询串 (?v= / ?digest=)"
"$PY/python.exe" strip_query_strings.py ./docs

echo "==> 校验: HTML 中残留查询串应为 0"
grep -rlo '?v=[0-9a-f]\|?digest=' docs --include=*.html | wc -l
echo "==> 构建完成"
