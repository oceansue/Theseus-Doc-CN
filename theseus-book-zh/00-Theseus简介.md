# Theseus 简介

*注意：关于 Theseus 的总体介绍和快速上手指南，请参阅[顶层 README](https://github.com/theseus-os/Theseus#readme)。*

Theseus 是一个从头开始用 [Rust](https://www.rust-lang.org/) 编写的新操作系统，用于探索新颖的操作系统结构、更好的状态管理，以及如何利用**语内设计（intralingual design）**原则，把资源管理等操作系统职责转移到编译器中去。

请继续阅读下一章以深入了解 Theseus，或者也可以查看我们[发表的学术论文](https://www.theseus-os.com/Theseus/book/misc/papers_presentations.html)，深入研究 Theseus 背后的研究与设计理念。

### 名字的由来？

> 忒修斯与雅典的青年们从克里特岛归来时所乘的那艘船有三十支桨，雅典人一直将它保存到法勒鲁姆的德米特里（Demetrius Phalereus）时代，因为人们会把逐渐腐朽的旧木板取下，换上新的、更坚固的木料。如此一来，这艘船便成为哲学家们讨论"事物如何生长"这一逻辑问题时反复援引的著名例证：一派认为这艘船依然是原来的那艘船，另一派则坚持认为它已不是同一艘船。
> 　—— *普鲁塔克（Plutarch），《忒修斯传》*

"Theseus"这个名字的灵感来自*忒修斯之船*（The Ship of Theseus），一个古希腊的形而上学悖论与思想实验，它思考的问题是："如果你逐个替换一个物体的每一个组成部分，那么重建后的这个物体还是原来那个物体吗？"

虽然我们并不试图回答这个问题，但我们确实希望让系统中任何一层、每一个操作系统组件都能在运行时被替换，而无需重启。这种轻松而任意的*在线演化（live evolution）*目标，正是 Theseus 最初（至今仍是）的动机之一。
