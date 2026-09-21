# 关于 Theseus 的论文与演讲

多年来，Kevin Boos、Ramla Ijaz 以及其他 Theseus 合作者围绕 Theseus OS 及相关主题做过许多演讲。
本页精选收录了这些演讲的幻灯片（包括一些视频录像），以及精选的同行评审学术论文与学位论文列表。

## 精选论文与学位论文

- [OSDI 2020] **[Theseus: an Experiment in Operating System Structure and State Management](https://www.usenix.org/conference/osdi20/presentation/boos)**
    - 这篇主要论文描述了 Theseus 的设计原则、实现、评估与局限。
    - [论文（PDF）](https://www.usenix.org/system/files/osdi20-boos.pdf) — 
[OSDI 2020 视频演讲](https://www.youtube.com/watch?v=i1pLDZKtlBI) — 
[OSDI 2020 短视频](https://www.youtube.com/watch?v=T0Du5vps9aU) — 
[幻灯片（PDF）](https://www.usenix.org/sites/default/files/conference/protected-files/osdi20_slides_boos.pdf)
- [[KISV 2023](https://kisv-workshop.github.io/program/)] **[Leveraging Rust for Lightweight OS Correctness](https://dl.acm.org/doi/10.1145/3625275.3625398)**
    - 一篇关于扩展语内设计（intralingual design）、并采用混合方法（类型系统加形式化验证）来证明 Theseus 内存管理子系统的轻量级正确性保证的论文。
    - [论文（PDF）](https://dl.acm.org/doi/pdf/10.1145/3625275.3625398)
- Kevin Boos 博士学位论文：[Theseus: Rethinking Operating Systems Structure and State Management](https://scholarship.rice.edu/handle/1911/109201)
- Ramla Ijaz 硕士学位论文：[Exploring Intralingual Design in Operating Systems](https://scholarship.rice.edu/handle/1911/109609)

### 其他已发表的作品

- [OSDI 2022] 海报：[Correct and Performant Device Drivers via Intralingual Design](https://www.usenix.org/conference/osdi22/poster-session)
    - 对一项进行中工作的概述：利用形式化验证 + 语内设计来打造更好的设备驱动。
    - [海报 PDF](https://www.theseus-os.com/kevinaboos/docs/OSDI%202022%20Poster.pdf)
- [PLOS 2017] [Theseus: A State Spill-free Operating System](https://www.sigops.org/s/conferences/sosp/2017/workshops.html)
    - [论文 PDF](https://www.theseus-os.com/kevinaboos/docs/theseus_plos2017.pdf) —— 一篇更简短、观点已过时的论文，介绍 Theseus 的早期设计。
    - 已被 OSDI 2020 论文取代。
- [EuroSys 2017] [A Characterization of State Spill in Modern Operating Systems](https://dl.acm.org/doi/10.1145/3064176.3064205)
    - 引入并研究了 state spill（状态溢出）这一概念。
    - 这是我们日后 Theseus 工作的动机来源。

## 精选演讲与幻灯片

- [Theseus: a Rust-native OS for Safety and Reliability（2023 年 9 月）](https://docs.google.com/presentation/d/e/2PACX-1vSq144Pl5Ql02OP9zq80wuy7iI1GwUNfCwUelpKay2qeIis4uMY2qOfSgIKeG7Rb053fMoVXXHa3ka9/pub?start=false&loop=false) – [[视频演讲](https://www.bilibili.com/video/BV1d34y1373n/)]
- [Theseus 如何使用 Rust，以及 Rust 带来的挑战（2022 年初）](https://docs.google.com/presentation/d/e/2PACX-1vQ2InjW_5kpdepoJ9vdsH-B1G4mvcjohcj_CA2dzx-tVRz0ee52qo1bwCQ7TnDGE9PiE5doW4sIO_7W/pub?start=false&loop=false)
- [安全语言操作系统的工作原理，附 Theseus 实例](https://docs.google.com/presentation/d/e/2PACX-1vSa0gp8sbq8S9MB4V-FYjs6xJGIPm0fsZSVdtZ9U2bQWRX9gngwztXTIJiRwxtAosLWPk0v60abDMTU/pub?start=false&loop=false) — 
[[视频演讲](https://www.youtube.com/watch?v=n7r8zO7SodE)]
- [Theseus 设计概述（2020 年末）](https://docs.google.com/presentation/d/e/2PACX-1vR96Oh5iiV2XTPv5KfjGykxoqqo1auGfvxahkMXxQImZsO5B9sXl5h1BEmIzBbb8Pj8lr_NDx4WUr-y/pub?start=false&loop=false)
- [面向程序员的 Theseus 入门](https://docs.google.com/presentation/d/e/2PACX-1vQuDoQq0mKf2r4m3xMeZ4LVao2Ngh6HPHWCdJASW9uasaRSbWaRvHc2LoZD2bTpIOHUkKeN6VjP8KJG/pub?start=false&loop=false)
- [Kevin Boos 博士答辩：深入剖析 Theseus OS 研究](https://docs.google.com/presentation/d/e/2PACX-1vTq5L-t1F8tSmIRiUaFLtcGSY6Bm8CSh7p4j8GuTqrUOu3OzUckXAW-TWiYCueAndunVpBgB51Hoamh/pub?start=false&loop=false) — 
[[视频演讲](https://www.youtube.com/watch?v=JWGPLVYXZlU)]
- [Ramla Ijaz 硕士答辩：深入剖析 Theseus 中的语内设计](https://docs.google.com/presentation/d/e/2PACX-1vR5zQMf3AQYMITczojVizQBd1JHtuKChIEVBoBPtnXu59EgFpCZKb1oxbMbO2oSxBm_5pC3foK3V-rK/pub?start=false&loop=false)
- [Theseus 中的 crate 加载/管理与 crate 命名空间](https://docs.google.com/presentation/d/e/2PACX-1vSo0D-hnRljdp7DT19kyTv09RbE-4mnQKqe85ljoK9DeHIS8mCMpThQwcsEaAe6X9g0QGqGI0IahHwK/pub?start=false&loop=false)
- [在 Theseus 中支持栈展开（unwinding）与异常/Panic（2019 年末）](https://docs.google.com/presentation/d/e/2PACX-1vSm-ybVzbGBeorvTeNfxzfKLV61CrYJgNk9K1seRESrthr9L7i5suPtpKfHBdqelJiN1X2LToGtr18T/pub?start=false&loop=false)
- [为 Theseus 实现基础的应用程序支持（2018 年年中）](https://docs.google.com/presentation/d/e/2PACX-1vQEvnxBUM9PJgYYvxh0vj894rqnkeZBgH45-FijHMrXB-IgPIysbkiQTbn7LxHnkqDIGGrY_H9o42c9/pub?start=false&loop=false)
- [在 Theseus 上支持多核处理器](https://docs.google.com/presentation/d/e/2PACX-1vRBCZsC9QzZHX8rSSSVsLBJ9AcxvddRmeNZlkbzCkOnIfrOVxqnvkHlrTIZ_CAn_MOUGmxkaPVijkJP/pub?start=false&loop=false)
- [实现 crate 的动态加载与链接（2017 年末）](https://docs.google.com/presentation/d/e/2PACX-1vSsuHSIU0Iq66FgbNldaDDRlvez4dOhz6fFvJXF5O885uxpUtbcbr7EpX2rxqDguVlGQziE6gMLwiDM/pub?start=false&loop=false)

---

- [设想：验证语内不变量](https://docs.google.com/presentation/d/e/2PACX-1vRUvgprQ69r1JYypkswcWVrv_18BidWKrKgKVn4wiMmAHJUDz4Dhx7qv7Dozw2ljU9sllKqsRIHJNlJ/pub?start=false&loop=false)
- [Rust 与 C 的对比，附简短的 Rust 入门](https://docs.google.com/presentation/d/e/2PACX-1vQYomAnfTNucuCqYgNkPaxpIdrhPxil9Qzle_6-xd7TYfdEBlgML0B3vztdNC2odwc25dLzW3XsithZ/pub?start=false&loop=false) — 
[[视频演讲](https://www.youtube.com/watch?v=mmJiwscpB4o)]
