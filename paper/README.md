# Theseus 相关论文库（原文 + 中文翻译）

本目录收录《The Theseus OS Book（中文版）》第 32 章（[关于 Theseus 的论文与演讲](../theseus-book-zh/32-关于Theseus的论文与演讲.md)）中列出的学术论文与学位论文：每篇一份原文 PDF + 一份中文翻译（或导读）。

> 翻译约定见各文件开头的"论文信息块"。短文为**全文翻译**；两本学位论文篇幅过大（149 / 60 页），提供**中文导读**（摘要全译 + 目录全译 + 逐章要点）。
> 图表以"【图 N：…】"形式标注，原图请对照本目录下的 PDF。

## 论文清单

| # | 论文（中文题名链接到译文） | 发表 | 原文 PDF | 译文 |
| --- | --- | --- | --- | --- |
| 1 | [Theseus：操作系统结构与状态管理的一次实验](OSDI2020-中文翻译.md) | USENIX OSDI 2020 | [OSDI2020-Theseus-Experiment-OS-Structure.pdf](OSDI2020-Theseus-Experiment-OS-Structure.pdf) | 全文翻译 |
| 2 | [利用 Rust 实现操作系统的轻量级正确性保证](KISV2023-中文翻译.md) | KISV 2023（SOSP'23 Workshop） | [KISV2023-Leveraging-Rust-Lightweight-OS-Correctness.pdf](KISV2023-Leveraging-Rust-Lightweight-OS-Correctness.pdf) | 全文翻译 |
| 3 | [一种无状态溢出的操作系统 Theseus](PLOS2017-中文翻译.md) | PLOS 2017（SOSP'17 Workshop） | [PLOS2017-Theseus-State-Spill-free-OS.pdf](PLOS2017-Theseus-State-Spill-free-OS.pdf) | 全文翻译（早期设计，部分观点已被 OSDI'20 取代） |
| 4 | [现代操作系统中状态溢出现象的刻画](EuroSys2017-中文翻译.md) | EuroSys 2017 | [EuroSys2017-State-Spill-Characterization.pdf](EuroSys2017-State-Spill-Characterization.pdf) | 全文翻译 |
| 5 | [通过语内设计实现正确且高性能的设备驱动（海报）](OSDI2022-海报-中文翻译.md) | USENIX OSDI 2022 Poster | [OSDI2022-Poster-Intralingual-Device-Drivers.pdf](OSDI2022-Poster-Intralingual-Device-Drivers.pdf) | 全文翻译 |
| 6 | [Theseus：重构操作系统的结构与状态管理（博士论文）](Boos-PhD-中文导读.md) | Rice University, 2020 | [Boos-PhD-2020-Theseus-Rethinking-OS-Structure.pdf](Boos-PhD-2020-Theseus-Rethinking-OS-Structure.pdf) | 中文导读（149 页） |
| 7 | [探索操作系统中的语内设计（硕士论文）](Ijaz-MS-中文导读.md) | Rice University, 2020 | [Ijaz-MS-2020-Intralingual-Design-OS.pdf](Ijaz-MS-2020-Intralingual-Design-OS.pdf) | 中文导读（60 页） |

## 原文出处

- **OSDI 2020**：USENIX 开放获取 —— <https://www.usenix.org/conference/osdi20/presentation/boos>
- **KISV 2023**：ACM DL —— <https://dl.acm.org/doi/10.1145/3625275.3625398>（PDF 取自林中教授实验室站点 <https://www.yecl.org/publications/kisv2023ijaz.pdf>）
- **PLOS 2017**：作者站点 —— <https://www.theseus-os.com/kevinaboos/docs/theseus_plos2017.pdf>
- **EuroSys 2017**：ACM DL —— <https://dl.acm.org/doi/10.1145/3064176.3064205>（PDF 取自 <https://www.yecl.org/publications/boos2017eurosys.pdf>）
- **OSDI 2022 海报**：作者站点 —— <https://www.theseus-os.com/kevinaboos/docs/OSDI%202022%20Poster.pdf>
- **博士论文 / 硕士论文**：Rice 大学数字学术档案 —— <https://scholarship.rice.edu/handle/1911/109201> 、 <https://scholarship.rice.edu/handle/1911/109609>

## 建议阅读顺序

1. 先读 **PLOS 2017**（早期构想，篇幅短）与本书第 01 章，建立对 Theseus 结构的直觉；
2. 精读 **OSDI 2020**（核心论文，含完整设计与评估）；
3. 对正确性/形式化验证感兴趣，读 **KISV 2023** 与**硕士论文导读**；
4. 需要实现级细节与完整演进史时，按**博士论文导读**的指引选择性阅读原书章节。
