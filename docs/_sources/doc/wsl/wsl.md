# 在 Windows 上使用 WSL(以 Arch Linux 为例)

下面是快速上手步骤，包含常用命令与注意事项.

## 1. 安装 WSL

在 PowerShell(以管理员运行)中执行：

```powershell
wsl
```

## 2. 安装 Linux 发行版

- 列出可用发行版：

```powershell
wsl --list --online
```

- 安装 Arch Linux(示例)：

```powershell
wsl --install archlinux
```

## 3. (可选)设置默认发行版

```powershell
wsl --set-default <distribution name>
```

## 4. 启动已安装的发行版

```powershell
wsl
```

启动后会进入 Linux 终端(默认 shell).

## 5. 更新发行版并安装软件包(Arch 示例)

更新软件包列表并升级系统：

```bash
pacman -Syu
```

安装常用工具：

```bash
pacman -S nano reflector
```

## 6. 更新镜像源(提高下载速度)

例如使用 reflector 选择中国的快速镜像并保存：

```bash
reflector --country China --latest 10 --sort rate --save /etc/pacman.d/mirrorlist
```

## 7. 添加 archlinuxcn 源(可选)

参考清华镜像帮助页面：

https://mirrors.tuna.tsinghua.edu.cn/help/archlinuxcn/

## 8. 安装需要的开发包

通用安装命令：

```bash
pacman -S <package-name>
```

示例(嵌入式交叉编译工具链与常见开发工具)：

```bash
pacman -S arm-none-eabi-gcc arm-none-eabi-newlib arm-none-eabi-gdb cmake ninja git make gcc python
```

根据项目需要选择并安装其他包.

如果终端中文表现**异常**请参考Linux踩坑记录