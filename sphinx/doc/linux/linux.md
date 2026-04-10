# Linux 相关

## ArchLinux AUR源下载问题

一般下载卡住都是因为

```bash
git clone <rep>.git
```

没有成功把仓库拉下来，**一种情况**是某些aur软件autobuild版本滞后于实际仓库，即文件不存在拉不下来；

**大部分情况**是魔法出了问题，一旦存在特殊断流(被reset)，git clone操作会被立即打断，这对网络稳定性有较高的要求.可以考虑浏览器手动下载，将文件放置在yay的缓存目录中`/home/用户名/.cache/yay/<packname>`，然后手动在终端运行

```bash
makepkg
```

等待打包完成后，手动安装包

```bash
sudo pacman -U <package>
```

## Timeshift恢复Btrfs后出问题

可以参考[archlinux 简明指南](https://arch.icekylin.online/guide/advanced/system-ctl#%E7%B3%BB%E7%BB%9F%E5%BF%AB%E7%85%A7-%E5%A4%87%E4%BB%BD-%E4%B8%8E%E6%96%87%E4%BB%B6%E4%BC%A0%E8%BE%93)，文章中提到:

Timeshift 恢复 Btrfs 快照时，可能出现由于子卷 ID 变更导致无法挂载目录而无法进入系统.

使用 vim / nano 编辑器修改 /etc/fstab 文件

```bash
sudo vim /etc/fstab
# or
sudo nano /etc/fstab
```

删除 / 和 /home 条目中最后的 subvolid=xxx，也可以通过以下命令查看正确的 ID，手动更正 subvolid:

```bash
sudo btrfs sub list -u /
```

>## 终端中文表现为乱码

首先需要编辑`/etc/locale.gen`文件

```bash
sudo nano /etc/locale.gen
```

将 en_US.UTF-8和zh_CN.UTF-8取消注释,在终端输入

```bash
locale-gen
```

生成配置文件后还需要安装合适的中文字体，如`noto-sans-cjk`

基本上能解决大部分显示异常的问题
