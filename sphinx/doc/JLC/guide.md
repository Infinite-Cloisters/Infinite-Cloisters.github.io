# 开发环境与工具链选择

这篇写给第一次摸单片机、要在几天内把板子跑起来的同学。内含AI扩写内容，但我看了一下应该没有太大问题。

先说结论:**工具链不重要,能把代码烧进去、能在线打断点调试、能随时回退代码,才是真的**。

下面几套方案我都列出来,各有适用场景。如果你拿不定主意,直接照 **方案一（VSCode + EIDE + probe-rs）** 搭,跨平台、免费、不限代码大小、下载器随便换，也是电源组那边喜欢用的开放方案。

## 方案速览

| 方案 | 费用 | 平台 | 代码大小限制 | 下载器 | 上手难度 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| VSCode + EIDE + CubeMX + probe-rs | 全免费 | Win / Linux / macOS | 无 | ST-Link / J-Link / DAPLink / ... | 中 | 个人推荐,配置一次到处能用 |
| CLion + CubeMX | 学生免费 | Win / Linux / macOS | 无 | ST-Link / J-Link / DAPLink（OpenOCD） | 中 | 代码补全和重构最强 |
| STM32CubeIDE + CubeMX | 全免费 | Win / Linux / macOS | 无 | **基本只有 ST-Link 好用** | 低 | 官方一体机,开箱即用 |
| Keil MDK5 + CubeMX | 收费（有 Lite 版） | 仅 Windows | 未授权 32KB | ST-Link / J-Link / ULINK / CMSIS-DAP | 低 | 资料最多,但**联网/授权折腾** |

---

## 零、通用的第一步:STM32CubeMX

上面四套方案里,CubeMX 是共用的。它的作用只有一个:**用图形界面配好时钟树和外设,然后生成初始化代码**。

几个必须记住的点:

1. **安装路径不要有中文、不要有空格。** CubeMX 基于 Java,路径里出现中文/空格会在生成代码时各种玄学报错。
2. 需要先装 JRE/JDK,再装 CubeMX;首次使用要在线下载对应系列的 HAL 包（F1/F4/G4/H7...）。
3. **Toolchain / IDE 选项决定了你后面走哪条路**:

| 你想走的路 | Project Manager → Toolchain / IDE 选 |
| --- | --- |
| VSCode + EIDE（GCC） | `CMake/Makefile/MDK-ARM` |
| CLion | `STM32CubeIDE` |
| STM32CubeIDE | `STM32CubeIDE` |
| Keil | `MDK-ARM` |

4. **用户代码只能写在 `/* USER CODE BEGIN xxx */` 和 `/* USER CODE END xxx */` 之间**,写在外面,下次点 GENERATE CODE 就会被覆盖掉,一天白干。这句话值得背下来。
5. 建议在 Code Generator 里勾选 `Generate peripheral initialization as a pair of .c/.h files`,外设分文件,找代码好找。

---

## 一、VSCode + EIDE + STM32CubeMX + Probe-rs（我个人比较喜欢的）

如果你打算直接使用CMake完成编译，请参考["VSCode使用CMake编译STM32"](https://blog.csdn.net/qq_42839452/article/details/153870471)，这个其实就是另外一个方案中CLion帮你干的活，选择使用VSCode单纯是为了轻量（CLion软件相对较重）。

### 1.1 可能需要的软件或插件

| 组件 | 说明 |
| --- | --- |
| VSCode | **必须** |
| STM32CubeMX | **必须** 生成 CMake/Makefile 工程|
| ARM GNU Toolchain | **可选**  `bin` 目录加进 PATH 环境变量,`arm-none-eabi-gcc -v` 能出版本就 OK |
| 插件 `Embedded IDE`（EIDE） | **可选** 小白直接在在里面下载一系列工具链 |
| 插件 `STM32CubeIDE for Visual Studio Code` | **可选** CubeIDE的vscode版本，EIDE和这个二选一 |
| 插件 `C/C++` | **必须** 代码补全、跳转 |
| 插件 `CMake Tools` | **可选** 直接使用CMake进行编译 |
| 插件 `probe-rs` | **必须** 调试适配器,装完如果它找不到 probe-rs 会提示你装，如果用cubeide插件这个就不用了 |
| probe-rs CLI | **必须** 烧录 + 在线调试（打断点、看变量、看寄存器） |

如果你用`STM32CubeIDE for Visual Studio Code`，请忽略下面内容

装 probe-rs（Windows,PowerShell）:

```powershell
irm https://github.com/probe-rs/probe-rs/releases/latest/download/probe-rs-tools-installer.ps1 | iex
```

Linux / macOS 可以用 `cargo install probe-rs-tools`,或者直接去 GitHub Releases 下载。

装完验证:

```powershell
probe-rs --version
```

### 1.2 CubeMX 生成 + EIDE 手 动 导入

1. CubeMX 里 Toolchain / IDE 选 **CMAKE or Makefile**,GENERATE CODE。
2. VSCode 打开工程目录,EIDE 面板 → 新建项目 → 其他步骤参考下文。 如果是`MDK-ARM`就直接导入。
3. EIDE 里确认:工具链路径指向 `arm-none-eabi-gcc`、芯片型号选对、链接脚本指向 CubeMX 生成的 `*_FLASH.ld`。

> 具体新建项目的其他步骤**新建同名空工程（选对应芯片的 GCC 模板）,然后把 CubeMX 生成的 `Core/`、`Drivers/`、`Middlewares/`、启动文件和 `.ld` 链接进去**,再手动补 Include Paths 和宏定义（`USE_HAL_DRIVER`、`STM32F407xx` 这类）。

这种方案虽然没有CMake配合插件直接编译方便，但胜在简单、通用性好。

### 1.3 编译期最常见的三个坑

1. **FPU 没开**:带硬件浮点的芯片（F4/F7/H7/G4）默认可能是 `soft`,FreeRTOS 的 `port.c` 会报 `selected FPU does not support instruction`。到 Target Options 里把 FPU 改成 `fpv4-sp-d16`（M4）/ `fpv5-d16`（M7）。
2. **链接脚本语法错误**:CubeMX 生成的 `.ld` 偶尔会出现 `> AT> FLASH` 这类缺参数的写法,手动改成 `>RAM AT> FLASH`,`_estack` 写成 `ORIGIN(RAM) + LENGTH(RAM)`。
3. **`undefined reference`**:源文件没加全,尤其 FreeRTOS 的 `portable/GCC/ARM_CMxF` 目录和 HAL 驱动 `Src` 目录。
4. 不要随便动`-lto`,代码关键记得加`__IO`防止优化，合理使用`__attribute__和#pragma`就行函数级别优化，有些时序比较严格的利用这个可以让编译器不优化。

### 1.4 用 probe-rs 插件调试（照官方文档来）

probe-rs 的 VSCode 插件走的是微软 DAP 协议,`launch.json` 里 `type` 固定写 `probe-rs-debug`。

**关键点:它不挑语言。** 只要你有带符号的 `.elf` 和芯片名,C 工程、C++ 工程、汇编工程都能调,不是 Rust 专属。

此外，这个东西是基于rust的，理论上直接写好`.cargo`内的配置文件，就可以直接使用预设命令一键下载。

最小可用配置（改三处就能跑:芯片名、elf 路径、svd 路径）:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "probe-rs-debug",
      "request": "launch",
      "name": "probe-rs Debug",
      "cwd": "${workspaceFolder}",
      "chip": "STM32F407ZETx",
      "flashingConfig": {
        "flashingEnabled": true,
        "haltAfterReset": true,
        "formatOptions": {
          "binaryFormat": "elf"
        }
      },
      "coreConfigs": [
        {
          "coreIndex": 0,
          "programBinary": "build/YourProject.elf",
          "svdFile": "STM32F407.svd"
        }
      ],
      "consoleLogLevel": "Console"
    }
  ]
}
```

常用可选字段,按需加:

| 字段 | 作用 | 什么时候用 |
| --- | --- | --- |
| `probe` | `"VID:PID"` 或 `"VID:PID:<Serial>"` | 电脑上插了多个下载器,指定用哪个 |
| `speed` | SWD 时钟（kHz）,如 `24000` | 连接不稳定就往下调,比如 `1000` |
| `connectUnderReset` | 拉住复位线再连 | 程序把 SWD 引脚配成别的功能、或者跑飞了连不上时 |
| `wireProtocol` | `"Swd"` / `"Jtag"` | 默认 SWD |
| `allowEraseAll` | 允许整片擦除 | 芯片锁死时解锁 |
| `chipDescriptionPath` | 自定义芯片描述文件 | probe-rs 官方没有你的芯片（部分国产 MCU）,用 `target-gen` 从 CMSIS `.pack` 转换 |
| `runtimeExecutable` | 默认 `probe-rs` | 改成了非标准安装路径时用 |
| `server` | `"127.0.0.1:50000"` | 连接一个独立的 `probe-rs dap-server`（远程调试场景） |

`coreConfigs` 里还能开 RTT(不用串口就能打 log,速度快到可以放进中断):

```json
"coreConfigs": [
  {
    "coreIndex": 0,
    "programBinary": "build/YourProject.elf",
    "svdFile": "STM32F407.svd",
    "rttEnabled": true,
    "rttChannelFormats": [
      {
        "channelNumber": 0,
        "dataFormat": "String",
        "showTimestamps": true
      }
    ]
  }
]
```

几个提醒:

- **`svdFile` 强烈建议配**。配上之后 VSCode 里能直接展开外设寄存器每一位,调底层外设时省一半命。SVD 文件去 Keil 的 Pack 包或者芯片厂商官网找。
- 插件目前官方标注仍是 **pre-production / Alpha**,偶尔会抽风。抽风时的退路是 `probe-rs gdb --chip <chip> your.elf` 起一个 GDB server,再用 `arm-none-eabi-gdb` 连上去手动调——流程见本站《使用 arm-none-eabi-gdb 和 probe-rs 实现程序调试》。
- **probe-rs 和 Cortex-Debug 不能混用**。EIDE 自带的烧录器（JLink / STLink / OpenOCD / pyOCD）也能下载,但调试这边统一走 probe-rs,别两套混着配。
- 支持的下载器比想象中多:ST-Link v2/v2-1/v3、J-Link、CMSIS-DAP / DAPLink、Raspberry Pi Debug Probe、FTDI 方案、ESP USB Bridge 等。**这意味着你换一块板子、换一个下载器,配置几乎不用改。**

---

## 二、CLion + STM32CubeMX（体验下来ST系列很舒服，但是其他厂家的配置需要一定动手能力）

CubeMX 里 Toolchain / IDE 选 **STM32CubeIDE**,生成完直接用 CLion 打开目录即可。

优点:

- **代码补全、重构、静态检查是这几套方案里最强的**,写业务逻辑体验最好。
- 内置嵌入式调试支持:配一个 OpenOCD 的 board cfg（或者 ST-LINK server）,点虫子图标就能断点调试，也可以用其他的比如说probe-rs、pyocd但是配置稍微麻烦，不做介绍自行了解。
- 跨平台,和 VSCode 方案一样,不绑死 ST-Link。

要注意的:

- 仍然需要自己装 `arm-none-eabi-gcc`,并在 CLion 的 Toolchains 里指过去。
- 学生可申请免费教育许可

适合:**代码量大、有队友写复杂逻辑（比如上位机协议解析、状态机）** 的场景。

---

## 三、STM32CubeIDE + STM32CubeMX（懒人必备，其实和CLion差不多）

ST 官方的一体化 IDE,基于 Eclipse,**自带 CubeMX**,装完就能用,不需要额外配工具链。

优点:

- 开箱即用,零配置,下载装好就能点灯。
- 免费的、无代码大小限制。
- 官方维护,和 HAL 库版本绑定得最好,不容易出现"库和工具对不上"的怪问题。
- 交叉编译、烧录、调试、CubeMX 配置全在一个软件里,对纯新手最友好。

局限（这是我最在意的一点）:

- **调试绑死 ST-Link**。虽然理论上可以外接 J-Link（装 Segger 插件）或 CMSIS-DAP,但配置过程比较折腾。
- Eclipse 系 IDE 界面偏老旧,启动慢、吃内存,代码补全体验不如 CLion / VSCode。

个人建议直接使用 VSCode / CLion。

---

## 四、Keil MDK5 + STM32CubeMX（经典，教程比较多，但页面和路径管理太落后了）

经典方案,国内教程最多,实验室和老项目里到处都是。CubeMX 里 Toolchain / IDE 选 **MDK-ARM**。

优点:

- **网上资料最多**,遇到报错几乎都能搜到答案,这一点在比赛通宵的时候价值极高。
- 调试器成熟稳定,逻辑分析仪（Logic Analyzer）、Event Recorder 这些好用的东西是 Keil 的强项。
- 队友/学长大概率会,出问题有人问。

坑（说实话这几年我越来越不推荐它了）:

- **对网络有要求**。安装器件支持包（Pack Installer）要联网;授权（License）注册也要联网,换了网卡、重装系统、换电脑都可能要重新处理。比赛现场网络不好的时候很尴尬。
- **未授权版本有 32KB 代码大小限制**。HAL 库本身就挺占地方,稍微用点 FreeRTOS + LVGL 就爆了。
- **只有 Windows**。
- AC5 / AC6 编译器版本差异会带来一些移植问题,老工程换编译器容易出一堆 warning 甚至 error。
- 编辑器本身比较古老,没有好用的现代补全和重构。

适合:**维护已有 Keil 工程、或者队里有人很熟 Keil** 的情况。新开工程我更建议前面三套。

> 如果你实在要装 Keil:记得用管理员权限、安装路径不要有中文、先装 Keil 再装 Pack、装完立刻备份一份 license 相关的信息。

---

## 五、关于用 Rust 开发（个人不建议）

Rust 写嵌入式确实很香——所有权模型能在编译期掐掉一大类内存 bug,`embedded-hal` 生态这几年也做得很漂亮。probe-rs、RTT、`defmt` 这套工具链就是 Rust 社区做起来的,我们前面用的东西其实都沾了它的光（本站也有 Rust 开发 STM32 的尝鲜记录,感兴趣可以去翻）。

**但我不建议比赛/入门阶段用 Rust,原因是实打实的:**

1. **学习曲线陡。** 生命周期、借用检查、`no_std`、PAC/HAL 分层、`.cargo/config.toml` + `memory.x` + 链接脚本,光把工程跑起来就要啃一堆概念。比赛只有几天,不划算。
2. **资料量差一个数量级。** STM32 的 HAL 库教程一搜一大把,Rust 的 `stm32f4xx-hal` 遇到冷门外设基本只能翻 docs.rs 和源码。
3. **队友协作成本高。** 队里只要有一个人不会 Rust,整套工具链对他就是黑盒,分工会很难受。
4. **芯片支持看运气。** 主流 ST 系列没问题,国产替代（PY32、CH32、AT32 这类）在 probe-rs / Rust HAL 侧的支持参差不齐,而比赛里你完全可能临时换芯片。

我的建议:**先把 C + HAL 这套走通,项目做完、有空了,再拿 Rust 复刻一个小 demo 玩玩。** 那时候你会发现很多概念（寄存器、中断、DMA）已经懂了,学 Rust 只剩下学语言本身,体验会好非常多。

---

## 六、强烈建议:学会用 Git 做版本管理

这条不是可选项。**比赛里最常见的翻车不是写不出代码,而是"刚才还好好的,改了两行就全崩了,还不知道改了哪两行"。**

学会 Git,最直接的收益就是:**改坏了能从云端拉回来。**

### 最小可用流程

```bash
git init                        # 或者 git clone <仓库地址>
git add .                       # 把改动放进暂存区
git commit -m "增加 PID 参数整定"   # 提交,写人话,别写 "update"
git push origin main            # 推到云端
```

改坏了想回退:

```bash
git status                      # 看看动了哪些文件
git diff                        # 看看具体改了什么
git checkout -- Core/Src/main.c # 丢掉这个文件的改动
git reset --hard HEAD~1         # 干脆回退到上一次提交(注意:之后就找不回来了)
git log --oneline               # 看历史提交
```

### 几条实操建议

1. **每个阶段性成果都 commit 一次**。一个功能调通了就提交,别攒一天。commit message 写清楚做了什么,未来的你会感谢现在的你。
2. **一定要推到云端**（Gitee / GitHub / GitLab,建议开私有仓库）。只在本地 commit,硬盘挂了就全没了。
3. **配好 `.gitignore`**,别把编译产物传上去,否则仓库几天就几百 MB、clone 慢得要死:

```text
# 编译产物
build/
Debug/
Release/
Objects/
Listings/
*.o
*.elf
*.axf
*.hex
*.bin
*.map

# CubeMX / IDE
.mxproject
.settings/
.cproject
.project
*.launch
.vscode/settings.json

# 系统
.DS_Store
Thumbs.db
```

4. **不要提交 CubeMX 的 `.ioc` 之外的中间文件**,但 `.ioc` **必须提交**——它是你的引脚和时钟配置,是最重要的文件之一。
5. **多人协作时提前分工好文件**。两个人同时改 `main.c` 必然冲突。CubeMX 生成的文件尽量让一个人改,业务代码分文件写。
6. 命令行不习惯就用 GUI:VSCode 左侧源代码管理面板、Git Graph 插件、SourceTree、GitHub Desktop 都行。但 `git log` / `git diff` / `git checkout` 这三个命令,还是建议记一下,救命的时候最快。

---

## 参考

- [probe-rs 官方文档](https://probe.rs/docs/) —— 尤其是 Debugger 一节的 `launch.json` 完整字段说明
- [probe-rs VSCode 插件](https://marketplace.visualstudio.com/items?itemName=probe-rs.probe-rs-debugger)
- B 站 UP 主 **keysking** —— STM32 HAL 库系列教程,讲得清楚,入门强烈推荐
- 本站其他相关文档:
  - 《使用 arm-none-eabi-gdb 和 probe-rs 实现程序调试》
  - 《使用 rust 开发 stm32 体验》
- [https://www.cad.qzz.io](https://www.cad.qzz.io) —— 随记文档主页（Readthedoc 镜像:[https://def.qzz.io](https://def.qzz.io)）
