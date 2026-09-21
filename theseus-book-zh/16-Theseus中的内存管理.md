# Theseus 中的内存管理

与其他操作系统管理内存的方式相比，内存管理是 Theseus 设计中最独特的方面之一。

## 单一*虚拟*地址空间

如前文所述，Theseus 是一个单一地址空间（Single Address Space，SAS）操作系统，也就是说，所有内核实体、库和应用程序都被加载到同一个地址空间中，并在其中运行。这之所以可行，一方面源于精心的设计，另一方面则是因为它依靠基于 Rust 类型和内存安全的隔离机制，而不是基于硬件的内存保护。

话虽如此，Theseus 的单一地址空间是一个*虚拟*地址空间，而非物理地址空间；
所有被解引用的 Rust 层指针以及所有被访问的地址都是虚拟地址。
虽然从技术上讲，Theseus 完全可以不使用虚拟内存而直接操作物理内存地址，但使用虚拟地址给我们带来了许多好处，例如更容易实现连续内存分配、可以用保护页（guard page）来捕捉栈溢出，等等。

## 类型与术语

Theseus 使用精确、专门的术语以及专用的类型，以避免因混淆物理内存和虚拟内存而导致的错误。
下表简要描述了各种基本内存类型，并附有指向其源码级文档的链接：

| 类型说明 | 虚拟内存类型 | 物理内存类型 |
| --- | --- | --- |
| 一个内存地址 | [`VirtualAddress`](https://theseus-os.github.io/Theseus/doc/memory_structs/struct.VirtualAddress.html) | [`PhysicalAddress`](https://theseus-os.github.io/Theseus/doc/memory_structs/struct.PhysicalAddress.html) |
| 一块内存 | [`Page`](https://theseus-os.github.io/Theseus/doc/memory_structs/struct.Page.html) | [`Frame`](https://theseus-os.github.io/Theseus/doc/memory_structs/struct.Frame.html) |
| 一段连续的内存块范围 | [`PageRange`](https://theseus-os.github.io/Theseus/doc/memory_structs/struct.PageRange.html) | [`FrameRange`](https://theseus-os.github.io/Theseus/doc/memory_structs/struct.FrameRange.html) |
| 内存块的分配器 | [`page_allocator`](https://theseus-os.github.io/Theseus/doc/page_allocator/index.html) | [`frame_allocator`](https://theseus-os.github.io/Theseus/doc/frame_allocator/index.html) |

### 地址

在 Theseus 中，虚拟地址和物理地址各自拥有专门且相互独立的类型，二者**不可互操作**。
这是为了确保程序员能够明确地知道自己正在使用哪一种地址，从而不会意外地把两者混为一谈。
`VirtualAddress` 和 `PhysicalAddress` 的构造函数还会保证你无法创建无效的地址，并保证整个系统中使用的所有地址在形式上都是规范的（canonical），这一点依据的是硬件架构的要求。

对于 64 位架构，`VirtualAddress` 的可能取值范围是从 `0` 到 `0xFFFFFFFFFFFFFFFF`，该范围内的所有规范地址都可以使用。
然而，虽然 `PhysicalAddress` 的可能取值也覆盖同样的范围，但整个物理地址空间中存在大量"空洞"，它们对应着并不存在、不可使用的物理地址；这些空洞的具体位置取决于硬件，通常要到运行时由操作系统向引导加载程序询问之后才能知晓。
因此，你可以确信每一个规范的虚拟地址都真实存在且可以使用，但却不能对每一个规范的物理地址都做出同样的保证。

### `Page`、`Frame` 与范围类型

一块虚拟内存被称为一个 `Page`（页），而一块物理内存被称为一个 `Frame`（帧）。
`Page` 和 `Frame` 的大小相同，通常为 4KiB（4096 字节），但最终取决于硬件。
这些内存块是硬件的内存管理单元（MMU）能够操作的最小基本单元，也就是说，从硬件的角度来看它们是不可再分的。
换句话说，MMU 硬件无法把任何小于一个 `Page` 的内存块映射到任何小于一个 `Frame` 的内存块上。

一个 `Page` 有一个起始 `VirtualAddress` 和一个结束 `VirtualAddress`；例如，某个 `Page` 可能（以闭区间方式）起始于地址 `v0x5000`，（以开区间方式）结束于 `v0x6000`。
类似地，一个 `Frame` 有一个起始 `PhysicalAddress` 和一个结束 `PhysicalAddress`，例如从 `p0x101000` 到 `p0x102000`。
我们可以说某个 `Page` 在其边界之内包含了某个 `VirtualAddress`，同样也可以说某个 `Frame` 包含了某个 `PhysicalAddress`。
虽然 `Page` 和 `Frame` 内部都有编号，但我们通常用它们的起始地址来标识它们，例如说"起始地址为 `v0x9000` 的页"，而不是"第 9 页"。
就其本质而言，`Page` 与 `PhysicalAddress` 没有任何关联；同样地，`Frame` 与 `VirtualAddress` 也没有任何关联。

为了方便起见，Theseus 提供了专门的"范围"（range）类型，用来表示一段连续的虚拟 `Page` 或物理 `Frame`。
它们是两端都包含的区间；更多信息请参见我们自定义的 [`RangeInclusive`](https://theseus-os.github.io/Theseus/doc/range_inclusive/index.html) 类型，它取代了 Rust 内置的 `core::ops::RangeInclusive` 类型。
这些类型实现了 Rust 标准的 [`IntoIterator`] trait，因而可以方便地遍历范围中的所有页或帧。

Theseus 借助宏来生成上述基本类型的实现，
因为它们在虚拟内存与物理内存两个类别之间是对称的。
这保证了 `VirtualAddress` 与 `PhysicalAddress` 拥有相同的接口（公开方法）；`Page` 与 `Frame` 之间也是如此，其余类型依此类推。

### 页分配器与帧分配器

Theseus 的[页分配器](https://theseus-os.github.io/Theseus/doc/page_allocator/index.html)（page allocator）和[帧分配器](https://theseus-os.github.io/Theseus/doc/frame_allocator/index.html)（frame allocator）在设计与实现上实际上是相同的，只是前者分配虚拟内存的 `Page`，而后者分配物理内存的 `Frame`。

虽然底层实现可能随时间推移而变化，但这两个分配器的通用接口是一致的。

- 你可以在任意地址请求新分配一个或多个 Page 或 Frame，只有在没有剩余虚拟内存或物理内存时才会失败。
- 你可以要求分配从包含某个特定地址的 Page 或 Frame 开始，但如果包含该地址的 Page 或 Frame 已经被分配出去了，请求就会失败。
- 你还可以指定新分配至少需要覆盖的字节数，该数值会被向上取整到最近的 Page 或 Frame 粒度。
    - 这些分配器无法分配任何小于单个 Page 或 Frame 的内存；若需要更小的分配，就应当使用动态分配的堆内存。
- 两个分配器都支持"保留"（reserved）内存区域的概念，这类区域只能由特定的内核实体使用，例如在引导/初始化早期运行的内存处理函数。
    - frame_allocator 利用保留区域来为特定用途保留某些物理内存范围，例如存放来自引导加载程序的早期引导信息的内存，或者存放实际的内核可执行代码的内存。
- 两个分配器还都支持在堆建立之前进行早期内存分配，使 Theseus 能够借助静态数组中的一系列小型、以静态方式追踪的分配来引导（bootstrap）其动态内存管理系统。

Theseus 中的页分配器和帧分配器并不直接允许你*访问*内存；你仍然必须把虚拟 `Page` *映射*到物理 `Frame` 上，才能访问其中的内存。
我们会使用更多专用类型来表示这一过程，下文将予以介绍。

在 Theseus 中，与其他操作系统一样，只有一个帧分配器，因为只有一套物理内存——也就是连接到计算机主板上的那块实际的系统内存（RAM）。
如果存在多个帧分配器，它们可以各自独立地从同一个唯一的物理地址空间中分配物理内存块，这在逻辑上是无效且不健全的。
与其他多地址空间操作系统不同，Theseus 同样只有一个页分配器，因为我们只有一个虚拟地址空间。
所有的页都必须从这唯一的虚拟地址空间中分配，因此只需要一个页分配器。

## 高级内存类型

上述"基本"类型侧重于通过类型强制的清晰性来防止简单的程序员失误，
而下面的"高级"类型则力求通过类型自身的不变量来防止复杂得多的错误。

- [`AllocatedPages`](https://theseus-os.github.io/Theseus/doc/page_allocator/struct.AllocatedPages.html)：虚拟内存中连续的一段 Page，并且只有唯一的独占所有者。
    - 只能通过向 page_allocator 请求分配来获得。
- [`AllocatedFrames`](https://theseus-os.github.io/Theseus/doc/frame_allocator/struct.AllocatedFrames.html)：物理内存中连续的一段 Frame，并且只有唯一的独占所有者。
    - 只能通过向 frame_allocator 请求分配来获得。
- [`MappedPages`](https://theseus-os.github.io/Theseus/doc/memory/struct.MappedPages.html)：虚拟地址连续的一段页，它们已被映射到物理帧上，并且只有唯一的独占所有者。
    - 我们将在下一节讨论内存映射时介绍 MappedPages。

基本类型与高级类型的主要区别在于，高级类型能够保证*独占性*。
因此，如果你持有的是一个从 `v0x6000` 到 `v0x8000` 的 `PageRange`，那么没有任何机制可以阻止其他实体创建一个与之重叠的类似 `PageRange`，例如从 `v0x7000` 到 `v0x9000` 的范围。
然而，如果你持有的是一个从 `v0x6000` 到 `v0x8000` 的 `AllocatedPages`，那么就可以保证**整个系统中没有任何其他实体**持有包含其中任何页的 `AllocatedPages` 对象。
这是一个强有力的保证，使我们能够在分配、映射和访问内存时建立更强的隔离性与安全性不变量，下一节将对此加以说明。
