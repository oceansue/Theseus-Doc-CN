# 在虚拟机或真实硬件上运行 Theseus

我们已经测试过 Theseus 能否在多种环境中正常运行，目前仅限于 x86_64：

- 虚拟机模拟器：QEMU、bochs、VirtualBox、VMware Workstation Player。
- 真实硬件：Intel NUC 设备、Supermicro 服务器、各种 Thinkpad 笔记本，以及搭载技嘉（Gigabyte）主板的 PC。

目前，主要的限制因素是设备需要通过传统的 BIOS（而非 UEFI）来支持从 USB 或 PXE 引导；对 UEFI 的支持仍在开发中。

请注意，Theseus 尚未完全成熟，在你的自有硬件上引导运行的风险需自行承担。在这样做之前，请务必备份所有重要文件。

如果你在任何虚拟或真实硬件平台上引导 Theseus 时遇到了问题，请查看 [GitHub 上的开放 issue](https://github.com/theseus-os/Theseus/issues/)，看看是否已经有人报告过你的问题或尝试修复它。
如果是这样，请留下一条评论描述你的经历，或者提交一个新的 issue，帮助 Theseus 的开发者们朝着支持你的硬件环境努力！
