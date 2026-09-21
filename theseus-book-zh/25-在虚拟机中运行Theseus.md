# 在虚拟机中运行 Theseus

使用虚拟机模拟器是开发、测试和运行 Theseus 迄今为止最简单的方式。

## QEMU

我们的主要测试环境和推荐的模拟器是 [QEMU](https://www.qemu.org/)，它也是使用我们内置的 Makefile 命令运行 Theseus 时的默认选择。
例如，`make run` 目标会在构建过程完成后自动在 QEMU 虚拟机中运行 Theseus。

顶层 Makefile 指定了 Theseus 在 QEMU 中的配置参数，例如系统内存、挂载的存储设备、串口日志输出等。
所有这些参数都以 `QEMU_` 开头，可以在命令行中覆盖，也可以通过设置诸如 `net` 或 `host` 之类的环境变量来间接覆盖，或者直接编辑 Makefile 本身。

## Bochs

在 Theseus 的较早版本中，我们同时使用 [Bochs](https://bochs.sourceforge.io/) 和 QEMU 进行测试。Bochs 目前仍受支持，但其配置可能已经过时；相关配置位于仓库根目录下的 `bochsrc.txt`（[直接链接](https://github.com/theseus-os/Theseus/blob/theseus_main/bochsrc.txt)）文件中。

Bochs 运行得相当慢，而且支持的硬件设备虚拟化远少于 QEMU；因此，我们不推荐使用它。不过，你可以使用 Makefile 中为它准备的目标来尝试在 Bochs 中运行 Theseus：

```sh
make bochs
```

## VMware Workstation Player

我们已经在 VMWare Workstation 上测试过 Theseus，它通常开箱即用。不过，你可能需要启用一些选项来提升性能，并让 Theseus 能够访问更多设备。

首先，[在此下载 VMware Workstation Player](https://www.vmware.com/products/workstation-player/workstation-player-evaluation.html)，它可以在非商业用途下免费安装和使用。

在 Linux 上，你将下载到一个 `.bundle` 文件，随后需要在终端中执行它。例如：

```sh
chmod +x VMware-Player-<...>.bundle
sudo ./VMware-Player-<...>.bundle
```

打开 VMware Workstation Player 之后，请执行以下操作：

1. 点击 Create A New Virtual Machine（创建新的虚拟机）。
2. 在 New Virtual Machine Wizard（新建虚拟机向导）窗口中，选择 Use ISO image:（使用 ISO 镜像:），然后浏览并选择 Theseus 的 ISO 镜像，它应该位于 build 目录下，例如 build/theseus-x86_64.iso。接着，点击 Next（下一步）。
3. 在 Guest Operating System（客户机操作系统）下，选择 Other（其他）按钮，然后从下拉菜单中选择 Other 64-bit（其他 64 位）。接着，点击 Next（下一步）。
4. 将 Name:（名称:）字段设置为 "Theseus" 或你喜欢的任何名称。点击 Next（下一步）。
5. 磁盘大小无所谓；点击 Next（下一步）。
6. 点击 Customize Hardware（自定义硬件），然后选择以下设置：
    - 512MB 内存（更少的内存也许可行，但最低需要大约 10-20 MB）。
    - 2 个或更多处理器核心。
    - 如果你想使用 CPU 性能计数器，请选择 Virtualize CPU performance counters（虚拟化 CPU 性能计数器）（并非必需）。
    - 如果你想获取 Theseus 的日志输出，则需要添加一个串口连接：
        1. 点击左下角的 Add...（添加...）以添加新的硬件类型，然后选择 Serial Port（串口）。
        2. 在 Connection（连接）下，选择 Use output file:（使用输出文件:），然后为串口日志选择一个要写入的目标文件名。例如，/home/your_user/theseus_vmware.log。
        3. 点击 Save（保存）。
7. 点击 Finish（完成），然后点击 Close（关闭）。

Theseus 应该会在几秒钟后启动。你可以通过 `cat` 查看或直接打开该文件来查看串口日志输出：

```sh
cat /home/your_user/theseus_vmware.log
```

## VirtualBox

我们已经在 VirtualBox 上测试过 Theseus，它通常开箱即用。不过，你可能需要启用一些选项来提升性能，并让 Theseus 能够访问更多设备。

首先，[在此下载 VirtualBox](https://www.virtualbox.org/wiki/Downloads) 并将其安装到你的系统上。在 Ubuntu 及其他基于 Debian 的 Linux 发行版上，你会下载到一个 `.deb` 文件，可以用软件安装器打开它，也可以像这样在命令行中安装：

```sh
sudo dpkg -i virtualbox-<...>.deb
```

打开 VirtualBox 之后，请执行以下操作：

1. 点击 New（新建）。
2. 在 Create Virtual Machine（创建虚拟机）窗口中，将 Type（类型）设为 Other（其他），将 Version（版本）设为 Other/Unknown (64-bit)（其他/未知（64 位）），取一个名称，然后点击 Next（下一步）。
3. 在下一个窗口中，选择 512MB 内存（更少的内存也许可行，但最低需要大约 10-20 MB）。
4. 在所有存储磁盘选项上继续点击下一步即可，这些设置无关紧要。
5. 回到主窗口后，右键点击你新建的 Theseus 虚拟机并选择 Settings（设置）。
6. 在左侧边栏中点击 Storage（存储），然后选择 💿 Empty（💿 空）选项，为光盘选择一个镜像。
点击 Optical Drive:（光驱:）选项右侧的 💿▾ 按钮，选择 Choose a disk file（选择一个磁盘文件），然后导航到 build/ 目录下的 Theseus ISO 镜像，例如 build/theseus-x86_64.iso。
7. 在左侧边栏的 System（系统）下，切换到 Processor（处理器）标签页，选择 2 个（或更多）处理器。
8. 如果你想获取 Theseus 的日志输出，则需要添加一个串口连接：
    1. 在左侧边栏中点击 Serial Ports（串口），在 Port 1 标签页下，勾选 Enable Serial Port（启用串口）复选框。
    2. 在 Port Mode（端口模式）下拉菜单中，选择 Raw File（原始文件）选项。
    3. 在 Path/Address（路径/地址）文本框中，输入串口日志要写入的目标文件名。例如，/home/your_user/theseus_vbox.log。
    4. 点击 Ok（确定）。
9. 在主窗口中，从左侧边栏选择 Theseus 虚拟机条目，然后点击顶栏的 Start（启动）。

Theseus 应该会在几秒钟后启动。你可以通过 `cat` 查看或直接打开该文件来查看串口日志输出：

```sh
cat /home/your_user/theseus_vbox.log
```
