# 在 Theseus 上构建并运行 C 程序

> *警告：*在 Theseus 之上构建 C 程序的支持仍处于实验阶段，随时可能发生变化。

Theseus 是一个安全语言操作系统（safe-language OS），所有代码都运行在单一地址空间（SAS）和单一特权级（SPL）之中，
因此在 Theseus 之上直接运行任何其他不安全或非 Rust 代码时，**无法保证**其安全性、保护性或隔离性。

尽管如此，我们仍然为在 Theseus 之上构建 C 程序引入了实验性支持；请自行承担风险。

## 前提条件

你必须拥有为 Theseus 交叉编译的 GCC 和 Binutils 版本，例如禁用了 `red zone`（红色区域）使用的 `x86_64-elf` 目标。

为了省事，我们编写了[一个自动化脚本和一份指南](https://www.theseus-os.com/Theseus/book/c/cross_compiler.html)，说明如何构建并安装所有必需的工具。

注意，在运行下面任何 gcc 命令之前，`x86_64-elf-*` 这些二进制文件必须位于你系统的 PATH 中。

## 快速上手：构建 C 程序

示例用的简易 C 程序见 `c_test` 目录。它所做的只是运行一个简单的 `main()` 函数并返回一个常量值。

简而言之，构建 C 程序需要以下步骤：

```sh
make         # 1. 构建 Theseus OS 本身
make tlibc   # 2. 构建 tlibc，即 Theseus 的 libc
make c_test  # 3. 构建一个示例 C 程序
make orun    # 4. 在 QEMU 中运行 Theseus（不重新构建任何东西）
```

## 运行 C 程序

一旦 C 程序的可执行 ELF 文件被打包进 Theseus 的 ISO 镜像，就可以使用 `loadc` 应用在 Theseus 中执行它。
可执行文件默认会被自动放入 `_executable` 命名空间文件夹，因此在 Theseus 的 shell 中运行以下命令：

```
loadc /namespaces/_executable/dummy_works
```

你应该会在 shell 的图形界面上看到返回值，同时还会看到各种日志消息，其中既有来自 tlibc 的输出，也有来自 Theseus 内核的输出。
