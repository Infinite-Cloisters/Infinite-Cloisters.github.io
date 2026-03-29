# GIT工具

## 基本使用指令

```powershell
# 设置你的基本信息
git config --global user.name "yourname"
git config --global user.email "you@example.com"
# 初始化仓库
git init
# 添加文件
git add *
# 提交本地
git commit -m "评论"
# 添加远程源
git remote add origin <url>
# 提交到远程，缺省则是默认使用当前本地分支名
# git push <远程主机名> <本地分支名>:<远程分支名>
git push

# 有些鉴权方式比如说GUI支持账户+密码，纯终端一般需要你手动创建auth token使用它进行仓库管理
```

初学者可以配合GitHub Desktop或者VSCode进行辅助使用，此外**一定要合理使用`.gitignore`减少仓库大小**

诸如gitee相比GitHub更快（在中国），使用的流程基本上都差不多。

## 分支管理

分支用于隔离不同功能或修复任务，避免直接在主分支上修改。

```powershell
# 查看本地分支（* 表示当前所在分支）
git branch
# 查看本地+远程分支
git branch -a
# 创建新分支
git branch feature/login
# 切换分支
git switch feature/login# 老命令也可以：git checkout feature/login
# 创建并切换到新分支
git switch -c feature/login# 老命令也可以：git checkout -b feature/login
# 开发完成后切回主分支
git switch main
# 将功能分支合并到当前分支
git merge feature/login
# 删除本地分支（已经合并）
git branch -d feature/login
# 强制删除本地分支（未合并也删除，谨慎）
git branch -D feature/login
```

### 远程分支常见操作

```powershell
# 首次推送分支并建立上游追踪关系（后续可直接 git push）
git push -u origin feature/login
# 拉取远程更新（抓取并合并当前分支）
git pull
# 仅抓取远程更新，不自动合并
git fetch
# 删除远程分支
git push origin --delete feature/login
```

### 典型协作流程

1. 从 `main` 拉最新代码：`git switch main` + `git pull`
2. 创建任务分支：`git switch -c feature/xxx`
3. 本地开发并多次提交：`git add` + `git commit`
4. 推送到远程：`git push -u origin feature/xxx`
5. 发起 PR/MR，评审通过后合并到 `main`
6. 删除无用分支（本地和远程）

### 合并冲突处理

当 `git merge` 或 `git pull` 出现冲突时：

1. 用编辑器打开冲突文件，处理 `<<<<<<<` `=======` `>>>>>>>` 标记
2. 标记为已解决：`git add <冲突文件>`
3. 完成合并提交：`git commit`

如果你在 rebase 过程中冲突：

```powershell
# 解决冲突并 add 之后继续
git rebase --continue
# 放弃本次 rebase
git rebase --abort
```

### 分支命名建议

- `feature/xxx`：新功能
- `fix/xxx`：问题修复
- `hotfix/xxx`：紧急修复
- `docs/xxx`：文档更新

保持分支短生命周期、小步提交，可以显著降低冲突概率。

## 使用 git-filter-repo (Python包) 清理 .git

适用场景：误提交了大文件、密钥、敏感配置，或者历史里有不需要保留的目录。

> 注意：`git filter-repo` 会重写提交历史。已经推送到远程的仓库需要强制推送，并通知所有协作者重新同步。

### 1. 安装工具

```powershell
python -m pip install git-filter-repo
# 验证
git filter-repo --help
```

### 2. 先做备份（建议）

```powershell
# 推荐做一个镜像备份仓库
git clone --mirror <repo-url> repo-backup.git
```

### 3. 常见使用

```powershell
# 删除历史中的某个文件（例如密钥）
git filter-repo --path .env --invert-paths
# 删除历史中的某个目录
git filter-repo --path secrets/ --invert-paths
# 删除历史中所有 .zip 文件
git filter-repo --path-glob *.zip --invert-paths
# 删除历史记录中所有大于 10M 的文件 （其实这个比较常用？）
git filter-repo --strip-blobs-bigger-than 10M --force
# 批量替换敏感字符串（先准备 replacements.txt）
# 格式示例：
# old_token==>REDACTED_TOKEN
git filter-repo --replace-text replacements.txt
```

### 4. 清理后检查（可选）

```powershell
# 查看历史是否仍有目标文件
git log --all -- .env
# 查看仓库对象体积情况
git count-objects -vH
```

### 5. 推送到远程（重写历史后）

```powershell
# 注意一下清理可能会干掉远程分支，建议先查看一下当前远程分支，如果分支没有了需要重新添加远程仓库
git remote -v
# 强制推送当前分支
git push origin --force --all
# 如有标签也一起更新
git push origin --force --tags
```

### 6. 协作者需要做的事

重写历史后，协作者本地旧历史会与远程冲突。最稳妥方式是：

1. 备份本地未提交改动
2. 重新克隆仓库
3. 或者删除本地分支后基于新远程分支重建
