
# 在 Windows 上安装 ARM GNU Toolchain（用于单片机/STM32 开发）

## 概要

本文档说明在 Windows 平台上获取并配置 ARM GNU Toolchain，配合常见构建工具（CMake、Make/Ninja）以及在 VS Code / CLion 中进行开发的建议步骤与常见问题排查。

## 适用场景

- 使用 `arm-none-eabi-*` 系列工具链进行裸机/嵌入式开发（如 STM32、nRF 等）。
- 在 Windows 环境下使用 CMake + GNU 工具链构建工程。

## 下载与安装

1. 前往官方页面下载 ARM GNU Toolchain（Windows 安装包）：

	https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads

2. 下载 `.msi`（或压缩包）后按提示安装。记下安装目录，例如默认可能为：

	`C:\Program Files\Arm\GNU Toolchain\mingw-w64-x86_64-arm-none-eabi\bin`

3. 将工具链的 `bin` 目录加入系统 `PATH`（建议为当前用户环境变量）。在 PowerShell（以普通用户）中可执行：

	```powershell
	# 将工具链目录追加到当前用户的 Path（请根据实际路径修改）
	$toolPath = 'C:\Program Files\Arm\GNU Toolchain\mingw-w64-x86_64-arm-none-eabi\bin'
	[Environment]::SetEnvironmentVariable('Path', $env:Path + ';' + $toolPath, 'User')
	# 使当前会话立即可用
	$env:Path += ';' + $toolPath
	```

	注意：如果路径中包含空格，请按示例完整使用引号并替换为实际路径。

4. 安装完成后验证：

	```powershell
	arm-none-eabi-gcc --version
	arm-none-eabi-objdump --version
	```

## 安装构建工具（必须）

可使用 `winget` 安装常见构建工具与辅助工具：

```powershell
winget install cmake
winget install ezwinports.make
winget install Ninja-build.Ninja
```

- `cmake`：项目生成器
- `make`（通过 ezwinports 提供的 mingw make）：用于 `MinGW Makefiles` 方案
- `ninja`：更快的构建后端（推荐搭配 Ninja 生成器）

## 开发环境建议

- CLion：对 CMake 支持良好，可与 STM32CubeMX 结合（在 CubeMX 中选择导出为 CubeIDE ）。
- VS Code：推荐安装扩展 `CMake Tools`（管理构建）和 `CMake Language Support`（CMake 高亮/提示）。

  - 注意：`CMake Language Support` 需要 `dotnet`（.NET RUNTIME）以启用某些功能，请在 VS Code 设置中配置 `dotnet` 可执行路径（不一定需要 .net 6）。

## CMake 使用示例

1. 使用 MinGW Makefiles：

```powershell
cmake -B build -G "MinGW Makefiles"
cmake --build build --target all -j <threads>
```

2. 使用 Ninja（当已安装 `ninja` 时更推荐）：

```powershell
cmake -B build -G "Ninja"
cmake --build build -j <threads>
```

将 `<threads>` 替换为 CPU 核心数（合适值）或 直接不写 `-j <threads>` 。

## 常见问题与排查

- 无法找到 `arm-none-eabi-gcc`：确认 `PATH` 是否已正确追加且终端已重启或 `$env:Path` 已更新。可用 `Get-Command arm-none-eabi-gcc` 验证。
- 链接或编译失败：检查使用的 CMake 工具链文件（`-DCMAKE_TOOLCHAIN_FILE=...`）是否指向正确的交叉编译器路径，以及 `CMAKE_C_COMPILER`/`CMAKE_ASM_COMPILER` 是否正确设置。
- VS Code 构建失败：在 `CMake Tools` 中检查所选 Kit（Toolchain）是否为 `arm-none-eabi` 对应的编译器；必要时在 `settings.json` 或项目 `CMakePresets.json` 中指定编译器路径。

## 实用命令汇总

- 验证工具链：`arm-none-eabi-gcc --version`
- 显示 PATH 内容（PowerShell）：`$env:Path -split ';'`
- 检查命令位置：`Get-Command arm-none-eabi-gcc`

## 参考链接

- ARM GNU Toolchain 下载：[官方下载链接](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads,"工具链下载")
- CMake 官方网站：[CMake官网](https://cmake.org/,"官网")
