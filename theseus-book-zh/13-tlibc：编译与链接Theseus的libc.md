# `tlibc`：编译与链接 Theseus 的 libc

> *警告：* 在 Theseus 之上构建 C 程序的支持尚处于实验阶段，随时可能发生变化。

Theseus 的 libc 实现 `tlibc` 仍在开发之中，目前只是一个概念验证（proof-of-concept）库，缺少大多数标准 libc 的功能。

## 以与 Theseus 兼容的方式构建 tlibc

大多数标准库和 libc 实现都被构建为完全链接的静态库或动态库；用 Rust 的术语来说，这对应于 `staticlib` 或 `cdylib` crate 类型（[关于 crate 类型与链接的更多信息见这里](https://doc.rust-lang.org/reference/linkage.html)）。

这种做法对 Theseus 来说并不适用，原因有以下几点。
首先，由于 Theseus 在单一特权级（SPL）下运行所有代码，最底层的用户代码与最顶层的内核代码之间没有清晰的分界点。
在传统操作系统中，标准库通过*系统调用*接口把自己的代码与操作系统的其余部分隔离开。
这样一来，针对特定操作系统平台进行构建就很容易——只需定义系统调用接口，并针对必要的头文件进行编译即可。
不需要进行复杂的链接，因为依赖链的最底端终止于 `syscall` 汇编指令，这使得该库从链接器的角度来看是自包含的。

其次，Theseus 在运行时对原始目标文件进行动态链接，因此我们无法轻易地为独立的 C 库创建完全静态链接的二进制文件，因为它无法得知自己的依赖会存在于内存中的什么位置。
同样，这对标准 libc 实现来说不成问题，因为它不需要直接链接到每一个具体的系统调用处理函数。

因此，我们为 `tlibc` 使用标准的 `rlib` crate 类型，并自行对编译得到的原始目标文件执行部分链接。

```sh
ld -r -o tlibc/target/.../tlibc.o  tlibc/target/.../deps/*.o
```

另外，我们也可以像下面这样使用 `ar` 把所有目标文件打包成一个归档文件；这两种做法在功能上没有太大差别，但有些构建工具更倾向于使用 `.a` 归档文件，而不是 `.o` 目标文件。

```sh
ar -rcs tlibc/target/.../libtlibc.a  tlibc/target/.../deps/*.o
```

我们使用 `theseus_cargo` 工具（[如这里所述](https://www.theseus-os.com/Theseus/book/building/rust_builds_out_of_tree.html)）来确保 `tlibc` 是针对既有 Theseus 构建中正确版本的 crate 和符号进行编译并依赖它们。

## 使用 tlibc

得到 `tlibc.o`（或 `.a`）文件之后，我们就可以用它来满足任意 C 程序对基本 libc 函数/数据的依赖。

[下一节](https://www.theseus-os.com/Theseus/book/c/compiler_linker.html)介绍我们如何使用 `tlibc` 文件来构建一个可以在 Theseus 之上运行的独立 C 可执行文件。
