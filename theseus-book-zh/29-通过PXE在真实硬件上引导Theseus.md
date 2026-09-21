# 通过 PXE 在真实硬件上引导 Theseus

以下步骤结合了 OSTechNix 上的[这篇](https://www.ostechnix.com/how-to-install-pxe-server-on-ubuntu-16-04/)为 Ubuntu 搭建 PXE 的指南，以及 Andrew Wells 的[这篇](https://wellsie.net/p/286/)关于如何在 PXE 中使用任意 ISO 的指南。

PXE 可用于把 Rust 加载到通过局域网（LAN）与开发用主机相连的目标计算机上。要把主机配置为 PXE 服务器，首先进入 Theseus 所在的目录并运行以下命令来制作 Theseus ISO：
`make iso`

然后，你需要搭建测试机器将要访问的 TFTP 服务器和 DHCP 服务器。

## 搭建 TFTP 服务器

首先，安装 TFTP 所需的所有软件包和依赖：
`sudo apt-get install apache2 tftpd-hpa inetutils-inetd nasm`
编辑 tftp-hpa 的配置文件：
`sudo nano /etc/default/tftpd-hpa`
加入以下几行：

```
RUN_DAEMON="yes"
OPTIONS="-l -s /var/lib/tftpboot"
```

接着，打开编辑器修改 `inetd` 配置文件：
`sudo nano /etc/inetd.conf`
并加入：
`tftp dgram udp wait root /usr/sbin/in.tftpd /usr/sbin/in.tftpd -s /var/lib/tftpboot`

重启 TFTP 服务器并检查它是否正在运行：

```sh
sudo systemctl restart tftpd-hpa
sudo systemctl status tftpd-hpa
```

如果 TFTP服务器无法启动，并且提示某个套接字正在使用，请重新打开 tftp-hpa 配置文件，把 `TFTP_ADDRESS=":69"` 所在那一行的端口改成 `6969`，然后重启 TFTP 服务器。

## 搭建 DHCP 服务器

首先，安装 DHCP 服务器所需的软件包：
`sudo apt-get install isc-dhcp-server`

然后运行 `ifconfig` 查看可用的网络设备，找到网络设备名，例如 `eth0`。

编辑 `/etc/default/isc-dhcp-server` 配置文件，把上一步得到的网络设备名加入 "INTERFACES"。以我为例，这一项是 `INTERFACES="eth0"`。

配置一个任意的 IP 地址，它会在下一步中用到：
`sudo ifconfig <network-device-name> 192.168.1.105`
每当充当服务器的计算机重启之后，可能都需要重新执行这条命令。

编辑 `/etc/dhcp/dhcpd.conf` 文件，取消 `authoritative;` 一行的注释，并添加一个类似下面这样的子网配置：

```
subnet 192.168.1.0 netmask 255.255.255.0 {
  range 192.168.1.20 192.168.1.30;
  option routers 192.168.1.1;
  option broadcast-address 192.168.1.255;
  default-lease-time 600;
  max-lease-time 7200;
}

allow booting;
allow bootp;
option option-128 code 128 = string;
option option-129 code 129 = text;
next-server 192.168.1.105;
filename "pxelinux.0";
```

重启 DHCP 服务器并检查它是否正在运行：

```sh
sudo systemctl restart isc-dhcp-server
sudo systemctl status isc-dhcp-server
```

## 把 Theseus ISO 装入 TFTP 服务器

为了让 TFTP 服务器能够加载 Theseus，我们需要在引导目录中放入 Theseus ISO 和一个 memdisk 文件。要获得 memdisk 文件，先下载包含它的 syslinux。

```sh
wget https://www.kernel.org/pub/linux/utils/boot/syslinux/syslinux-5.10.tar.gz
tar -xzvf syslinux-*.tar.gz
```

然后进入 memdisk 目录并编译。

```sh
cd syslinux-*/memdisk
make memdisk
```

接下来，为 Theseus 创建一个 TFTP 引导目录，并把 memdisk 二进制文件连同 Theseus ISO 一起复制进去：

```sh
sudo mkdir /var/lib/tftpboot/theseus
sudo cp /root/syslinux-*/memdisk/memdisk /var/lib/tftpboot/theseus/
sudo cp /Theseus/build/theseus-x86_64.iso /var/lib/tftpboot/theseus/
```

进入 PXE 配置文件：
`sudo nano /var/lib/tftpboot/pxelinux.cfg/default`
并加入以下内容，把 Theseus 添加为一个菜单项：

```
label theseus
    menu label Theseus
    root (hd0,0)
    kernel theseus/memdisk
    append iso initrd=theseus/theseus-x86_64.iso raw
```

最后，再重启一次 DHCP 服务器，并确认它正在运行：

```sh
sudo systemctl restart isc-dhcp-server
sudo systemctl status isc-dhcp-server
```

在目标计算机上，进入 BIOS，开启传统引导模式（Legacy boot mode），并把网络引导设为最优先的引导选项。目标计算机重启之后，应当会进入一个菜单，其中显示了引导进入 Theseus 的选项。

## 后续的 PXE 使用

首次搭建好 PXE 之后，你可以运行 `make pxe` 来制作更新后的 ISO，删除旧的 ISO，并把新的 ISO 复制到 TFTP 引导目录中。此后，重启目标计算机即可引导新版本的 Theseus。如果在 DHCP 服务器第一次正常工作之后重启它时遇到问题，一种可行的解决办法是用前面用过的命令确认 IP 地址是否仍然是你想要的那个：
`sudo ifconfig <network-device-name> 192.168.1.105`
