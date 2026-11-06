# Rust 学习大纲 · 以撮合引擎为教材

> **教材**：`matching-engine/`（src+tests+benches 共 6479 行，edition 2021，MSRV 1.75）
> **学员背景**：Python Web 为主，已学 PyTorch，有 Go 并发基础
> **开始日期**：2026-11-03　**最近更新**：2026-11-05（第 5 课验收通过）

---

## 一、目标与判断标准

不是"把 Rust 书看完"，而是**能独立读懂并安全改动这 6400 行**。三个可验证的终点：

1. 打开 `engine.rs` 的 `place()`，能逐行说出每个 `&mut` 在借什么、什么时候归还。
2. 给项目加一个功能（新拒单原因、新订单类型），不需要问人"该改哪几处"。
3. 对自己写的代码能解释"这里为什么不能写得更简单"——而不是靠 `clone` 绕过去。

---

## 二、教学方式（固定不变）

| 环节 | 做法 |
|---|---|
| 节奏 | **一课一屏**：一条消息只讲一个概念 + 一个练习，不预告下一课 |
| 顺序 | 作业不交付，不进下一课 |
| 分工 | 练习骨架我写（`examples/lessonNN_*.rs` 里的 `todo!()`），实现你写 |
| 门禁 | 每课必过 `cargo test` + `cargo clippy -- -D warnings` |
| 报错 | 卡住先贴完整报错（含 `E0xxx` 错误码），我只给方向不给答案 |
| 教材 | 只读主干四个文件；`liquidation`/`adl`/`funding` 等业务外围先跳过 |

---

## 三、路线

```
S1 语言内核（第 1–6 课）   ──▶ S2 工程化（第 7–10 课） ──▶ S3 领域实战（第 11+ 课，选 1 个方向）
所有权 · 类型 · 错误处理       泛型 · 迭代器 · 模块 · 测试      崩溃恢复 / 性能
```

---

## 四、课程表

### S1 · 语言内核

| # | 主题 | 主要源文件 | Rust 知识点 | 练习文件 | 状态 |
|---|---|---|---|---|---|
| 1 | enum 是"带数据的标签" | `src/types.rs` | enum 携带不同载荷、穷尽 `match`、or-pattern、`Vec` 间接层解决递归 | `lesson01_enum.rs` | ✅ 已验收 |
| 2 | 顺序由 `Ord` 决定 | `src/book.rs` | newtype、`Ord`/`PartialOrd` 契约、`BTreeMap` 有序性、类型隔离 | `lesson02_ord.rs` | ✅ 已验收 |
| 3 | 借用与 NLL | `src/engine.rs` `place()` | `&mut self`、`Option`、`let-else`、非词法生命周期、为什么"先抄出队首字段" | `lesson03_borrow.rs` | ✅ 已验收 |
| 4 | 写日志时谁拥有命令（clone 还是借用） | `src/runner.rs` + `src/wal.rs` | 泛型记录 `Rec<T>`（`Rec<&Cmd>` 写 / `Rec<Cmd>` 读）、E0505（借了不能移走）、bincode 按位置编码的静默错位 | `lesson04_own.rs` | ✅ 已验收 |
| 5 | `Option` / `Result` / `panic` 的边界 | `engine.rs` 的 `validate` / `cancel` | `Option` vs `Result`、`?`、什么时候该 panic（不变量破坏） | `lesson05_err.rs` | ✅ 已验收 |
| 6 | 状态怎么变成字节 | `types.rs` + `snapshot.rs` | `derive(Serialize/Deserialize)`、bincode、为什么状态类型必须可序列化 | `lesson06_serde.rs` | 计划 |

### S2 · 工程化

| # | 主题 | 主要源文件 | Rust 知识点 | 状态 |
|---|---|---|---|---|
| 7 | 泛型与 trait | `wal.rs`（`read_all::<T>`） | 泛型函数、trait bound、单态化 | 计划 |
| 8 | 迭代器与闭包 | `book.rs` `depth()`、`engine.rs` `available_liquidity` | `range`/`map`/`sum`、惰性求值、闭包捕获 | 计划 |
| 9 | 模块、可见性与 feature | `lib.rs` + `Cargo.toml` | `pub(crate)`、模块分层、`#[cfg(feature)]` | 计划 |
| 10 | 测试与不变量 | `tests/replay.rs` | `#[test]`、断言设计、用测试锁住"重放一致" | 计划 |

### S3 · 领域实战（学完 S1 再选一个做到底）

| # | 方向 | 源文件 | 交付物 |
|---|---|---|---|
| 11 | 崩溃恢复：WAL + 快照 | `runner.rs` / `wal.rs` / `snapshot.rs` | 能解释"先落盘后执行"为什么能保证不丢单，并做一次人为崩溃实验 |
| 12 | 性能与内存 | `benches/` / `src/bin/mem_probe.rs` | 给出改前改后的吞吐/内存数据，说清热点在哪 |

---

## 五、当前进度

### 第 1 课 · enum 是"带数据的标签" ✅ 2026-11-03 验收通过

- **交付**：`examples/lesson01_enum.rs`，2 个测试全绿，clippy 干净
- **掌握**：enum 三种载荷形状（元组变体/结构体变体）、穷尽 `match` 由编译器强制、or-pattern 合并空分支
- **关键区分**：`E0599`（名字不存在，定义被删）vs `E0004`（定义在，`match` 没覆盖）
- **踩坑记录**：
  - 把 `types.rs` 的 `Rejected` **变体定义**注释掉，导致全 crate 23 处引用崩 → 本意应是注释 `match` 分支
  - rust-analyzer 自动插入 `use std::f32::consts::E`，被 `-D warnings` 拦下 → 门禁的价值

### 第 2 课 · 顺序由 `Ord` 决定 ✅ 2026-11-05 验收通过

- **交付**：`examples/lesson02_ord.rs`，3 个测试全绿，clippy 干净
- **掌握**：`BTreeMap` 的有序性来自 key 的 `Ord`；newtype + 手写 `Ord` 实现反转排序；`first_key_value()`（1.66+）比 `keys().next()` 更直接
- **关键区分**：类型系统只校验「结构」（有没有实现 `Ord`），不校验「语义」（哪个方向才是业务要的顺序）。`derive(Ord)` 生成的是字段升序，编译完全通过，但把「最优买价」变成了「最低买价」——只有测试能抓
- **踩坑记录**：
  - 删掉两个手写 impl、只给 derive 加 `Ord` → `E0277: can't compare RevPrice with RevPrice`，`required by a bound in Ord`。现场演示了 `trait Ord: Eq + PartialOrd<Self>` 这条依赖链
  - 补上 `PartialOrd` 后编译通过，但 3 个测试全挂：`best()` 返回 `Some(9900)` 而非 `Some(10100)`

### 第 3 课 · 借用与 NLL ✅ 2026-11-05 验收通过

- **交付**：`examples/lesson03_borrow.rs`，`fill()` 由用户独立实现，2 个测试全绿，clippy 干净（参考实现保留为 `fill2` 供对照）
- **掌握**：借用区间 = [借用产生，最后一次使用]；`front()` / `front_mut()` / `pop_front()` 三件套的读/改/拿走分工；`entry().or_default()`（无则建）vs `get_mut()`（无则退）的语义选择；`break`/循环终止性不属于编译器管
- **建立的心智模型**：引用绑定的是**地址**不是值；值内联存在容器里，move = 字节搬家，地址不跟值走；借用检查管的是"地址在有效期内不许换房客"
- **踩坑记录**：
  - E0502：`front()` 后在 `pop_front()` 之后还用 `f`（第三课 B 版本）
  - `let mut f = front()` 以为 mut 能改字段 → `E0594: cannot assign behind a &`
  - `for lv in level` 想遍历判断：撮合循环不是遍历（逗留/摘除/早停），且迭代器全程占用 `&mut` → E0499
  - `f.visible -= remaining` 忘了取 min → 数量守恒破坏；两分支写法漏相等边界 → 僵尸单（visible=0 出不了队，prune 失效）
  - **死循环**：`>=` 分支没配 else，队首不够吃时状态不变无限重跑——编译器/clippy/借用检查都不管终止性
  - NLL 按路径计算：`continue` 路径上 `f` 死于 `format!` 行，pop 合法；同代码换个路径可能变红

### 第 4 课 · 写日志时谁拥有命令 ✅ 2026-11-05 验收通过

- **交付**：`examples/lesson04_own.rs`，`apply_borrow` 由用户实现并合并为泛型单形状，测试绿、clippy 干净、`rustfmt` 零 diff
- **掌握**：`Rec<T>` 一份字段列表同时服务写端（`Rec<&Cmd>`，只 `Serialize`）和读端（`Rec<Cmd>`）；借用 → 序列化 → move 的顺序不是风格，是所有权逼出的唯一解
- **关键区分**：**序列化契约**（字节能不能被正确解释）与**崩溃一致性**（write-ahead 顺序）是两个正交维度。前者靠"形状只有一份"，后者靠"先落盘后执行"
- **实验数据**（bincode 1.x，fixint，28 字节记录）：

  | 读端结构改动 | 结果 |
  |---|---|
  | `command` 提到 `seq` 前面 | **静默成功**：`Place { id: 7, qty: 5 }` 读成 `Cancel { id: 0 }` |
  | `seq: u64` 改成 `u32` | **静默成功**：`id = 30064771072`（垃圾值） |
  | 读端多一个字段 | 报错 `unexpected end of file`（唯一会报错的一种） |
  | `Rec<T>` 单形状 | 写端读端字节逐字节相等 |

- **踩坑记录**：
  - 把"两个结构体的字段对齐"理解成"先写日志后读日志的执行顺序"，答错了第 3 题
  - 以为"函数返回 `String` 就不能把 `process(cmd)` 挪到中间"——不知道 `let out = ...; out` 是合法的尾表达式
  - E0505 的 note 直接建议 `.clone()`，正是本课要否掉的方案：编译器只管安全，不管代价

### 第 5 课 · 三种失败，三种表达 ✅ 2026-11-05 验收通过

- **交付**：`examples/lesson05_err.rs`，`validate` / `place` / `cancel` 由用户实现，3 测试全绿、clippy 零告警、`rustfmt` 零 diff
- **掌握**：`Option<RejectReason>` 表达"业务拒绝"（`None` = 没有理由拒绝你）；`Result` + `?` 留给 IO；`panic!` 留给不变量破坏。判据一句话：**这个失败是谁的错**
- **同一函数两种处理**（`engine.rs:453`）：`index` 里没有 → 用户撤了个不存在/已完结的单 → 发 `Event::Rejected`；`index` 有、`book` 没有 → 两容器不同步 → `panic!`
- **为什么 `validate` 返回 `Option` 而不是 `Result`**：`Result` 会诱导 `validate(&req)?`，但 `place` 返回 `Vec<Event>` 不是 `Result`，`?` 用不了；用 `Option` 等于在类型层面声明"这个失败不该上抛，必须就地变成事件"
- **`next_id` 三条铁律**：唯一、确定性（重放必须分配同样的号）、必须进快照（漏了就恢复后重号 → 撤错别人的单）
- **`if let` 的语义**：匹配不上就跳过整块，编译器替你补 `_ => {}`；所以 `None` 分支不需要写，也不报 E0004。要处理 `None` 才用 `match` 或 `else`
- **踩坑记录**：
  - `self.index.insert(seq, price).expect("msg")` → 新插入必然返回 `None`，`expect` 直接 panic，3 个测试全挂
  - `self.book.insert(-1, (seq, price))` → `Vec::insert` 第一个参数是下标（`usize`，无负号），报 E0600；`usize::MAX` 那条 help 不要照做
  - `invariant_break_panics` 曾"假绿"：断言只有 `is_err()`，`todo!()` 也是 panic，照样过 —— **弱断言没有判别力**
  - 漏写 `self.book.push(...)`，两容器从第一笔起就不同步；`return Event::Accepted(seq)` 被 clippy `needless_return` 拦下（`if/else` 整体就是尾表达式）

---

## 六、学习档案

| 项目 | 内容 |
|---|---|
| 原语言背景 | Python（Web）、Go（并发）、PyTorch、Java、Ruby |
| 当前阶梯 | S1 语言内核 |
| 已掌握 | enum 代数数据类型、穷尽 match、newtype + 手写 `Ord`、`-D warnings` 门禁流程、会查 `cargo doc` 找更贴切的 API、借用区间（活到最后一次使用）、`front`/`front_mut`/`pop_front` 分工、`entry` vs `get` 语义、E0502/E0594/E0499/E0505 的读法、泛型结构体单一形状（`Rec<T>`）、`Option`/`Result`/`panic` 三者的适用边界、`if let` 只关心一种情况时的隐式 `_ => {}` |
| 反复踩坑 | 分不清"改定义"和"改使用点"；IDE 自动导入引入噪音；对 trait 依赖链（`Ord: Eq + PartialOrd`）没形成肌肉记忆；容易把"结构对齐"和"执行顺序"两类问题混为一谈；习惯性给不会失败的操作加 `expect` |
| 待观察 | 循环终止性（第 3 课死循环一次）；分支重复导致的边界缝隙（僵尸单）；对"编译器建议 ≠ 最佳方案"的敏感度（第 4 课 clone 提示）；写测试时断言强度（第 5 课假绿） |

---

## 七、环境备忘

- 工具链：`cargo 1.99.1` / `rustc 1.99.1`，edition 2021，MSRV 1.75
- 练习统一放 `matching-engine/examples/`，用 `cargo test --example <名字>` 跑，不污染 `src/`
- 若遇到 `error deleting lock file ... 拒绝访问`：另一个 cargo 进程（或 rust-analyzer）正占用 `target/`，等它结束再跑

---

## 八、维护约定

- 每课验收后更新「课程表」状态与「当前进度」两节
- 新踩的坑追加到对应课次的「踩坑记录」，不覆盖旧内容
- 课程表顺序可调整，但已验收的课不回退
