# 项目长期记忆：GitHubPages（Sphinx 随记文档站）

站点内容：嵌入式 / 开发环境 / 电赛 / 科技论文写作等中文技术笔记。
线上：https://www.cad.qzz.io （GitHub Pages，产物在 `docs/`）、https://def.qzz.io （Read the Docs）。

## 目录与构建

- 源码在 `sphinx/`，构建产物在 `docs/`（GitHub Pages 直接吃 `docs/`）。
- 构建链：`make -C sphinx html` → `cp -r sphinx/_build/html/* ./docs/` → `python strip_query_strings.py ./docs`
  - **最后一步必须跑**：`strip_query_strings.py` 去掉 Sphinx 生成的 `?v=<hash>` 缓存串，否则 GitHub Pages 上 CSS/JS 404。校验：`grep -rlo "?v=[0-9a-f]" docs --include=*.html | wc -l` 应为 0。**这一步必须真跑**——曾出现过脚本报告 `30/30 modified` 但改动没落盘、查询串仍在的情况，重跑一次即正常；凡是脚本自称改了多少个文件，都以 grep 计数为准。
  - `build.sh` / `build.ps1` 里的 `make clean` 与 `rm -rf ./docs/*` 会触发沙箱批量删除拦截，**不要照跑**；直接增量 `make html` + `cp -r` 覆盖即可。
  - 还需保证 `docs/.nojekyll` 与 `docs/CNAME` 存在。
- `conf.py`：`extensions = ['recommonmark','sphinx_markdown_tables','sphinx_copybutton']`，`source_suffix = {'.rst':'restructuredtext', '.md':'markdown'}`，主题 `sphinx_rtd_theme`，`language='zh_CN'`，`html_static_path=['_static']`。
- 每个 doc 子目录有 `index.rst`（含 `.. _label:`、标题、`.. toctree::`），正文可用 `.md`。
- **markdown 里不能写 RST 指令**（recommonmark 不认 `.. note::`，也不认 ```eval_rst 围栏块，后者还会报 Pygments lexer 警告）。想用主题的提示框必须写 `.rst`；markdown 只能用引用块 `> **备注**` 代替。markdown 中也不要写 toctree——toctree 统一放在该目录的 `index.rst` 里。

## 中文排版硬规则（踩过坑）

1. **RST 里中文加粗**必须用转义空白做边界：`\ **加粗**\ `。直接写 `**加粗**` 贴中文会配对错乱、漏出字面星号。详见同日工作日志。
2. **RST 等宽字面量**用双反引号 ` ``x`` `；单反引号是 title-reference，渲染成斜体 `<cite>`。
3. **Markdown（CommonMark）里 `**…**` 的闭合号后面不能紧跟汉字**（如 `**偶数行（…）**设置`），否则不闭合。把粗体范围收窄到 `**偶数行**` 即可。
4. **Markdown 表格必须顶格**、前后留空行——缩进在列表项里 recommonmark 不解析，会退化成普通段落。
5. **CJK 标题下划线**：docutils 按双宽计字符，N 个汉字需要 ≥2N 个 `=`。
6. **`.. toctree::` 必须放在第一个章节标题之前**。RST directive 归属于「最近一个在它之前的章节标题」，插了新章节在 toctree 前面会让整棵目录树被吞进那一节，侧栏层级全错。
7. **`.. toctree::` 的选项块与条目之间必须有空行**：
   ```rst
   .. toctree::
       :maxdepth: 1

       prepare
       lab1
   ```
   少了那个空行，docutils 会把 `prepare`/`lab1` 当成选项去解析，报 `ERROR: Error in "toctree" directive: invalid option block.`，并且**整棵 toctree 被静默丢弃** → 该目录下所有文档报 `WARNING: document isn't included in any toctree`，侧栏只剩文档标题、层级全平。排查口诀：只要看到 `toc.not_included`，先查 toctree 选项块后的空行。
8. **验证 toctree 是否真的生效**：`make -C sphinx html` 后 grep `invalid option block` 应为空；再检查产物里 `<h2>`/`<section>` 的兄弟关系，**不要**用「toctree 是否在第一个 `<section>` 之前」判断——文档标题本身就会生成一层 `<section>`。

## 文档写作约定（用户明确要求）

- **不要出现评价/对比「参考答案」的话**（如「参考答案踩了坑」「参考答案里用的是…」）。要讲的知识点直接陈述，不归属到参考答案。纯评价性的句子直接删。
- **不要写「目标效果 / 期望输出」预览块**——每道题下面已有编译结果图，重复描述是冗余。题目结构固定为：`**题目**`（+「要求：」）→ `**答案**`（源码）→ `**编译结果**`（渲染图）→ `**说明**`。
- 配图用「实际编译渲染的结果图」，编译环境标注 TeX Live 2026 + XeLaTeX。
- 视觉类产出交付前先用 Edge headless 截图自查。

## 相关脚本与环境

- 实验题配图生成：`E:\tmp\texbuild\build_images.py`（切片参考答案 .tex → 逐题 xelatex 编译 → 裁剪 PNG → `sphinx/_static/techpapers/`）。
  - 需设 `FONTCONFIG_FILE` / `FONTCONFIG_PATH` 指向 TeX Live 的 fonts conf，否则 Fontconfig/Kpathsea 报错。
  - 单题重跑：`python build_images.py <关键字>`。脚本内**不要用 `shutil.rmtree`**（会触发沙箱批量删除拦截而中途静默中断），改为复用目录覆盖 + mtime 校验。
- venv：`C:\Users\28035\.workbuddy\binaries\python\envs\default`（已装 `pymupdf`）。
- Edge headless 截图：`"/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --window-size=W,H --screenshot="<绝对路径>.png" "file:///<绝对路径>"`，`--screenshot=` 必须是绝对路径。

## 遗留

- `sphinx/doc/JLC/hardware.md` 仍是 0 字节空文件，PCB 设计指南待写（勿覆盖用户可能已填的内容）。
