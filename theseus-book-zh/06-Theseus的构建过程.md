# Theseus 的构建过程

### Cargo

Theseus 使用 [cargo](https://doc.rust-lang.org/cargo/index.html)（Rust 的包管理器与构建工具）来自动管理依赖，并替我们调用真正的 Rust 编译器。
我们利用 cargo 的 [workspace 特性](https://doc.rust-lang.org/cargo/reference/workspaces.html)与虚拟清单（virtual manifest），把所有主要 crate 归组到一个顶层元项目（meta project）之中，这能显著加快构建速度。
这样一来，来自主仓库目录（`kernel/` 和 `applications/`）的 crate 及其全部依赖，都会被编译到同一个 `target/` 目录中。

该 workspace 的成员定义在根目录的 [Cargo.toml](https://github.com/theseus-os/Theseus/blob/theseus_main/Cargo.toml) 清单文件中，其中还列出了 cargo 应当忽略的其他目录。

### Makefile

虽然所有 Rust 代码都是用 cargo 构建的，我们仍然使用 `make` 和 Makefile 来处理高层次的构建任务。你不需要直接运行 `cargo` 或 `rustc` 命令；一切请通过 `make` 来完成。

顶层 [Makefile](https://github.com/theseus-os/Theseus/blob/theseus_main/Makefile) 本质上只是通过 `cargo` 调用 Rust 工具链和编译器，然后把编译出的目标文件从相应的 `target/` 目录复制到顶层的 `build/` 目录，最后使用各种引导加载程序工具（例如 GRUB）生成可引导的 `.iso` 镜像。

Makefile 唯一的特殊构建动作，是使用 `nasm` 汇编器编译 `nano_core/boot/` 中与体系结构相关的汇编代码，然后将其与 `nano_core` 完整链接为一个独立的静态二进制文件。

### 配置 Theseus

请继续阅读[下一节](https://www.theseus-os.com/Theseus/book/building/configuration.html)，进一步了解如何配置 Theseus 的构建。
