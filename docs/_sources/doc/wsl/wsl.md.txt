# 在 Windows 上使用 WSL（以 Arch Linux 为例）

下面是快速上手步骤，包含常用命令与注意事项。

## 1. 安装 WSL

在 PowerShell（以管理员运行）中执行：

```powershell
wsl
```

## 2. 安装 Linux 发行版

- 列出可用发行版：

```powershell
wsl --list --online
```

- 安装 Arch Linux（示例）：

```powershell
wsl --install archlinux
```

## 3. （可选）设置默认发行版

```powershell
wsl --set-default <distribution name>
```

## 4. 启动已安装的发行版

```powershell
wsl
```

启动后会进入 Linux 终端（默认 shell）。

## 5. 更新发行版并安装软件包（Arch 示例）

更新软件包列表并升级系统：

```bash
pacman -Syu
```

安装常用工具：

```bash
pacman -S nano reflector
```

## 6. 更新镜像源（提高下载速度）

例如使用 reflector 选择中国的快速镜像并保存：

```bash
reflector --country China --latest 10 --sort rate --save /etc/pacman.d/mirrorlist
```

## 7. 添加 archlinuxcn 源（可选）

参考清华镜像帮助页面：

https://mirrors.tuna.tsinghua.edu.cn/help/archlinuxcn/

## 8. 安装需要的开发包

通用安装命令：

```bash
pacman -S <package-name>
```

示例（嵌入式交叉编译工具链与常见开发工具）：

```bash
pacman -S arm-none-eabi-gcc arm-none-eabi-newlib arm-none-eabi-gdb cmake ninja git make gcc python
```

根据项目需要选择并安装其他包。

## 9. 在 VS Code 中通过 WSL 工作

- 安装 VS Code 的 Remote - WSL 扩展。
- 打开命令面板（Ctrl+Shift+P），选择 "Remote-WSL: New Window"。
- 在 WSL 窗口中打开要编辑的项目文件夹。
- 在 VS Code 中打开终端即可运行 Linux 命令。

注意：

- Linux 下不能直接运行 Windows 的 `.exe`（例如 `arm-none-eabi-gcc.exe`），请在 WSL 环境中使用对应的 Linux 工具链。
- 在 VS Code 的工具链/扩展配置中，确保选择的是 WSL 内的工具而非 Windows 本地的工具链。

---

如果你希望我把文档改为加入更多场景（如 WSL2 设置、GUI 支持或系统备份），我可以继续扩展相关内容。 