# 构建面向 Theseus（x86_64-elf）的 GCC 与 Binutils

**我们提供了一个脚本，可以替你完成所有这些工作；**参见 [scripts/install_x86_64-elf-gcc.sh](https://github.com/theseus-os/Theseus/blob/theseus_main/scripts/install_x86_64-elf-gcc.sh)，

```sh
./scripts/install_x86_64-elf-gcc.sh $HOME/src $HOME/opt
```

---

在本文中，我们会用到两个目录，二者都可以设置为你指定的位置：

1. $SRC：存放 gcc 和 binutils 源码的目录
    - 例如 $HOME/src/
2. $DEST：存放我们编译出的 gcc 和 binutils 软件包及库的目录（也就是它们的安装位置）
    - 例如 $HOME/opt/

（说明步骤取自 [OS dev wiki 上的这篇教程](https://wiki.osdev.org/Building_GCC)。）

## 1. 构建独立版本的 GCC 和 Binutils

安装所需的软件包：

```sh
sudo apt-get install gcc build-essential bison flex libgmp3-dev libmpc-dev libmpfr-dev texinfo gcc-multilib
```

### 下载并构建 GCC/Binutils

在本教程中，我们将使用 2020 年 7 月 20 日发布的 `gcc` `10.2.0` 版本，
以及 2020 年 9 月 19 日发布的 `binutils` `2.35.1` 版本。

你可以从网上众多镜像站点获取它们，例如：

- gcc: [https://mirrors.kernel.org/gnu/gcc/gcc-10.2.0/](https://mirrors.kernel.org/gnu/gcc/gcc-10.2.0/)
- binutils: [https://mirrors.kernel.org/gnu/binutils/](https://mirrors.kernel.org/gnu/binutils/)

为新构建的软件包创建一个用于安装的目标目录：

```sh
mkdir $DEST
export PREFIX="$DEST/gcc-10.2.0"
```

把每个源码包解压到你选择的目录（`$SRC`）中，然后构建 binutils：

```sh
mkdir build-binutils
cd build-binutils
../binutils-2.35.1/configure --prefix="$PREFIX" --disable-nls --disable-werror
make -j$(nproc)
make install
```

然后回到 `$SRC` 目录并构建 gcc：

```sh
cd gcc-10.2.0
./contrib/download_prerequisites
cd ../

mkdir build-gcc
cd build-gcc
../gcc-10.2.0/configure --prefix="$PREFIX" --disable-nls --enable-languages=c,c++
make -j$(nproc)
make install
```

## 2. 再次构建 GCC 和 Binutils，使其交叉目标为 Theseus（x86_64-elf）

既然我们已经获得了一份独立于主机系统包管理器所安装版本的 gcc/binutils 构建，就可以用它来构建一个本身就针对特定目标执行交叉编译的 gcc 版本——在这里，就是我们的 Theseus `x86_64-elf` 目标。

注意：以下步骤基于 [OS dev wiki 上的这篇教程](https://wiki.osdev.org/GCC_Cross-Compiler#The_Build)。

首先，为交叉编译器的构建与安装创建一个目录，例如 `$DEST/cross`。

```sh
mkdir $DEST/cross
export PREFIX="$DEST/cross"
export TARGET=x86_64-elf
export PATH="$PREFIX/bin:$PATH"
```

其次，重新构建与上文相同的 binutils 软件包，但要按使其面向 Theseus 的方式进行配置。

```sh
../binutils-2.35.1/configure --target=$TARGET --prefix="$PREFIX" --with-sysroot --disable-nls --disable-werror
make -j$(nproc)
make install
```

确认新构建的交叉编译器 binutils 软件包确实存在，并且位于系统的 PATH 中：

```sh
which --$TARGET-as
```

应当输出类似下面的内容：

> ```
> /home/my_username/opt/cross/bin/x86_64-elf-as
> ```

然后回到 `$SRC` 目录，构建一个能把 C/C++ 程序交叉编译到 Theseus 的 gcc 版本。

```sh
mkdir cross-build-gcc
cd cross-build-gcc
../gcc-10.2.0/configure --target=$TARGET --prefix="$PREFIX" --disable-nls --enable-languages=c,c++ --without-headers
make all-gcc -j$(nproc)
make all-target-libgcc -j$(nproc) 
make install-gcc
make install-target-libgcc
```

在继续之前，先检查一下交叉编译出的 gcc 是否能正常工作。

```sh
$DEST/cross/bin/$TARGET-gcc --version
```

它应当打印出一些关于你新构建的 gcc 的信息。加上 `-v` 标志可以输出更多细节。

## 3. 重新构建 GCC，去除默认的 red zone（红色区域）使用

重要的是，我们必须在 gcc 中完全禁用 [red zone（红色区域）](https://en.wikipedia.org/wiki/Red_zone_(computing))。在调用 gcc 本身时，我们只需在命令行上传入 `-mno-red-zone` 参数即可，但这并不会影响交叉编译得到的 `libgcc` 本身。因此，为了避免 `libgcc` 中的函数错误地使用 Theseus 中并不存在的 red zone，我们必须构建一个无 red zone 的 `libgcc` 版本，这样才能成功地为 Theseus 构建并链接 C 程序，而不会让 `libgcc` 的方法试图写入 red zone。

注意：以下步骤改编自 [这篇教程](https://wiki.osdev.org/Libgcc_without_red_zone)。

### 调整 GCC 配置

首先，在 gcc 源码树的 `$SRC/gcc-10.2.0/gcc/config/i386` 目录下新建一个文件。

将以下几行添加到这个新文件中并保存：

```
MULTILIB_OPTIONS += mno-red-zone
MULTILIB_DIRNAMES += no-red-zone
```

是的，尽管我们是在为 `x86_64` 进行构建，也要把它放进名为 `i386` 的原始 x86 架构配置目录中。

然后，让 gcc 的构建过程使用这个新的 `multilib` 配置。打开文件 `$SRC/gcc-10.2.0/gcc/config`，搜索以下配置行（对于 gcc-10.2.0，它们从第 1867 行开始）：

```
x86_64-*-elf*)
	tm_file="${tm_file} i386/unix.h i386/att.h dbxelf.h elfos.h newlib-stdint.h i386/i386elf.h i386/x86-64.h"
	;;
```

添加一行，使其看起来像这样：

```
x86_64-*-elf*)
	tmake_file="${tmake_file} i386/t-x86_64-elf"
	tm_file="${tm_file} i386/unix.h i386/att.h dbxelf.h elfos.h newlib-stdint.h i386/i386elf.h i386/x86-64.h"
	;;
```

**注意**：`tmake_file` 前面的缩进必须是 TAB，而不是空格。

### 重新构建不带 red zone 的 GCC

回到构建目录，重新配置并重新构建 `libgcc`：

```sh
cd $SRC/cross-build-gcc
../gcc-10.2.0/configure --target=$TARGET --prefix="$PREFIX" --disable-nls --enable-languages=c,c++ --without-headers
make all-gcc -j$(nproc)
make all-target-libgcc -j$(nproc) 
make install-gcc
make install-target-libgcc
```

要验证是否成功，请运行以下两条命令：

```sh
x86_64-elf-gcc -print-libgcc-file-name
x86_64-elf-gcc -mno-red-zone -print-libgcc-file-name
```

第一条命令应当输出指向 `libgcc.a` 的路径，第二条命令应当输出一个类似、但以 `no-red-zone` 为所在目录的路径：

> ```
> $DEST/cross/lib/gcc/x86_64-elf/10.2.0/libgcc.a
> $DEST/cross/lib/gcc/x86_64-elf/10.2.0/no-red-zone/libgcc.a
> ```

## 附录：如何使用无 red zone 版本的 GCC

要正确使用这个面向 Theseus 目标交叉编译并禁用了 red zone 的新版 GCC，请务必做到：

1. 使用现在位于 $DEST/cross 中的 x86_64-elf-gcc 可执行文件
2. 指定 -mno-red-zone 标志，可以在命令行上指定，也可以将其作为 LDFLAGS 的一部分
