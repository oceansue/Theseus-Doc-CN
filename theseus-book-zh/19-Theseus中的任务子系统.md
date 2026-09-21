# Theseus 中的任务子系统

Theseus 的任务子系统完整实现了[多任务](https://en.wikipedia.org/wiki/Computer_multitasking)支持，
即多个不同的任务可以在同一组共享资源（也就是 CPU 和内存）之上并发地执行。

由于 Theseus 是一个单一地址空间（SAS）操作系统，它并没有为每个任务提供独立的地址空间，因此也不遵循经典的 POSIX/类 Unix 的"进程"抽象——在该抽象中，进程是一组在相同地址空间中执行同一程序的线程。
你可以把 Theseus 中的任务（task）等同于其他系统中的线程；"任务"与"线程"这两个术语可以互换使用。
你也可以把 Theseus 整体看作单个"进程"，因为所有 Task 都在同一个地址空间中执行，但进程与 Theseus 之间的类比也就到此为止。

总体而言，Theseus 任务管理子系统所暴露的接口遵循 Rust 标准库的[线程模型](https://doc.rust-lang.org/std/thread/)，二者有诸多相似之处：

- 你可以以一个函数或闭包作为入口点来派生（创建）一个新任务。
- 你可以使用便捷的构建器（builder）模式来自定义新任务。
- 你可以通过 [`join`](https://www.theseus-os.com/Theseus/doc/task/struct.JoinableTaskRef.html#method.join) 一个任务来等待它退出。
- 你可以使用任何标准同步类型来进行任务间通信，例如共享内存或通道。
- 你可以捕获任务中发生 panic 或异常之后的栈展开行为。

这样看来，Theseus 中的任务实际上是语言层面的绿色线程（green thread）概念与操作系统层面的原生线程的结合体。

## `Task` 结构体

系统中当前存在的每个任务都对应一个 `Task` 结构体实例。
任务通常被视为一种*执行上下文*，任务结构体包含了与给定程序代码执行相关的关键信息。
与其他操作系统相比，Theseus 中的 [`Task`](https://theseus-os.github.io/Theseus/doc/task/struct.Task.html) 结构体在大小和职责范围上都相当精简，
因为我们的状态管理哲学力求让每个子系统只保存与该子系统相关的状态。
例如，与调度器相关的状态并不存在于 Theseus 的任务结构体中，而是位于实际使用它们的相应调度器 crate 中。
换句话说，Theseus 的任务结构体并不是一个大而全的整体。

Theseus 的任务结构体包含以下几个关键条目：

- 该任务在 CPU 上执行时真正的 [`Context`](https://theseus-os.github.io/Theseus/doc/context_switch/struct.Context.html)。
    - 其中保存着 CPU 寄存器的值（例如栈指针和其他寄存器），在该任务与其他任务之间进行上下文切换时会被保存和恢复。
- 该任务的名称和唯一 ID。
    - 它们主要用于便于人类阅读和调试。
- 该任务的可运行性（[`RunState`](https://theseus-os.github.io/Theseus/doc/task/enum.RunState.html)），即它是否可以被调度执行，以及它当前的运行状态。
    - 其中包括该任务的[退出值](https://theseus-os.github.io/Theseus/doc/task/enum.ExitValue.html)（如果它已经退出）。
- 该任务所运行于其中的命名空间；参见 [`CrateNamespace`](https://theseus-os.github.io/Theseus/doc/mod_mgmt/struct.CrateNamespace.html)。
    - 让任务运行在不同的 CrateNamespace 中是部分模拟标准进程抽象所提供的隔离性的一种方式；更多信息参见[此处](https://www.theseus-os.com/Theseus/book/design/design.html#cell--crate)。
- 该任务的[栈](https://theseus-os.github.io/Theseus/doc/stack/struct.Stack.html)。
- 该任务的[环境](https://theseus-os.github.io/Theseus/doc/environment/struct.Environment.html)，例如它当前的工作目录。
- 各种与处理执行失败以及清理失败任务相关的状态。
    - 它们用于实现容错，例如栈展开、任务清理，以及在故障发生时自动重启关键任务。

> 注意：[`Task`](https://theseus-os.github.io/Theseus/doc/task/struct.Task.html) 结构体的源码级文档对 Task 结构体的每个成员字段都有详细得多的描述。

Task 结构体本身被拆分为两个主要部分：

1. 不可变状态：在 Task 初次创建之后就不会再改变的内容。
2. 可变状态：在 Task 的生命周期内可以改变的内容。

不可变状态包含在 [`Task`](https://theseus-os.github.io/Theseus/doc/task/struct.Task.html) 结构体本身中，而可变状态则包含在 [`TaskInner`](https://github.com/theseus-os/Theseus/blob/d6b86b6c46004513735079bed47ae21fc5d4b29d/kernel/task/src/lib.rs#L237) 结构体中。
每个 Task 结构体都包含一个由锁保护的 `TaskInner` 实例。
这一设计旨在显著降低以只读方式访问 Task 状态时的加锁开销与竞争。
注意，某些可变状态（主要是运行状态信息）已被移入 `Task` 本身，因为它们可以被安全地原子修改；但总体而言，所有其他可变状态都放在 `TaskInner` 中。
我们还谨慎地正确指定了 `Task` 和 `TaskInner` 结构体中各状态项的公开可见性，以确保它们不会被其他 crate 恶意或意外地修改。

### `TaskRef` 类型

任务经常需要在 Theseus 的众多实体和子系统之间共享。
为此，Theseus 提供了 [`TaskRef`](https://theseus-os.github.io/Theseus/doc/task/struct.TaskRef.html) 类型，它实际上是指向某个 `Task` 的共享引用，即一个 `Arc<Task>`。
我们引入一个专门的 [`newtype`](https://doc.rust-lang.org/book/ch19-04-advanced-types.html#using-the-newtype-pattern-for-type-safety-and-abstraction) 而不是直接使用 `Arc<Task>`，有以下几个原因：

- 使所有与任务管理相关的代码更加清晰。
- 控制 Task 结构体中各条目的可见性（公开或私有）。
- 保证在创建新 Task 时，任务本地数据区（即每个任务各自的数据）被正确地建立起来。
    - 必须存在从 Task 指向其外层 TaskRef 的循环引用，才能实现任务本地数据；更多细节参见 [`TaskLocalData`](https://github.com/theseus-os/Theseus/blob/d6b86b6c46004513735079bed47ae21fc5d4b29d/kernel/task/src/lib.rs#L1085) 类型。
- 只暴露一组有限的函数，让外部 crate 只能修改或查询特定的任务状态，例如 join 一个任务。
- 极大优化两个 Task 之间的比较与相等性测试。
    - 如果两个 TaskRef 指向同一个底层 Task 结构体，就认为它们相等。
    - 这避免了必须对 Task 结构体中的所有字段进行比较测试——那是非常昂贵的操作。
- 防止其他实体直接访问某个 Task 结构体，或用非 Arc 的共享指针类型包裹某个 Task。

> 注意：虽然 `TaskLocalData` 提供了一种非常基础的任务级数据形式（通常称为线程本地存储，TLS），但在生成的目标代码中对编译器可知的标准 TLS 区域提供完整支持仍在开发之中。

### 全局任务列表

与所有其他操作系统一样，Theseus 维护着一份系统中所有任务的全局列表。
目前，这个任务列表被保存为一个从数字任务 ID 到 `TaskRef` 的映射。

任务在最初被派生时加入任务列表，并在其整个生命周期内一直保留在列表中。
需要注意的是，某个任务存在于任务列表中并不代表该任务是可运行的或正在执行。
只有当一个任务已被*收割*（reaped，即它已完全退出，且其退出值已被另一个任务"取走"）之后，才会从任务列表中移除；例如，一个"父"任务可能会收割它派生出的"子"任务。

## 上下文切换

在操作系统术语中，"上下文切换"一词经常被错误地一词多用（overload），被随意用来指代许多相关话题：

1. 在同一地址空间内从一个线程切换到另一个线程。
2. 从一个地址空间中的线程切换到另一个地址空间中的线程。
3. 在系统调用期间从用户态切换到内核态（例如从 Ring 3 切换到 Ring 0）。
4. 在中断被触发时从用户线程切换到内核线程。

只有上面的第 1 种才是我们所认为的真正的上下文切换，也是我们在这里说"上下文切换"时所指的含义。
上面的第 2 种是*地址空间切换*（address space switch），例如切换页表，这是另一种动作，只有在切换到与当前任务处于不同进程/地址空间中的任务时才可能发生。
上面的第 3 种是*模式切换*（mode switch），通常不会导致完整的执行上下文被保存或恢复；只有部分寄存器可能被压入栈或从栈中弹出，具体取决于给定平台的系统调用所采用的调用约定。
上面的第 4 种与第 3 种类似，但它是由硬件而非用户态软件触发的，因此可能需要保存/恢复更多的执行上下文状态。

上下文切换的一个关键特性是：它对当前正在执行的代码是透明的，因为操作系统内核的底层会在恢复执行之前按需保存和恢复执行上下文。
因此，上下文切换（配合抢占）使得多个彼此不信任、互不配合的任务能够透明地共享 CPU，同时维持这样一种理想化模型：每个任务都以为自己是整个系统中唯一在执行的任务，并且独占地使用 CPU。

### 实现上下文切换

Theseus 中上下文切换的实现分散在若干个 crate 中，每个 crate 对应启用的某一特定 SIMD 指令子集。
顶层的 [`context_switch`](https://theseus-os.github.io/Theseus/doc/context_switch/index.html) crate 会根据目标硬件平台规范所选择的 SIMD 功能子集，自动选择正确的版本。
例如，如果启用了 SSE2，那么 `#[cfg(target_feature = "sse2")]` 就会为真，从而使用 `context_switch_sse2` crate 作为上下文切换的实现。
目前，在构建 Theseus 时可以使用 `x86_64-unknown-theseus-sse` 目标来选择这一配置：

```sh
make run TARGET=x86_64-unknown-theseus-sse
```

Theseus 同时支持 SSE2 和 AVX，但其默认目标 `x86_64-unknown-theseus` 将二者都禁用了。
这会让编译器生成软浮点指令而不是 SIMD 指令，也就是说完全不会使用 SIMD 寄存器组。
因此，禁用 SIMD 会得到最简单、最快速的上下文切换版本，因为只需要保存和恢复基本的通用 CPU 寄存器组；所有 SIMD 寄存器都可以忽略。

上下文切换本质上是一个 unsafe 操作，这也是标准 [`context_switch()`](https://theseus-os.github.io/Theseus/doc/context_switch_regular/fn.context_switch_regular.html) 函数被标记为 unsafe 的原因。
它必须用汇编实现，以确保编译器不会在我们保存/恢复寄存器的指令之间插入任何会修改寄存器值的指令。
它只会被 [`task_switch()`](https://theseus-os.github.io/Theseus/doc/task/fn.task_switch.html) 函数调用，因为只有该函数拥有正确的信息——已保存的寄存器值以及恢复出的寄存器值的目标位置——才能正确地调用它。

## 抢占式多任务与协作式多任务

Theseus 完整实现了抢占式多任务（preemptive multitasking）支持：在固定的周期性时间间隔上打断某个任务，以便让其他任务接管执行。
这可以防止某个贪婪的任务霸占所有系统资源，和/或让其他任务一直得不到执行时间。
与大多数其他系统一样，我们在 Theseus 中使用一个定时器中断来实现这一点，它在每个 CPU 核心上每隔几毫秒触发一次。
这个时间段的长度被称为*时间片*（timeslice），它是一个可配置的设置项。
目前，这个定时器中断是在 [`LocalApic`](https://theseus-os.github.io/Theseus/doc/apic/struct.LocalApic.html) 初始化例程中设置的，该例程在每个 CPU 核心被发现并初始化时运行。
中断处理函数本身非常简单，目前位于 `kernel/interrupts/src/lib.rs` 中名为 [`lapic_timer_handler()`](https://github.com/theseus-os/Theseus/blob/d6b86b6c46004513735079bed47ae21fc5d4b29d/kernel/interrupts/src/lib.rs#L380) 的函数里。

协作式多任务（cooperative multitasking）也是可行的，但目前 Theseus 尚未提供一种简便的方法来禁用抢占、从而*只*使用协作式多任务；不过要加上这一点并不困难。
目前，任务可以通过调用 [`schedule()`](https://theseus-os.github.io/Theseus/doc/scheduler/fn.schedule.html) 来主动把处理器让给其他任务，该函数会选择下一个要运行的任务并切换过去。
这个调度函数与前面提到的定时器中断处理函数所调用的函数是同一个，后者每隔几毫秒抢占一次当前任务。

## 任务的生命周期

Theseus 的任务遵循一个典型的任务生命周期，[`RunState`](https://theseus-os.github.io/Theseus/doc/task/enum.RunState.html) 枚举的可能取值部分地展示了这一生命周期。

- Initializing（初始化中）：任务正在被创建。
    - 当任务创建完毕、完全派生之后，其运行状态会被设置为 Runnable。
- Runnable（可运行）：任务可以被调度执行（但当前不一定正在执行）。
    - 一个可运行的任务可能被阻塞，从而在随后被解除阻塞之前不会被调度执行。

注意："running（正在运行）"和"runnable（可运行）"不是一回事。

一个任务从被派生之后到退出之前的这段时间内都被认为是可运行的，只要它没有被阻塞。
只有当一个任务当前正在某个 CPU 核心上执行时，才称它是*正在运行*的；而当它在等待被调度执行、同时其他任务正在运行时，它只是被认为是可运行的。
- Blocked（被阻塞）：任务正阻塞在某个其他条件上，无法被调度执行。
    - 被阻塞的任务可以被解除阻塞，重新标记为可运行。
- Exited（已退出）：任务不再执行，也永远不会再执行。
    - 已退出的任务拥有一个 [`ExitValue`](https://theseus-os.github.io/Theseus/doc/task/enum.ExitValue.html)，它可能是以下之一：
        - Completed（已完成）——任务正常运行至结束，并按预期完成。
        - Killed（被杀死）——任务因崩溃（语言层面的 panic 或机器层面的异常）或收到杀死请求而提前停止执行。
    - 已退出的任务在它被"收割"（reaped，见下文）之前不得被清理。
- Reaped（已收割）：任务已退出，且其 [`ExitValue`](https://theseus-os.github.io/Theseus/doc/task/enum.ExitValue.html) 已被另一个 Task 取走。
    - 任务一旦被收割，就会被清理并从系统中移除。
    - 如果没有其他任务在等待某个已退出的任务退出，系统会自动收割它。
关于其工作原理的更多信息，参见 [`JoinableTaskRef`](https://www.theseus-os.com/Theseus/doc/task/struct.JoinableTaskRef.html)。

### 派生新任务

派生（创建）新任务的功能实现在一个单独的 [`spawn`](https://theseus-os.github.io/Theseus/doc/spawn/index.html) crate 中。
Theseus 提供了 `TaskBuilder` 接口，允许使用者自定义新任务的创建，它以调用 [`new_task_builder()`](https://theseus-os.github.io/Theseus/doc/spawn/fn.new_task_builder.html) 作为起点。
在派生任务时，调用者必须传入一个函数和一个参数：该函数是任务的入口点，而该参数会被传给这个入口点函数。
一旦任务构建器已被用来对新任务完成适当的自定义，就必须在 `TaskBuilder` 对象上调用 `spawn()` 方法，才能真正创建新的 `Task` 实例并将其加入一个或多个运行队列。
这并不会立即执行该任务，而只是使它有资格在下一次任务切换时被调度执行。

传入派生例程的那个函数，实际上并不是任务第一次被切换到时最先运行的函数。
所有新任务都拥有相同的入口点，即 [`task_wrapper()`](https://github.com/theseus-os/Theseus/blob/d6b86b6c46004513735079bed47ae21fc5d4b29d/kernel/spawn/src/lib.rs#L500) 函数，它简化了跳入一个新任务的流程：

1. 设置正确的栈内容
2. 以正确的参数调用任务的入口函数
3. 捕获展开过程中的 panic 与异常
4. 在任务退出后处理其状态，无论它是成功完成还是失败。

### 清理任务

`Task` 结构体实现了 Rust 的 `Drop` trait，这意味着一旦指向某个 Task 的所有引用都消失了，该 Task 对象本身就可以被 drop 并清理掉。
由于 Task 比大多数结构体都要复杂，仅靠 drop 处理函数并不足以彻底清理并移除该任务的所有痕迹，以及它对系统产生的影响。

清理流程会在任务退出之后开始，任务退出可能是运行至结束，也可能是因收到请求而被杀死，或是在遇到 panic 或异常之后退出。

- 如果任务运行至结束，[`task_wrapper()`](https://github.com/theseus-os/Theseus/blob/d6b86b6c46004513735079bed47ae21fc5d4b29d/kernel/spawn/src/lib.rs#L500) 会调用 [`task_cleanup_success()`](https://github.com/theseus-os/Theseus/blob/d6b86b6c46004513735079bed47ae21fc5d4b29d/kernel/spawn/src/lib.rs#L547)，该函数将任务标记为已成功退出，并把返回的 [`ExitValue`](https://theseus-os.github.io/Theseus/doc/task/enum.ExitValue.html) 存入它的 Task 结构体。
- 如果任务没有运行结束，[`task_wrapper()`](https://github.com/theseus-os/Theseus/blob/d6b86b6c46004513735079bed47ae21fc5d4b29d/kernel/spawn/src/lib.rs#L500) 会调用 [`task_cleanup_failure()`](https://github.com/theseus-os/Theseus/blob/d6b86b6c46004513735079bed47ae21fc5d4b29d/kernel/spawn/src/lib.rs#L587)，该函数将任务标记为遭遇了失败，并把导致它被提前杀死的[原因](https://theseus-os.github.io/Theseus/doc/task/enum.KillReason.html)存入它的 Task 结构体。

在处理完成功或失败的退出情形之后，任务生命周期的最后一环是 [`task_cleanup_final()`](https://github.com/theseus-os/Theseus/blob/d6b86b6c46004513735079bed47ae21fc5d4b29d/kernel/spawn/src/lib.rs#L631) 函数，它会把该任务从其所在的任何运行队列中移除，丢弃指向该任务的最后一个引用，然后重新启用中断并让出处理器。
那个最后的任务引用在被 drop 时，会触发前文提到的 Task 结构体的 drop 处理函数，它会自动释放该任务所获取的所有状态和已分配的资源。
注意，栈展开的过程已经完成了大部分资源和分配的释放，因为它们都是由位于程序栈上的所有权值来表示的。

> 注意：对于以*可重启*（restartable）方式派生的关键系统任务，还有另一组与之类似的任务生命周期函数。它们的主要区别在于：清理动作完成之后，会以与失败任务相同的入口点和初始参数派生出一个新任务。
---

> **译注（原书脚注）**：在单处理器（只有一个 CPU 核心）机器上，多任务并非真正的并发，只是因为多个任务的执行在给定时间间隔内被快速交错，看起来像是并发。真正的并发只能在多处理器机器上实现：不同的任务在不同的核心上同时执行。
