# github pages

##  环境要求

debian系列:

```bash
sudo apt update
sudo apt install python3 python3-pip
pip install -r requirements.txt
```

archlinux安装相关依赖(sphinx被自动安装):

```bash
sudo pacman -Sy
sudo pacman -S yay python
yay -S python-sphinx-markdown-tables python-sphinx-copybutton 
# yay -S python-sphinx_rtd_theme 
# yay -S shibuya-bin
yay -S sphinx-book-theme

```
