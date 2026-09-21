# 从 U 盘引导 Theseus

要通过 USB 引导，只需运行

```sh
make boot usb=sdc
```

其中 `sdc` 是 USB 磁盘本身的设备节点*（**而不是**像 sdc2 那样的分区）*。
操作系统镜像（.iso 文件）会被写入该 U 盘。

在 WSL 或其他不存在 `/dev` 设备节点的宿主环境中，你可以直接运行 `make iso`，然后把 `build/` 目录中的 `.iso` 文件刻录到 U 盘上。
例如，在 Windows 上我们推荐使用 [Rufus](https://rufus.ie/) 来刻录 ISO。

之后，一旦可引导的 U 盘准备就绪，把它插入你的 PC，重启或开机，然后在 BIOS 或传统引导设备界面中选择该 USB 设备即可。
