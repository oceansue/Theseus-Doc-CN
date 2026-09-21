# 在无头系统上交互式运行 Theseus

默认情况下，Theseus 期望运行在带有基本图形显示（显示器）和真实键盘（以及可选的鼠标）的标准桌面环境中。
Theseus 使用键盘作为主要输入设备、图形显示器作为主要输出设备来与系统交互。

Theseus 也可以在[无头模式（headless mode）](https://en.wikipedia.org/wiki/Headless_computer)下运行，此时计算机的"头"（显示器和键盘）并不存在，I/O 通过网络或串口连接完成。
这对服务器、嵌入式微控制器、某些虚拟机环境以及其他任何没有显示器显示的系统环境都很有用。

当前版本的 Theseus 只在串口（COM1 和 COM2）上监听传入的连接。
当在某个串口上收到数据（例如一次按键）时，Theseus 会派生一个终端模拟器来处理该端口上的 I/O。

> 注意：无头交互模式可以与常规的图形显示模式同时共存。

TODO：描述禁用硬件图形显示的各类选项

## 将终端模拟器连接到 Theseus

目前，我们只在通过 QEMU 这类 VMM 连接的虚拟串口上测试过此功能，但它对于真实的硬件串口同样适用。

当 Theseus 运行在虚拟机或另一台物理机器上时，我们建议在宿主机上使用终端模拟器程序连接到 Theseus 机器上的串口设备。
可选的程序包括：

- screen
- picocom
- minicom

默认情况下，Theseus 的 Makefile 会以两个串口（COM1 和 COM2）启动 QEMU，宿主机可以连接到它们并交换数据。
第一个串口 COM1 连接到启动 QEMU 进程的那个终端的 `stdio` 流。
该流用于系统日志以及控制 QEMU，因此最好使用 COM2 单独与 Theseus 交互，以免无头虚拟终端被日志语句污染。
第二个串口 COM2 连接到一个由 QEMU 分配的动态分配的伪终端（PTY）。要连接到它，请在 QEMU 首次启动时查看其输出，找到类似下面的一行：

```
char device redirected to /dev/pts/3 (label serial1-base)
```

这告诉你 QEMU 把客户 Theseus 虚拟机上的第二个串口（COM2）连接到了位于 `/dev/pts/3` 的 Linux PTY 设备。
注意，QEMU 对串口使用从 0 开始的索引，因此它的 "serial1" 标签指的是第二个串口，也就是我们的 "SERIAL2"（在 x86 上是 COM2）。

现在，一旦 QEMU 运行起来，你就可以把宿主机上的终端模拟器连接到 Theseus 中的串口，Theseus 会向该终端模拟器发出交互式命令。
为此，运行以下任意一条命令，然后按任意键即可启动终端提示符：

- screen /dev/pts/3
- picocom /dev/pts/3
- minicom -D /dev/pts/3

注意，有些程序（尤其是 `minicom`）在按下 `Backspace` 键时不一定会发送预期的值。
因此，如果你在按下 `Backspace` 时遇到了不符合预期的行为，需要确保你的程序在按下 `Backspace` 时发送的是正确的 ASCII `DEL`（0x7F）字符值，而不是 ASCII `BS`（0x08），后者只会把光标向左移动一个字符。
根据我们的经验，`screen` 和 `picocom` 的行为符合预期，而 `minicom` 则不然。
要修改 `minicom` 的默认行为，可以这样做：

- 按 Ctrl + A 两次，打开屏幕底部的元控制栏
- 按 T 打开 "Terminal Settings" 菜单
- 按 B 切换 "Backspace key sends" 设置。
    - 你需要把它设为 DEL，而不是 BS。

这两个串口都可以在 QEMU 中分别通过环境变量 `SERIAL1` 和 `SERIAL2` 来修改，不过再说一次，我们建议在虚拟环境中只使用 `SERIAL2`。
在真实硬件上只有一个串口，因此必须使用 COM1，此时你可以禁用系统日志，或者把它初始化到另一个串口（例如 COM2），以避免系统日志的打印输出污染连接到 COM1 的终端模拟器。
