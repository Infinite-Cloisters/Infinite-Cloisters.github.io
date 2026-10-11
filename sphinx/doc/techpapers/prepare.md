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

## 安装失败排查

安装器中途报错退出、下载或解压阶段卡死、装完之后 `xelatex` 在某个终端里莫名其妙找不到——这类问题多数不是 TeX Live 本身的问题，而是下面两类环境因素。它们同样是 `install-latex-guide-zh-cn.pdf` 里已经指出过的：**中文用户名**，以及**终端环境被其他工具链污染**。

### 1. 系统用中文作为用户名

Windows 用户名是中文时，安装器在处理临时文件路径时可能因路径含非 ASCII 字符而出错，典型表现是安装进行到一半突然失败。指南给出的办法是给安装过程单独指定一个纯英文的临时目录：

```
mkdir C:\temp
set TEMP=C:\temp
set TMP=C:\temp
```

这三条要在同一个命令行窗口里依次执行，然后**在该窗口内**运行 `install-tl.bat`，让安装器继承改过的环境变量。换个窗口再运行就不生效了。

### 2. 终端环境被 mingw / jdk / conda / msys 污染

安装前先看一眼当前的 `PATH`：

```
echo %path:;=&echo.%
```

一是确认其中包含 `C:\Windows\system32`；二是检查有没有混进 mingw、jdk、Cygwin 相关的内容。指南的建议是：**安装期间把这些条目暂时删除**，等 TeX Live 装完之后再重新加回去，并且放到 TeX Live 自己的路径之后。

原因不难理解：conda、MSYS2、mingw、JDK 这类工具都会把自己的一整套运行时目录插到 `PATH` 的最前面。安装器和 `tlmgr` 在调用外部程序、加载 dll 时，可能优先命中这些目录里的同名文件，于是安装过程失败，或者出现「在某个终端里能用、换个终端就报错」这种看起来很玄学的结果。

指南里还顺带提到两个容易被忽略的干扰源：**2345 好压**一类压缩软件可能影响安装，建议先卸载、装完 TeX Live 后换用其他同类软件；以及**不要安装第三方安全软件**，它会拦截安装器的写入操作。

> **备注**
>
> 上面两条（中文用户名、环境变量冲突）的处理办法出自 `install-latex-guide-zh-cn.pdf` 的第 1.1 节与第 1.1.3 节，此处只是转述要点，完整上下文与后续步骤请以原文为准。

### 3. conda / MSYS：直接在自己的终端里安装

如果 conda 或 MSYS2 是你的日常主力环境，把它们的路径从 `PATH` 里删掉并不现实。这时可以换个思路：不跟它们抢 `PATH`，而是在它们各自的终端环境内部安装 TeX Live，从根上避开冲突。

例如在conda终端中:

```powershell
(Base) C:\Users\28035> <path>/install-tl.bat
```

## 什么时候会用到它

编译时若报 `File 'xxx.sty' not found`，说明本地缺这个宏包，先 `tlmgr install xxx` 补装；如果下载卡住或超时，多半是镜像源没换，回到上面第一步。
