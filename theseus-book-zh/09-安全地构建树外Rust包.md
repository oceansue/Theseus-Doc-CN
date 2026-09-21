# 安全地构建树外（out-of-tree）Rust crate

## 背景：问题所在

由于 Rust 目前[尚无稳定的 ABI](https://slightknack.github.io/rust-abi-wiki/intro/intro.html)，因此还没有一种简单、稳定且安全的方法把两个或多个分别编译的 Rust 二进制文件整合在一起。
这里所说的*整合*，指的是让一个二进制文件依赖或调用另一个预构建的二进制文件，例如可执行文件、静态链接库、动态链接的共享对象等。

还有一个与之相关的问题，它源于 Rust 编译器为每个编译出的 crate 以及这些 crate 中的每个（未经名称修饰的）符号附加唯一 ID（编译器使用的元数据）的方式；即便在尚未链接的目标文件中，这个问题也会出现。

举例来说，Theseus 中的 `page_allocator` crate 会被编译成一个名字形如 `page_allocator-c55b593144fe8446.o` 的目标文件，而该 crate 实现并导出的函数 `page_allocator::allocate_pages_at()` 则会以符号 `_ZN14page_allocator17allocate_pages_at17heb9fd5c4948b3ccfE` 的形式生成。

crate 的唯一 ID（`c55b593144fe8446`）与每个符号的唯一 ID（例如 `heb9fd5c4948b3ccfE`）的取值都是确定性的，但取决于许多因素。
这些因素包括编译器版本、源码目录、目标目录等等。
我们有时把这两种唯一 ID 统称为*哈希*值，因为编译器是通过把这些因素一起哈希而得到它们的；这种哈希的生成方式被视为不透明且随时可能变化，因此我们把它当作黑盒对待。

Theseus 在运行时动态地加载并链接 crate 的目标文件。
当我们把所有 Theseus 内核 crate 一起构建到同一个目标目录中时（[详见此处](https://www.theseus-os.com/Theseus/book/building/building.html#cargo)），附加在每个 crate 名和符号上的唯一 ID/哈希值就取决于构建机器上的源码目录与目标目录（以及其他因素）。
一个运行中的 Theseus 实例在内存中只会载入一个 `page_allocator` crate 的实例，并期望所有其他 crate 都依赖该实例，也就是说，这些 crate 在编译时就应当预期链接到其带有特定哈希的符号，例如 `_ZN14page_allocator17allocate_pages_at17heb9fd5c4948b3ccfE`。

如果你单独编译另一个依赖完全相同一组 Theseus 内核 crate 的 `my_crate`，cargo 会把这些 Theseus crate *从源码*重新编译到那个新的目标目录中，导致重新生成的目标文件及其符号带有与原始 Theseus 实例完全不同的唯一 ID 哈希。
因此，当试图把 `my_crate` 加载进那个已在运行的预构建 Theseus 实例时，加载和链接都会失败，因为这个版本的 `my_crate` 依赖的是哈希值不同的 crate/符号，例如，它可能依赖符号 `_ZN14page_allocator17allocate_pages_at17hd64cba3bd66ea729E` 而不是 `_ZN14page_allocator17allocate_pages_at17heb9fd5c4948b3ccfE`（注意两者附加的哈希值不同）。

因此，**真正的问题**在于目前没有任何受支持的方法可以告诉 cargo：请针对一组预构建的依赖来构建某个 crate。至于这一功能为何有用却至今未获支持（提示：Rust 没有稳定的 ABI），[参见这个 GitHub issue](https://github.com/rust-lang/cargo/issues/1139) 了解更多。

### 一种糟糕且不安全的解决方案

从技术上讲，我们可以借助现有的非 Rust 的稳定 ABI（比如 C 语言 ABI）来解决这个问题。
这要求以与 C 兼容的方式定义/导出 Rust 函数、数据和类型，使它们与 C ABI（其预期的结构体内存布局和调用约定）兼容。
遗憾的是，这不可避免地要使用不安全的 FFI 代码块（通过 C 风格的 extern 函数）来连接两段彼此独立、完全安全的 Rust 代码，既愚蠢又繁琐。

在上面的例子中，我们无法直接调用 `page_allocator::allocate_pages_at()`，而需要像下面这样导出相应的包装函数：

```rust

#![allow(unused)]
fn main() {
// in `page_allocator`
#[no_mangle]
pub extern "C" fn allocate_pages_at(num_pages: usize, ...) -> ... {
    page_allocator::allocate_pages_at(num_pages, ...)
    ...
}
}
```

然后再用不安全的 FFI 代码块调用它：

```rust
// in `my_crate` 
extern "C" {
    fn allocate_pages_at(num_pages: usize, ...);
}
fn main() {
    unsafe {
        allocate_pages_at(15, ...);
        ...
    }
}
```

注意，上面省略了许多细节；这些代码包装器和绑定虽然可以自动生成，但不安全性却无法避免。

我们显然可以做得更好！

## 解决方案：使用 `theseus_cargo` 进行树外构建

更好的方案是"骗过"Rust 编译器，让它使用某次已有 Theseus 构建中的预构建 crate。
为此，我们开发了 `theseus_cargo`，它是一个自定义构建工具，也是 cargo 的一个包装器，能够利用预构建产物来解析树外 crate 对树内 Theseus crate 的依赖，而不是从源码重新构建这些依赖。

这一点通过两部分实现：

1. 在构建 Theseus 的（树内）内核 crate 时生成预构建依赖；
2. 针对这些预构建的 Theseus crate 正确地构建树外 crate。

### 1. 生成预构建依赖的集合

为了生成一组 Rust 编译器工具链能够理解的依赖文件，顶层的 Makefile 会调用另一个自定义构建工具，即位于 `tools/` 目录下的名为 `copy_latest_crate_objects` 的 Rust 程序。
它的调用方式如下（省略了细节）：

```mk
cargo run ... tools/copy_latest_crate_objects --  \
    --input  "target/.../deps"                    \
    --output-deps  "build/deps/"                  \
    --output-sysroot  "build/deps/sysroot/"       \
    ...
```

上述参数指定了我们希望：

1. 使用 target/.../deps 目录中由 Rust 生成的构建产物（已编译的 crate）作为输入，然后
2. 把它们复制到输出目录 build/deps/ 中。
3. 同时，把已交叉编译进 Theseus 平台专用 sysroot 文件夹的 Rust 基础库（core、alloc）的预构建版本复制到 build/deps/sysroot/。

此后，`build/deps/` 目录中就包含了针对已有的 Theseus 构建来编译树外 crate 所需的全部预构建依赖，其中的 crate 和符号都带有正确的版本（哈希正确）。
该工具还会生成一个 `TheseusBuild.toml` 文件，描述本次 Theseus 构建的各项参数，以便 `theseus_cargo` 能够复现这次构建。例如：

```toml
target = "x86_64-unknown-theseus"
rustflags = "--emit=obj -C debuginfo=2 -C code-model=large -C relocation-model=static -D unused-must-use -Z merge-functions=disabled -Z share-generics=no"
cargoflags = "--release"
host_deps = "./host_deps"
```

### 2. 针对预构建的 Theseus 依赖构建其他 Rust 代码

有了上面所述的 `build/deps/` 目录内容之后，我们就可以调用 `theseus_cargo`，在一个单独的编译实例中构建新的树外 crate。
`theseus_cargo` 工具是一个 Rust 程序，它会调用 cargo、捕获其详细输出，然后修改并重新执行 cargo 发出的 `rustc` 命令，让预构建的 crate 来满足树外 crate 的依赖。
这些预构建 crate 是一组依赖文件，即 `.rmeta` 和 `.rlib` 文件，Rust 编译器内部的元数据解析器能够理解它们。

`theseus_cargo` 对 rustc 命令所做的主要修改，是把下列参数中的 `<值>` 替换为 `/build/deps/` 中预构建 Theseus crate 的路径与名称：

- -L dependency=<dir>
- --extern <crate_name>=<crate_file>.rmeta

如果某条 rustc 命令带有需要修改的参数，`theseus_cargo` 就会重新执行该命令。

目前，要使用 `theseus_cargo`，必须从源码编译并安装它：

```sh
cargo install --path="tools/theseus_cargo" --root=$INSTALL_DIR
```

之后，就可以像 `cargo build` 一样调用它，例如针对输入文件夹中的预构建依赖构建一个 crate：

```sh
$INSTALL_DIR/theseus_cargo --input "build/deps/"  build
```

目前，`theseus_cargo` 会输出***非常冗长***的内容，其中会显示大量与结果无关的警告和日志语句，描述它正在做什么。
如果树外 crate 构建成功，它最后会打印出类似 "Ran rustc command (modified for Theseus) successfully" 的信息，然后以退出码 0 成功退出。

更多细节请参见 [`tools/theseus_cargo` 的源代码](https://github.com/theseus-os/Theseus/blob/theseus_main/tools/theseus_cargo/src/main.rs)。

通过捕获并修改 cargo 详细输出中的 rustc 命令，这种做法显然并不理想，但目前没有其他受支持的方式来获取这些信息，因为 [cargo 正在移除其 `--build-plan` 选项](https://github.com/rust-lang/cargo/issues/5579)。

## 相关链接、讨论与替代方案

- [Rust 的稳定模块化 ABI（Rust Internals Forum）](https://internals.rust-lang.org/t/a-stable-modular-abi-for-rust/12347/69)
- [Rust ABI wiki](https://slightknack.github.io/rust-abi-wiki/)
- [abi_stable](https://crates.io/crates/abi_stable) crate，它在底层的 Rust 到 Rust FFI 之上提供了"安全"的 trait、宏和包装器。
