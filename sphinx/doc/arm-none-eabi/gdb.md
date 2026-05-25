# 使用 arm-none-eabi-gdb 和 probe-rs 实现程序调试

本文档介绍在嵌入式开发中结合 `arm-none-eabi-gdb` 与 `probe-rs` 工具链进行调试的常见流程、安装提示和常用命令示例.大部分玩嵌入式的同学用的是Windows且可能不太愿意折腾WSL，所以本文档基于Windows平台.

参考文档:[probe-rs 官方文档](https://probe.rs/docs/)

## 先决条件

- 已编译带符号的 ELF 文件(通常为 debug 构建):例如 `target/<target>/debug/your-project`.
- 已安装适当的交叉工具链:`arm-none-eabi-gdb`(来自 GNU Arm Embedded Toolchain 或通过包管理器).

## 安装 probe-rs(参考)或者pyocd

安装 probe-rs (Windows)

```powershell
irm https://github.com/probe-rs/probe-rs/releases/latest/download/probe-rs-tools-installer.ps1 | iex
# 如果用rust可以使用
cargo install probe-rs cargo-flash cargo-embed
# pyocd系列，因为我个人不使用，所以不做介绍
pip install pyocd
```

安装完毕后应该能使用三个命令:

- probe-rs
- cargo-flash
- cargo-embed

接着建议安装VSCode probe-rs 拓展, <font color="green">即使没有安装成功</font>它也会询问是否安装probe-rs.

## 调试流程(概览)

### 1. 构建带符号的固件

- Rust:`cargo build --target <target>`(生成 ELF)
- C/C++:(正常我们是这个)使用交叉编译器生成 ELF.

### 2. 使用传统方式

启动一个 GDB server(由 probe-rs 提供)，使目标硬件通过 probe 与主机建立通信.通常 probe-rs 会在某个端口(例如 3333)提供 GDB 协议服务.

- 示例(启动 gdb server 的方式可能随工具不同而异):

```powershell
probe-rs gdb --chip <chip> <path/to/your.elf>
```

该命令会打开与 probe 的连接，并启动一个可供 `arm-none-eabi-gdb` 连接的 GDB server.请参考你安装的 probe-rs 工具的具体子命令与选项.

如果工具没有相关芯片可以使用`--chip-description-path`选项替换`--chip`，描述文件可以通过`target-gen`转换标准cmsis的.pack文件获得

### 2. 使用新版方式(VSCode官方插件只支持这个，更友好)

我没有在Clion中尝试过这个方法，但是Vscode中调试Py32是成功的，此外probe-rs不能用cortex-debug.

[具体操作办法参考官方](https://probe.rs/docs/tools/debugger/)

简而言之，就是配置好`launch.json`就能实现调试了，断点、单步读取变量都没有太大问题。

### 3. 在主机端打开 `arm-none-eabi-gdb` 并加载 ELF(以下都是传统gdb方案)

```powershell
arm-none-eabi-gdb <path/to/your.elf>
```

### 4. 在 gdb 内连接到远端 GDB server

```powershell
(gdb) target remote :1337
```

### 5. 初始化目标(可选)

```powershell
(gdb) monitor reset halt
# OR
(gdb) monitor reset init
```

### 6. 加载程序到目标(如果尚未由 server 自动加载)

```powershell
(gdb) load
```

### 7. 设置断点并运行

```powershell
(gdb) break main
(gdb) continue
```

### 8. 使用单步、查看寄存器、内存等进行调试，结束后断开连接

```powershell
(gdb) monitor halt
(gdb) detach
```

使用Clion中自定义gdb服务器可以简化每次繁琐的命令输入，自行查阅相关资料配置(也就是你先输入一边预设，以后点击按钮就是Clion帮你敲命令)

## 常用 gdb 命令速查

- 启动与连接
  - `arm-none-eabi-gdb <path/to.elf>`:以符号文件启动 gdb
  - `target remote :3333`:连接到本地 3333 端口的 GDB server

- 断点与运行
  - `break SYMBOL` / `b SYMBOL`:在函数或符号处设断点
  - `break *0xADDR`:在绝对地址设断点
  - `delete`:删除断点
  - `continue` / `c`:继续执行
  - `step` / `s`:单步进入(会进入函数)
  - `next` / `n`:单步但不进入函数
  - `finish`:执行至当前函数返回

- 程序加载与控制
  - `load`:将 ELF 加载到目标(在远端调试时常用)
  - `monitor reset` / `monitor reset halt`:通过 gdb server 复位目标并暂停(server 实现支持时可用)
  - `monitor halt` / `monitor resume`:通过 server 控制目标运行状态

- 查看状态
  - `info registers`:显示寄存器
  - `info breakpoints`:列出断点
  - `info threads`:列出线程(若支持)
  - `thread apply all bt`:在所有线程上打印回溯

- 读取与写入内存/变量
  - `x/<n><fmt> ADDRESS`:以指定格式显示内存(例 `x/16xb 0x20000000`)
  - `print VAR` / `p VAR`:打印变量(包含结构的字段)
  - `p/x $pc`:以十六进制打印程序计数器
  - `set VAR = VALUE`:修改变量(在允许的情况下)
  - `set $pc = 0xADDR`:修改寄存器

- 其它有用命令
  - `layout asm`, `layout regs`:TUI 模式下显示汇编/寄存器(需启用 TUI)
  - `maint print symbols`:调试符号信息(维护用途)

## 常见问题与调试技巧

- 如果无法连接:确认 probe 已插好、电源正常，并且 probe-rs 的 gdb server 正在运行且监听端口(默认 3333).
- 符号不匹配或行号不正确:确保 gdb 中加载的 ELF 是用相同版本和构建选项生成的带符号二进制.
- 硬件断点耗尽:部分芯片硬件断点数目有限，使用软件断点或将断点移到更集中位置.
- 使用 `monitor` 前缀命令可以通过 gdb server 发送原始控制命令(server 支持的命令集不同，请参阅对应实现文档).

## 参考

- probe-rs 官方仓库与文档(查看最新的子命令与使用示例)
- GNU Arm Embedded Toolchain 文档(关于 `arm-none-eabi-gdb` 的使用)
