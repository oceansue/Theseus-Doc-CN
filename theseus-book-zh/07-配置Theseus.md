# 配置 Theseus

Theseus 的源码使用 Rust 标准提供的 `cfg` 选项，通过构建期配置实现条件编译。

我们通过 `THESEUS_CONFIG` 环境变量来暴露设置这些选项的能力，它可以在命令行上、Makefile 本身中，或 Rust 构建脚本里设置。

要在命令行上设置一个或多个 cfg 选项，所有 cfg 选项必须写在一个带引号的字符串里，各个 cfg 选项之间用空白分隔。例如：

```sh
make run THESEUS_CONFIG="cfg_option_1 cfg_option_2"
```

下面是在 Makefile 中设置 cfg 选项的方式。本例中，每当执行 `make my_target` 时都会设置同样的 `cfg_option_1`：

```mk
my_target : export override THESEUS_CONFIG += cfg_option_1
my_target:
    $(MAKE) run
```

## 在 Rust 源码中使用 cfg 选项

在 Rust 中，主要有两种使用 cfg 语句的方式：

1. 作为代码块上的属性（attribute），从而启用条件编译。
    - 下面的代码中，如果设置了 cfg_option_1，foo() 会被编译为上面那个代码块，否则 foo() 会被编译为下面那个代码块。
`
#![allow(unused)]
fn main() {
#[cfg(cfg_option_1)]
fn foo() {
println!("cfg_option_1 was enabled!");
}

#[cfg(not(cfg_option_1))]
fn foo() {
println!("cfg_option_1 was disabled!");
}
}
`
2. 作为运行时的 if 条件判断，通过 `cfg!()` 宏在运行时使用并检查一个静态已知的 cfg 选项，该宏返回一个布尔值。
`
#![allow(unused)]
fn main() {
fn foo() {
if cfg!("cfg_option_1") {
println!("cfg_option_1 was enabled!");
} else {
println!("cfg_option_1 was disabled!");
}
}
}
`

请点击下方链接，进一步了解 Rust 对 cfg 选项的支持：

- [Rust 中条件编译的概述](https://doc.rust-lang.org/reference/conditional-compilation.html)
- [Rust by Example：`cfg`](https://doc.rust-lang.org/rust-by-example/attribute/cfg.html)
- [Rust 的 `cfg!()` 宏](https://doc.rust-lang.org/std/macro.cfg.html)

## `THESEUS_CONFIG` 与 `cfg` 如何协同工作

顶层 `Makefile` 中的一行代码，会把由 `THESEUS_CONFIG` 指定的 cfg 选项转换为 Rust 能够识别的 `--cfg` 值，从而可与标准的 Rust cfg 属性配合使用。
如下所示，这一行仅仅是给 `THESEUS_CONFIG` 中每个以空白分隔的值加上 "--cfg" 前缀，然后把它们全部追加到 `RUSTFLAGS` 环境变量中。

```mk
cargo : export override RUSTFLAGS += $(patsubst %,--cfg %, $(THESEUS_CONFIG))
```

> 注意：你也可以直接向 `RUSTFLAGS` 中添加 `--cfg XYZ`，而不必使用 `THESEUS_CONFIG`。

这是一种标准做法，可避免我们先前基于全局构建脚本的做法所带来的开销。
[详情请阅读此处](https://doc.rust-lang.org/rustc/command-line-arguments.html#--cfg-configure-the-compilation-environment)。
