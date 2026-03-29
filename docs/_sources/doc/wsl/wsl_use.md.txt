# 在 VSCode 上使用 WSL2

## 安装微软大战代码 :-)

首先你需要安装VSCode，在安装过程中 `选择附加任务` 中请勾选以下勾选框

- 将"通过Code打开”操作添加到Windows资源管理器文件上下文菜单
- 将“通过Code 打开″操作添加到Windows资源管理器自录上下文菜单
- 将Code注册为受支持的文件类型的编辑器
- 添加到PATH (重启后生效)

下一步就是安装WSL插件，通过远程资源管理器连接上你的WSL

## 9. 在 VSCode 中通过 WSL 工作

- 安装 VSCode 的 Remote - WSL 扩展。
- 打开命令面板（Ctrl+Shift+P），选择 "Remote-WSL: New Window"。
- 在 WSL 窗口中打开要编辑的项目文件夹。
- 在 VSCode 中打开终端即可运行 Linux 命令。

注意：

- Linux 下不能直接运行 Windows 的 `.exe`（例如 `arm-none-eabi-gcc.exe`），请在 WSL 环境中使用对应的 Linux 工具链。
- 在 VS Code 的工具链/扩展配置中，确保选择的是 WSL 内的工具而非 Windows 本地的工具链。


## WSL文件路径相关

建议在/home文件夹创建文件目录

/mnt/目录下对应的是Windows的C盘、D盘...

也就是说可以通过该目录访问你Winodws内的文件，执行构建操作。

Linux上使用构建工具比win平台效率更高，配置环境**更简单**！更**不容易出错**！


