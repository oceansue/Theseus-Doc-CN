# 使用 QEMU 进行 PCI 设备直通

PCI 直通（PCI passthrough）可以让客户操作系统直接访问某个物理设备。
以下步骤结合了[这篇](https://www.ibm.com/docs/en/linux-on-systems?topic=vfio-host-setup)关于 VFIO 直通设备主机配置的指南，以及[这份](https://www.kernel.org/doc/Documentation/vfio.txt)关于 VFIO 的内核文档。

为设备准备 PCI 直通主要有三个步骤：

1. 查找设备信息
2. 将设备从当前驱动中分离
3. 将设备挂接到 VFIO 驱动

完成这些步骤之后，就可以使用 **vfio** 标志把设备的槽位信息传递给 QEMU。例如，对于设备 59:00.0，我们运行：

```sh
make run vfio=59:00.0
```

### 查找设备信息

首先，运行 `lspci -vnn` 来找到槽位信息、该设备当前使用的内核驱动，以及你想使用的设备的厂商 ID（vendor ID）和设备代码（device code）。
下面是一张我们希望通过 PCI 直通访问的 Mellanox 以太网卡的示例输出：

```
59:00.0 Ethernet controller [0200]: Mellanox Technologies MT28800 Family [ConnectX-5 Ex] [15b3:1019]
	Subsystem: Mellanox Technologies MT28800 Family [ConnectX-5 Ex] [15b3:0008]
	Flags: bus master, fast devsel, latency 0, IRQ 719, NUMA node 1
	Memory at 39bffe000000 (64-bit, prefetchable) [size=32M]
	Expansion ROM at bf200000 [disabled] [size=1M]
	Capabilities: <access denied>
	Kernel driver in use: mlx5_core
	Kernel modules: mlx5_core
```

### 将设备从当前驱动中分离

要将设备从其内核驱动中分离，请运行以下命令，并把 `slot_info` 和 `driver_name` 替换为你在上一步中获得的值。

```sh
echo $slot_info > /sys/bus/pci/drivers/$driver_name/unbind
```

在上面的示例中，对应的命令是：

```sh
echo 0000:59:00.0 > /sys/bus/pci/drivers/mlx5_core/unbind
```

如果此时运行 `lspci -v`，你会看到该设备已经不再挂接任何内核驱动。

### 将设备挂接到 VFIO 驱动

首先，通过以下方式加载 VFIO 驱动：

```sh
modprobe vfio-pci
```

要挂接新的驱动，请运行以下命令，并把 `vendor_id` 和 `device_code` 替换为你在第一步中获得的值。

```sh
echo $vendor_id $device_code > /sys/bus/pci/drivers/vfio-pci/new_id
```

例如：`echo 15b3 1019 > /sys/bus/pci/drivers/vfio-pci/new_id`

现在，就可以在直接访问该设备的情况下启动 QEMU 了。

### 把设备归还给主机操作系统

要复位该设备，你可以重启系统，也可以使用以下命令把设备归还给主机操作系统（将 `$slot_info` 替换为之前获得的值）：

```sh
echo 1 > /sys/bus/pci/devices/$slot_info/remove    
echo 1 > /sys/bus/pci/rescan
```

### 注意：非特权用户的访问权限

要让非特权用户也能访问该 VFIO 设备，需要先找到该设备所属的 IOMMU 组：

```sh
readlink /sys/bus/pci/devices/$slot_info/iommu_group
```

例如：

```sh
readlink /sys/bus/pci/devices/0000:59:00.0/iommu_group
```

我们会得到如下输出，其中的 `74` 就是组号：

> ```
> ../../../../kernel/iommu_groups/74
> ```

最后，通过以下命令把访问权限授予当前用户：

```sh
chown $USER /dev/vfio/$group_number
```
