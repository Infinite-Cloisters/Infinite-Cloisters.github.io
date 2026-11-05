# SSH 远程连接与免密登录

整理了 SSH 连接服务器、生成公钥、配置免密登录，以及日常常用的 SSH / SCP 命令。

## 1. 生成公钥

在本地终端（Windows PowerShell / Linux / macOS）执行：

```bash
# 推荐 ed25519: 更安全、密钥更短
ssh-keygen -t ed25519 -C "your_email@example.com"

# 需要兼容老设备时可用 RSA (至少 4096 位)
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# 当然更简单的直接输入也可以
ssh-keygen

```

一路回车即可，默认生成于 `~/.ssh/`：

- 私钥 `id_ed25519`：务必保密，不要外传或提交到仓库
- 公钥 `id_ed25519.pub`：可公开，用于上传到服务器

`ssh-keygen` 会询问 passphrase（密钥口令），留空即为无口令（纯免密），输入则每次使用私钥需先解口令。

## 2. 上传公钥到服务器

下面这段 PowerShell 脚本用于把本地公钥追加到远端 `authorized_keys`，保持原样不要改动：

将公钥上传到服务器脚本如下：
```powershell
[CmdletBinding(DefaultParameterSetName = "DeployMode")]
param(
    [Parameter(Mandatory = $true, ParameterSetName = "DeployMode", Position = 0)]
    [Alias("r")]
    [string]$RemoteHost,

    [Parameter(Mandatory = $true, ParameterSetName = "DeployMode", Position = 1)]
    [Alias("u")]
    [string]$User,

    [Parameter(ParameterSetName = "DeployMode")]
    [ValidateRange(1, 65535)]
    [Alias("p")]
    [int]$Port = 22,

    [Parameter(Mandatory = $true, ParameterSetName = "HelpMode")]
    [Alias("h")]
    [switch]$Help
)

$scriptName = Split-Path -Leaf $PSCommandPath

function Show-Help {
    Write-Host @"
SSH 公钥部署工具 v2.1

使用方法:
  $scriptName <主机> <用户> [-Port <端口>]
  $scriptName -RemoteHost <主机> -User <用户> [-Port <端口>]
  $scriptName -h

参数:
  -RemoteHost   目标服务器 IP/域名 (部署模式必需)
  -User         目标服务器用户名   (部署模式必需)
  -Port         SSH 端口 (默认: 22)
  -h, -Help     显示帮助信息

示例:
  .\$scriptName REDACTED_IP xjq -Port 23
  .\$scriptName -RemoteHost 10.0.0.5 -User webuser -Port 2222

注意事项:
  1. 本地需已生成密钥对: ssh-keygen -t ed25519
  2. 首次连接自动接受主机指纹 (StrictHostKeyChecking=accept-new)
  3. 仍需在最后一步输入一次远端密码 (公钥尚未生效时)
"@
    exit 0
}

if ($Help) { Show-Help }

# --- 环境检查 -------------------------------------------------------------
if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) {
    Write-Host "[错误] 未找到 ssh 客户端, 请先安装 OpenSSH Client" -ForegroundColor Red
    exit 1
}

$sshDir = Join-Path $env:USERPROFILE ".ssh"
if (-not (Test-Path -LiteralPath $sshDir)) {
    Write-Host "[错误] SSH 目录不存在: $sshDir  请先执行 ssh-keygen -t ed25519" -ForegroundColor Red
    exit 1
}

# --- 公钥选择 -------------------------------------------------------------
$pubKeys = @(Get-ChildItem -LiteralPath $sshDir -Filter "*.pub" -File -ErrorAction SilentlyContinue)
if ($pubKeys.Count -eq 0) {
    Write-Host "[错误] 未找到任何 .pub 公钥文件于 $sshDir" -ForegroundColor Red
    exit 1
}

if ($pubKeys.Count -gt 1) {
    Write-Host "`n检测到多个公钥文件:"
    for ($i = 0; $i -lt $pubKeys.Count; $i++) {
        Write-Host ("  [{0}] {1}" -f ($i + 1), $pubKeys[$i].Name)
    }
    do {
        $selected = Read-Host "`n请选择公钥编号 (1-$($pubKeys.Count))"
    } while ($selected -notmatch '^\d+$' -or [int]$selected -lt 1 -or [int]$selected -gt $pubKeys.Count)
    $keyFile = $pubKeys[[int]$selected - 1].FullName
} else {
    $keyFile = $pubKeys[0].FullName
    Write-Host "`n使用唯一公钥: $($pubKeys[0].Name)" -ForegroundColor Cyan
}

# --- 读取公钥 (去掉换行, 保证末尾一个 \n) ---------------------------------
try {
    $keyLine = ((Get-Content -LiteralPath $keyFile -Raw -ErrorAction Stop) -replace '\r?\n', ' ').Trim()
} catch {
    Write-Host "[错误] 读取公钥文件失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
if ([string]::IsNullOrWhiteSpace($keyLine)) {
    Write-Host "[错误] 公钥文件内容为空: $keyFile" -ForegroundColor Red
    exit 1
}

# --- 部署 ---------------------------------------------------------------
$target = "$User@$RemoteHost"
$remoteCmd = 'mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'

# 保证输出为 UTF-8 且不带 BOM, 避免管道编码问题
$OutputEncoding = New-Object System.Text.UTF8Encoding($false)

Write-Host "`n正在部署公钥到 $target (端口 $Port) ..." -ForegroundColor Cyan
try {
    $keyLine | & ssh -p $Port -o StrictHostKeyChecking=accept-new $target $remoteCmd
    if ($LASTEXITCODE -ne 0) {
        throw "ssh 上传失败, 退出码 $LASTEXITCODE (可能是密码错误或端口不通)"
    }
} catch {
    Write-Host "`n[错误] 部署失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# --- 验证 (BatchMode: 不再询问密码) --------------------------------------
& ssh -p $Port -o BatchMode=yes -o StrictHostKeyChecking=accept-new $target "echo OK" 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[成功] 公钥已部署, 免密登录生效: ssh -p $Port $target" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n[警告] 公钥已写入, 但免密验证未通过 (退出码 $LASTEXITCODE)" -ForegroundColor Yellow
    Write-Host "请检查远端 ~/.ssh 权限、sshd 的 PubkeyAuthentication 与 AuthorizedKeysFile 配置" -ForegroundColor Yellow
    exit 2
}

```

## 3. 验证免密登录

上传成功后，直接连接服务器，若不再提示输入密码即表示免密生效：

```bash
ssh -p 22 user@host
```

如果仍要密码，检查远端文件权限（不正确时 sshd 会拒绝使用公钥）：

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

并确认 `/etc/ssh/sshd_config` 中：

```
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
```

修改配置后需重启 sshd：

```bash
# Linux
sudo systemctl restart sshd
```

## 4. SSH 连接服务器命令

基本语法：

```bash
ssh [选项] [user@]host[:port]
```

常用形式：

```bash
# 最简: 默认端口 22, 使用当前本地用户名
ssh host

# 指定用户与端口
ssh -p 2222 user@host

# 首次连接自动接受主机指纹 (避免交互确认)
ssh -o StrictHostKeyChecking=accept-new user@host

# 指定私钥文件
ssh -i ~/.ssh/id_ed25519 -p 22 user@host

# 本地端口转发 (本机 8080 映射到远端 80)
ssh -L 8080:localhost:80 user@host

# 远程执行单条命令 (常用于脚本/自动化)
ssh user@host "nvidia-smi"
```

## 5. 常用命令

### 文件传输（SCP）

```bash
# 本地 → 远端
scp -P 22 local_file.txt user@host:/path/to/dest/

# 远端 → 本地
scp -P 22 user@host:/path/to/remote_file.txt ./

# 递归传输整个目录
scp -r -P 22 ./myfolder user@host:/path/to/dest/
```

> 注意：scp 用大写 `-P` 指定端口，而 ssh 用小写 `-p`，两者容易混淆。

### 其他常用

```bash
# 查看 ssh 客户端版本
ssh -V

# 详细诊断 (排查连接失败)
ssh -v user@host

# 连接复用, 加速频繁连接 (ControlMaster)
ssh -o ControlMaster=auto -o ControlPath=~/.ssh/%r@%h-%p -o ControlPersist=600 user@host
```

### 配置别名（省去重复输入）

编辑本地 `~/.ssh/config`：

```
Host myserver
    HostName <YOUR_IP>
    User <USER_NAME>
    Port <PORT>
    IdentityFile ~/.ssh/id_ed25519
```

配置后只需 `ssh myserver` 即可一键连接。
