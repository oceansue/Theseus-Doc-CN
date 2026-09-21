# The Theseus OS Book（中文版）

Theseus 操作系统官方文档的中文翻译，基于官方在线书籍：

- 原文地址：<https://www.theseus-os.com/Theseus/book/print.html>
- 原文仓库：<https://github.com/theseus-os/Theseus>
- 原文语言：English ｜ 译本语言：简体中文
- 翻译日期：2026-09-21

> **说明**：本文档为学习用途的中文翻译，代码、命令与插图路径均保留原样；
> 书内相对链接已改写为指向官方网站的绝对链接，可直接点击跳转。
> 如与最新官方文档有出入，请以[英文原版](https://www.theseus-os.com/Theseus/book/print.html)为准。
> 全部插图为原书 SVG 图片，位于本目录的 `images/` 文件夹中。

## 目录

### 入门篇

| 章节 | 标题 |
| --- | --- |
| 00 | [Theseus 简介](00-Theseus简介.md) |
| 01 | [Theseus 的设计与结构](01-Theseus的设计与结构.md)（含全部 3 幅架构插图） |
| 02 | [源代码组织](02-源代码组织.md) |
| 03 | [启动过程与执行流程](03-启动过程与执行流程.md) |
| 04 | [Theseus 的理念与灵感](04-Theseus的理念与灵感.md) |

### 应用与构建篇

| 章节 | 标题 |
| --- | --- |
| 05 | [应用程序支持与开发](05-应用程序支持与开发.md) |
| 06 | [Theseus 的构建过程](06-Theseus的构建过程.md) |
| 07 | [配置 Theseus](07-配置Theseus.md) |
| 08 | [其他配置选项](08-其他配置选项.md)（含插图：静态链接 vs 动态链接） |
| 09 | [安全地构建树外 Rust 包](09-安全地构建树外Rust包.md) |
| 10 | [在 Theseus 上构建并运行 C 程序](10-在Theseus上构建并运行C程序.md) |
| 11 | [这一切是如何工作的](11-这一切是如何工作的.md) |
| 12 | [构建面向 Theseus 的 GCC 与 Binutils（x86_64-elf）](12-构建面向Theseus的GCC与Binutils.md) |
| 13 | [tlibc：编译与链接 Theseus 的 libc](13-tlibc：编译与链接Theseus的libc.md) |
| 14 | [编译与链接 C 程序](14-编译与链接C程序.md) |

### 核心子系统篇

| 章节 | 标题 |
| --- | --- |
| 15 | [关键子系统概览](15-关键子系统概览.md) |
| 16 | [Theseus 中的内存管理](16-Theseus中的内存管理.md) |
| 17 | [虚拟内存到物理内存的映射](17-虚拟内存到物理内存的映射.md) |
| 18 | [堆：动态内存分配](18-堆：动态内存分配.md) |
| 19 | [Theseus 中的任务子系统](19-Theseus中的任务子系统.md) |
| 20 | [任务管理中维护的不变量](20-任务管理中维护的不变量.md) |

### 图形与运行篇

| 章节 | 标题 |
| --- | --- |
| 21 | [显示子系统](21-显示子系统.md) |
| 22 | [窗口管理器的工作原理](22-窗口管理器的工作原理.md) |
| 23 | [如何创建窗口并显示内容](23-如何创建窗口并显示内容.md) |
| 24 | [在虚拟机或真实硬件上运行 Theseus](24-在虚拟机或真实硬件上运行Theseus.md) |
| 25 | [在虚拟机中运行 Theseus](25-在虚拟机中运行Theseus.md) |
| 26 | [使用 QEMU 进行 PCI 设备直通](26-使用QEMU进行PCI设备直通.md) |
| 27 | [在无头系统上交互式运行 Theseus](27-在无头系统上交互式运行Theseus.md) |
| 28 | [从 U 盘引导 Theseus](28-从U盘引导Theseus.md) |
| 29 | [通过 PXE 在真实硬件上引导 Theseus](29-通过PXE在真实硬件上引导Theseus.md) |

### 社区篇

| 章节 | 标题 |
| --- | --- |
| 30 | [软件开发的黄金法则](30-软件开发的黄金法则.md) |
| 31 | [贡献与 git 使用建议](31-贡献与git使用建议.md) |
| 32 | [关于 Theseus 的论文与演讲](32-关于Theseus的论文与演讲.md) |
| 33 | [Theseus 自述与快速上手](33-Theseus自述与快速上手.md) |

## 插图索引

| 图片 | 所在章节 | 内容 |
| --- | --- | --- |
| [images/kernel_structure.svg](images/kernel_structure.svg) | 01 | 现有操作系统设计与 Theseus 的结构对比 |
| [images/cell_consistency.svg](images/cell_consistency.svg) | 01 | 细胞（cell）抽象在实现、构建与运行时各阶段的一致性 |
| [images/metadata_tree.svg](images/metadata_tree.svg) | 01 | 简单的 crate 命名空间及相互依赖的节 |
| [images/boot_image.svg](images/boot_image.svg) | 08 | 构建期静态链接（左）与 Theseus 动态运行时链接（右）的对比 |

## 许可与致谢

- Theseus 项目由 Kevin Boos 等人开发，采用 MIT 许可证发布。
- 本翻译遵循原项目的开源许可；感谢 Theseus 社区提供的优秀文档。
