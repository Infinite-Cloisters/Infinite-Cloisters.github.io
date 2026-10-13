.. _sphinx_chinese_search:

中文搜索为什么搜不到：一次完整的排错
============================================================



本站的搜索一度是\ **完全不可用**\ 的：搜索页能正常打开、输入框也能输入，但结果区永远停在「正在搜索中..」，中文英文一律搜不出任何东西。

下面记录从现象到根因的完整过程，最后给出修法。结论是：**问题不在本站的配置里，而在 Sphinx 9.1.0 自身**——截至本文写作，9.1.0 已是最新版，上游尚未修复。

.. note::

   如果你也遇到同样的问题，可以直接跳到「根因」一节，但建议看完「先排除的四个假象」——那几步能避免把时间花在错误的方向上。

症状
--------

- 搜索结果区永远显示 ``正在搜索中..``，结果列表 ``<ul class="search">`` 恒为空。
- 中文、英文都搜不到，所以\ **不是**\ 分词问题。
- 页面本身不报错，界面上没有任何异常提示——这一点最容易误导人。

先排除的四个假象
--------------------

排错最怕的是把「看起来像原因的东西」当成原因。下面这四条都被逐一排除掉了。

**一、静态资源没加载？** 不是。起一个本地服务（``python -m http.server``）看访问日志，``searchtools.js``、``language_data.js``、``searchindex.js`` 全部返回 200，整个页面只有 ``favicon.ico`` 是 404。

**二、是查询串导致的 404？** 不是。实测线上带浏览器 UA 请求 ``_static/documentation_options.js?v=<hash>``，返回的是 200。

**三、线上站点整站 403，是不是服务器挂了？** 也不是。``curl`` 不加 User-Agent 会被 WAF 当成爬虫拦掉，整站返回 403；加上浏览器 UA 之后一切正常。**排查线上问题时 curl 必须带 UA**，否则会得到一个完全错误的结论。

**四、jieba 没装？** 这个判断源于用错了 Python 解释器。裸 ``python`` 指向的环境里确实没有 jieba，但构建实际使用的是安装了 Sphinx 和 jieba 的那个解释器。反过来看索引内容也能证明分词是好的——索引里存在 ``表格``、``安装``、``环境``、``宏包`` 这些中文词。

.. warning::

   这一条值得记牢：判断「某个包有没有装」之前，先确认自己用的是\ **构建时那个解释器**，否则整条线索都是假的。

定位：注入错误探针
----------------------

四个假象排除之后，剩下的可能就只有「JS 运行时报错」。但页面不会把错误显示出来，所以在 ``<head>`` 里注入一段探针，把错误写进 ``document.title``，再用无头浏览器把渲染后的 DOM dump 回来看：

.. code-block:: html

   <script>
   window.__diag = [];
   window.addEventListener('error', function (e) {
     window.__diag.push('ERROR: ' + e.message + ' @' + e.filename + ':' + e.lineno);
     document.title = 'DIAG::' + window.__diag.join(' || ');
   }, true);
   window.addEventListener('unhandledrejection', function (e) {
     window.__diag.push('REJECT: ' + e.reason);
     document.title = 'DIAG::' + window.__diag.join(' || ');
   });
   </script>

抓到的错误是：

.. code-block:: text

   Uncaught ReferenceError: ChineseStemmer is not defined
       @ /_static/language_data.js:13
   Uncaught ReferenceError: Stemmer is not defined
       @ /_static/searchtools.js:304
   typeof Search=object;  Search.query=undefined;  Search._index=NULL

到这里就清楚了：``language_data.js`` 加载即抛错，紧接着 ``searchtools.js`` 也抛错，连 ``Search.query`` 都没挂上去，搜索功能自然整个瘫掉。

根因：一个上游 bug
----------------------

打开生成的 ``_static/language_data.js``，最后一行是：

.. code-block:: javascript

   window.Stemmer = ChineseStemmer;

而这个文件里内联进来的词干代码，只定义了 ``BaseStemmer`` 和 ``EnglishStemmer``——``ChineseStemmer`` 从来不存在。

问题出在 Sphinx 的 ``sphinx/search/__init__.py`` 第 588 行：

.. code-block:: python

   def get_js_stemmer_code(self) -> str:
       if not self.lang.js_stemmer_rawcode:
           return self.lang.js_stemmer_code
       base_js_path = _MINIFIED_JS_PATH / 'base-stemmer.js'
       language_js_path = _MINIFIED_JS_PATH / self.lang.js_stemmer_rawcode
       return '\n'.join((
           base_js_path.read_text(encoding='utf-8'),
           language_js_path.read_text(encoding='utf-8'),
           f'window.Stemmer = {self.lang.language_name}Stemmer;',   # ← 用 language_name 拼变量名
       ))

它用 ``language_name`` 去拼 JS 里的变量名，对绝大多数语言都成立。但中文搜索类 ``SearchChinese`` 里这两者并不一致：

- ``language_name = 'Chinese'`` → 拼出 ``ChineseStemmer``
- ``js_stemmer_rawcode = 'english-stemmer.js'`` → 文件里定义的是 ``EnglishStemmer``

名字对不上，于是生成了一行引用未定义变量的代码。**任何使用 zh 搜索的 Sphinx 9.1.0 站点都会中招**，与主题、托管平台无关。

修复
--------

思路很简单：注册一个自己的中文搜索类，把 ``js_stemmer_code`` 自己拼出来，让别名指向真实存在的 ``EnglishStemmer``。在 ``conf.py`` 里加上：

.. code-block:: python

   import sphinx
   from pathlib import Path
   from sphinx.search.zh import SearchChinese


   def zh_js_stemmer_code() -> str:
       js_dir = Path(sphinx.__file__).parent / 'search' / 'minified-js'
       base = (js_dir / 'base-stemmer.js').read_text(encoding='utf-8')
       english = (js_dir / 'english-stemmer.js').read_text(encoding='utf-8')
       return f'{base}\n{english}\nwindow.Stemmer = EnglishStemmer;'


   class ChineseSearch(SearchChinese):
       js_stemmer_rawcode = ''            # 置空 -> Sphinx 改用下面的 js_stemmer_code
       js_stemmer_code = zh_js_stemmer_code()


   def setup(app):
       app.add_search_language(ChineseSearch)

为什么这样能生效
~~~~~~~~~~~~~~~~~~~~

``SearchLanguage`` 自带 ``lang = 'zh'``，自定义类继承它，所以 ``ChineseSearch.lang`` 仍然是 ``'zh'``；而 ``app.add_search_language(cls)`` 做的事情是：

.. code-block:: python

   languages[cls.lang] = cls

也就是把注册表里的 ``'zh'`` 覆盖掉。之后 ``IndexBuilder`` 通过 ``languages.get(html_search_language)`` 拿到的就是我们的类。因此 ``html_search_language = 'zh'`` 保持不变即可，不需要改任何配置。

为什么用 EnglishStemmer 而不是空词干
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

一个自然的想法是「中文不需要词干化，直接写个什么都不做的 Stemmer」。但这是错的：Python 侧的 ``SearchChinese.stem()`` 本来就用英文 snowball 词干处理拉丁词，如果 JS 侧不处理，两边就不一致——索引里存的是 ``table``，而查询时输入 ``tables`` 词干化后仍是 ``tables``，就对不上了。用 ``EnglishStemmer`` 才能和 Python 侧对齐。

.. note::

   副作用：``js_stemmer_rawcode`` 置空后，Sphinx 不再把 ``base-stemmer.js`` 和 ``english-stemmer.js`` 拷进 ``_static/``。这两个文件本来就没有任何页面引用，属于纯参考文件，没有影响。

让中文词组真正能被搜到：自定义词典
--------------------------------------

修完上面那个 bug，搜索能用了，但还有一个体验问题：很多词组搜不到。原因是\ **索引侧和查询侧的分词方式不一样**。

- 索引侧（Python）：jieba 把中文切成词。
- 查询侧（浏览器）：``searchtools.js`` 里的默认 ``splitQuery`` 按「非字母数字」切分，而汉字属于 Unicode 的 ``Letter``，所以\ **整段中文一个词都不会被切**。中文没有自己的 JS 分词器。

结果就是：你在输入框里输入的整个中文串，会被当成\ **一个**\ 词条去查索引。所以只要 jieba 没有把它作为一个整体切出来，这个词就永远搜不到。

解决办法是给 jieba 一份自定义词典。文件放在 ``sphinx/jieba_dict.txt``，``conf.py`` 里这样接：

.. code-block:: python

   html_search_language = 'zh'
   jieba_dict = Path(__file__).parent / 'jieba_dict.txt'
   html_search_options = {'dict': str(jieba_dict)} if jieba_dict.is_file() else {}

文件格式是 ``词 [频次] [词性]``，**频次和词性都可以省略**：

.. code-block:: text

   科技论文写作
   交叉编译 1000 n

.. warning::

   jieba 的用户词典\ **不支持**\ ``#`` 注释。``load_userdict`` 只跳过空行，注释行会被整行当成一个词条。所以这个文件里只能放纯词条，想记「为什么加这个词」请写在提交信息里。

改了词典\ **必须重新构建**\ 才会生效——词典只在生成索引时起作用，对已经打开的页面无效。

怎么判断一个词该不该加
~~~~~~~~~~~~~~~~~~~~~~~~~~

两步实测，不要凭感觉：

1. 看 jieba 能不能把整词切出来。判定标准是\ **整词在不在输出列表里**，而不是「输出是不是只有这一个元素」：

   .. code-block:: bash

      python -c "import jieba; print(list(jieba.cut_for_search('科技论文写作')))"

   ``cut_for_search`` 是搜索引擎模式，对长度大于 2 的词会先吐出子词、再吐整词。以 ``单片机`` 为例，输出是 ``['单片', '单片机']``——整词在，说明它本来就没问题，不需要加。

2. 确认这个词真的出现在文档内容里。没有出现过的词写进词典毫无意义：

   .. code-block:: bash

      grep -rl '科技论文写作' sphinx/doc | wc -l

为什么整句中文搜不到
------------------------

修好词典之后仍然会有人问：「我把一整句话粘进去，怎么还是搜不到？」这不是故障，而是上面那个不对称的必然结果。

- **整句中文搜不到。** 整串被当作一个词条，索引里不会有这么长的词。要按词搜。
- **多个词之间是「与」的关系。** 用空格分隔出多个词时，只有\ **同一页同时包含全部词**\ 才会命中。所以搜不到时，先算一下这几个词有没有同页共现，再怀疑分词。
- **单个汉字不入索引。** ``SearchChinese.word_filter`` 要求词长大于 1，所以像 ``源`` 这样的单字永远搜不到。

怎么验证搜索真的好了
------------------------

最直接的办法是问索引和问浏览器，两件事都要做。

查索引里有没有这个词（不改任何东西，纯读取）：

.. code-block:: bash

   python -c "
   import json
   t = open('docs/searchindex.js', encoding='utf-8').read()
   d = json.loads(t[t.index('(') + 1:t.rindex(')')])
   print('科技论文写作' in d['terms'])
   "

查浏览器里能不能搜出结果，仍然用无头浏览器把渲染结果 dump 回来：

.. code-block:: bash

   msedge --headless --disable-gpu --virtual-time-budget=15000 \
     --dump-dom "file:///<站点目录>/search.html?q=安装"

在 dump 出来的 HTML 里看 ``<ul class="search">`` 中有几个 ``<li>``，或者干脆在 URL 里带上 ``?q=`` 后截图看。本站修复前后的对比：

.. list-table::
   :header-rows: 1
   :widths: 30 22 22

   * - 查询
     - 修复前
     - 修复后
   * - ``科技论文写作``
     - 0 条
     - 5 条
   * - ``交叉编译``
     - 0 条
     - 2 条
   * - ``安装``
     - 卡在「正在搜索中」
     - 16 条
   * - ``table``
     - 0 条
     - 2 条

小结
--------

- 搜索整个瘫掉，是因为 Sphinx 9.1.0 给中文搜索生成了一个引用未定义变量 ``ChineseStemmer`` 的 JS 文件。**先看浏览器控制台的报错**，不要在配置里反复猜。
- 修法是注册一个自定义中文搜索类，覆盖 ``'zh'`` 注册项。
- 搜索「能用」和「好用」是两件事。查询串在浏览器端不会被切成中文词，所以要用自定义词典把常用的词组变成索引里的独立词条。
- 排错时先排除假象：静态资源的 200、查询串、线上的 403、以及\ **用错解释器**\ 得出的「包没装」。
