# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Documentation'
copyright = '2026, infinite-cloisters'
author = 'infinite-cloisters'
release = '0.1.9'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
master_doc = 'index'

extensions = ['recommonmark', 'sphinx_markdown_tables','sphinx_copybutton']

source_suffix = {'.rst': 'restructuredtext', '.md': 'markdown'}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'zh_CN'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'sphinx_rtd_theme'
# html_theme = 'shibuya'
html_theme = 'sphinx_book_theme'
html_theme_options = {
    "repository_url": "https://github.com/Infinite-Cloisters/Infinite-Cloisters.github.io"
}

html_static_path = ['_static']

# 会被原样复制到构建产物根目录的文件（robots.txt、sitemap.xml 等必须位于站点根）。
# 放在 _static 里只会得到 /_static/xxx，达不到 robots.txt 必须在根路径的要求。
html_extra_path = ['_extra']

import sphinx
from pathlib import Path
from sphinx.search.zh import SearchChinese

html_search_language = 'zh'
jieba_dict = Path(__file__).parent / 'jieba_dict.txt'
html_search_options = {'dict': str(jieba_dict)} if jieba_dict.is_file() else {}

def zh_js_stemmer_code() -> str:
    js_dir = Path(sphinx.__file__).parent / 'search' / 'minified-js'
    base = (js_dir / 'base-stemmer.js').read_text(encoding='utf-8')
    english = (js_dir / 'english-stemmer.js').read_text(encoding='utf-8')

    return f'{base}\n{english}\nwindow.Stemmer = EnglishStemmer;'

class ChineseSearch(SearchChinese):
    js_stemmer_rawcode = '' 
    js_stemmer_code = zh_js_stemmer_code()

def setup(app):
    app.add_search_language(ChineseSearch)