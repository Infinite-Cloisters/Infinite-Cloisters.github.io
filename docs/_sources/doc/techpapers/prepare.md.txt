# 环境准备：宏包与文档从哪里来

CTAN（The Comprehensive TeX Archive Network）是几乎所有 TeX 排版系统相关材料的汇集地，编译引擎、宏包、字体的源代码与说明文档都在上面。绝大多数 LaTeX 宏包会先上传到 CTAN 核心站点，再同步到全球各镜像——也就是说，你缺的宏包、想查的宏包手册，基本都能在这里找到。

CTAN 主站在国外，国内直连下载很慢。建议把 TeX 发行版的下载源换成清华 TUNA 镜像，配置方法见清华镜像站的帮助页：

[CTAN 镜像使用帮助 · 清华大学开源软件镜像站](https://mirrors.tuna.tsinghua.edu.cn/help/CTAN/)

这一页值得完整读一遍。下面按原页面的结构把要点整理一份，方便对照查阅。

> **备注**
>
> 本节内容整理自清华大学开源软件镜像站的 CTAN 帮助页，实际命令与下载地址请以原页面为准。

## 安装方法

TeX Live 发行版的常见安装方法可以参考下面这份中文文档：

[install-latex-guide-zh-cn.pdf](https://mirrors.tuna.tsinghua.edu.cn/CTAN/info/install-latex-guide-zh-cn/install-latex-guide-zh-cn.pdf)

除每年更新的完整版 ISO 镜像以外，CTAN 镜像中也包含**在线安装器**。这种方法可以使安装的所有宏包均为最新版本，但受网络连接状况影响较大。操作方法为（很可能需要管理员权限）。

### 1. 下载并解压缩 install-tl.zip

下载地址：

```
https://mirrors.tuna.tsinghua.edu.cn/CTAN/systems/texlive/tlnet/install-tl.zip
```

### 2. 运行安装器

Windows 下双击运行其中的 `install-tl.bat`。如果有图形化界面，可以在进入安装器前的右下角按钮指定使用镜像源。Linux 下使用如下命令：

```
perl install-tl --repository https://mirrors.tuna.tsinghua.edu.cn/CTAN/systems/texlive/tlnet
```

## 切换镜像

TeX Live 使用的 CTAN 镜像源可以从内置的包管理器 `tlmgr` 更改（很可能需要管理员权限）。在命令行中执行：

```
tlmgr option repository https://mirrors.tuna.tsinghua.edu.cn/CTAN/systems/texlive/tlnet
```

即可永久更改镜像源。如果只需要临时切换，可以用如下命令：

```
tlmgr update --all --repository https://mirrors.tuna.tsinghua.edu.cn/CTAN/systems/texlive/tlnet
```

其中的 `update --all` 指令可根据需要修改。

## MiKTeX

MiKTeX 发行版的特点在于仅安装用户需要的宏包，节省了磁盘空间占用，但在部分实现细节上与 TeX Live 有所出入。该发行版支持 Windows、Linux 和 macOS。

MiKTeX 仅提供 Windows 和 macOS 的独立安装包，在 Linux 下的安装请参考官方文档。使用的 CTAN 镜像源可以从内置的 MiKTeX Console 图形化应用程序切换，也可以使用如下命令：

```
mpm --set-repository=https://mirrors.tuna.tsinghua.edu.cn/CTAN/systems/win32/miktex/tm/packages/
```

## 什么时候会用到它

编译时若报 `File 'xxx.sty' not found`，说明本地缺这个宏包，先 `tlmgr install xxx` 补装；如果下载卡住或超时，多半是镜像源没换，回到上面第一步。
