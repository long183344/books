# 01 · C# 委托（Delegate）与 `public static Action` 详解

> 数据基准：C# 12 / .NET 8。本文从"委托到底是什么"讲起，重点拆解 `public static Action` 的语义与用法，
> 覆盖基础声明、调用、内置委托家族、`MulticastDelegate` 多播、协变逆变、闭包、事件、异步、实战场景与十大坑。
> 通读后你能回答：委托和函数指针有何不同？`Action` 与 `delegate` 何时该用哪个？`public static Action` 适合做什么？

---

## 一句话结论

> **委托是"类型安全的函数引用"——把方法当成数据来传递、存储、组合。** `Action` 是 .NET 内置的一类"无返回值"委托的快捷定义；`public static Action` 表示"一个全局可见、无需实例化对象即可调用的无参（或带参）回调钩子"，常用于全局事件总线、日志钩子、插件回调等跨模块解耦场景。能用 `Action`/`Func` 就别自己 `delegate`，能用局部/实例委托就别滥用 `static` 全局委托。

---

## 1. 委托是什么：先把本质讲清楚

很多教材一句话带过"委托是类型安全的函数指针"，但这句话有三个关键词需要拆开：

| 关键词 | 含义 | 对比 C/C++ 函数指针 |
| --- | --- | --- |
| **类型安全** | 委托不仅约束"是不是函数"，还约束**签名**（返回值 + 参数类型/个数/顺序） | C 函数指针只约束返回和参数类型，但极易写错、无编译期保护 |
| **函数引用** | 委托变量里装的是"方法"，不是值；调用委托 = 间接调用方法 | 同函数指针，但 .NET 帮你管了对象引用与生命周期 |
| **引用类型** | 委托本身是 `System.MulticastDelegate` 的子类（继承自 `Delegate`），是堆对象 | 函数指针是裸地址 |

### 1.1 委托的内部继承链

```
System.Object
  └─ System.Delegate            // 单个方法引用（抽象基类，不可直接实例化）
       └─ System.MulticastDelegate  // 可持有"方法调用列表"（多播）
            └─ 你声明的每一个 delegate 类型（编译器自动生成）
```

关键点：**所有 `delegate` 声明和所有 `Action`/`Func` 内置委托，最终都是 `MulticastDelegate` 的子类**。这意味着它们天生支持"多播"——一个委托变量可以挂多个方法，调用时依次执行。

### 1.2 为什么需要委托

没有委托，想"把一段逻辑交给别人在合适时机调用"，只能：
- 写死调用（无法扩展）—— 违反开闭原则；
- 传一个接口（重量级，只为传一个方法）—— 过度设计；
- 反射调方法（慢、字符串脆弱）—— 不可取。

委托让"方法"成为一等公民（first-class value），直接当参数、返回值、字段、属性传递。这是**回调、事件、LINQ、策略模式**的底层基石。

---

## 2. 委托基础：声明、绑定、调用

### 2.1 自定义 delegate（最原始形态）

```csharp
// 1) 声明一个委托类型：签名 = 两个 int 入参，返回 int
public delegate int Calculate(int a, int b);

class Program
{
    static int Add(int a, int b) => a + b;
    static int Mul(int a, int b) => a * b;

    static void Main()
    {
        // 2) 实例化（把方法"绑"到委托变量）—— 叫绑定 / 绑定目标
        Calculate op = Add;          // 写法一：直接赋值方法组（method group），编译器自动 new
        op = new Calculate(Mul);     // 写法二：显式 new（等价）

        // 3) 调用委托，像调用普通方法一样
        int r1 = op(3, 4);           // => 12（此时指向 Mul）
        op = Add;
        int r2 = op(3, 4);           // => 7

        Console.WriteLine($"{r1}, {r2}");
    }
}
```

要点：
- `Calculate op = Add;` 不是"调用 Add"，而是"把 Add 的引用赋给 op"，这是**方法组转换**（C# 2.0+ 支持）。
- 委托的签名必须与目标方法**完全匹配**（参数类型、个数、返回类型、ref/out 修饰符都要一致），否则编译报错——这就是"类型安全"。

### 2.2 三种给委托"装方法"的方式

```csharp
Calculate d;
d = Add;                       // ① 方法组（推荐，最干净）
d = delegate(int a, int b) { return a + b; };   // ② 匿名方法（C# 2.0，已过时写法）
d = (a, b) => a + b;           // ③ Lambda 表达式（现代 C# 首选）
```

现代代码里几乎一律用 **③ Lambda**，② 基本只在维护老代码时见到。

---

## 3. 内置委托家族：Action / Func / Predicate

每次都自己写 `delegate` 太啰嗦。.NET 在 `System` 命名空间里预定义了通用委托，**90% 场景直接用它们，不要自建 delegate**。

| 内置委托 | 签名特征 | 用途 |
| --- | --- | --- |
| `Action` | 无参、无返回值 `void Invoke()` | 回调、钩子、事件处理 |
| `Action<T1..T16>` | 1~16 个入参、`void` | 同上，带参数 |
| `Func<T1..T16,TResult>` | 1~16 入参 + 最后一个是**返回值** | 有计算/转换逻辑（map、选择器） |
| `Predicate<T>` | `bool Invoke(T)` | 条件判断（如 `List.Find` 的匹配器） |

> 注：`Predicate<T>` 本质是 `Func<T, bool>` 的历史别名，LINQ 时代更推荐直接用 `Func<T,bool>`。

### 3.1 Action 到底是什么

```csharp
// 框架里的真实定义（简化）：
public delegate void Action();             // 无参
public delegate void Action<in T>(T obj);  // 一个泛型入参
public delegate void Action<in T1, in T2>(T1 arg1, T2 arg2); // 两个入参
// ... 一直到 Action<T1..T16>
```

`Action` = **"返回 void 的委托"**。它**不能返回数据**，只负责"做一件事"。需要返回值就用 `Func`。

```csharp
Action greet = () => Console.WriteLine("Hello");
Action<string> greetTo = name => Console.WriteLine($"Hello, {name}");
Action<int, int> printSum = (a, b) => Console.WriteLine(a + b);

greet();            // Hello
greetTo("World");   // Hello, World
printSum(3, 4);     // 7
```

### 3.2 `public static Action` 逐项拆解

用户特别问到 `public static Action`，把它拆成三段理解：

| 修饰符 | 作用 | 对委托的含义 |
| --- | --- | --- |
| `public` | 访问级别：任何程序集都能访问 | 这个回调钩子对外暴露，跨模块可订阅/赋值 |
| `static` | 不依赖实例：属于**类型本身**而非对象 | 全局唯一，无需 `new` 某个类就能读写它；整个进程/AppDomain 共享同一份 |
| `Action` | 委托类型：无返回值的方法引用 | 挂上去的方法"只做事、不返回" |

```csharp
// 一个典型的 public static Action：全局日志钩子
public class Logger
{
    // 任何代码都能给它挂一个处理方法；无需实例化 Logger
    public static Action<string> OnLog;

    public static void Write(string msg)
    {
        // 安全调用：null 时不崩
        OnLog?.Invoke($"[{DateTime.Now:HH:mm:ss}] {msg}");
    }
}

// 在程序启动处"订阅"一次，全程序生效
Logger.OnLog = s => File.AppendAllText("app.log", s + Environment.NewLine);
Logger.Write("服务启动");   // => 写入 app.log
```

`public static Action` 的语义就是：**"进程内一个全局的、无返回值的回调入口"**。谁都能赋值、谁都能 `+=` 追加、谁都能 `Invoke` 触发。

### 3.3 Action 与 delegate 的选择

| 场景 | 用哪个 |
| --- | --- |
| 临时回调、LINQ、事件处理、策略参数 | `Action` / `Func`（内置，省代码） |
| 需要独特名字提升可读性、或需 `ref`/`out` 参数 | 自定义 `delegate`（内置委托不支持 `ref`/`out`） |
| 想限制调用方只能 `+=`/`-=` 不能整体替换 | 用 `event`（见第 6 节） |

---

## 4. 高级用法

### 4.1 多播委托（MulticastDelegate）

一个委托变量可以挂**多个方法**，调用时按顺序执行——这是 `MulticastDelegate` 的核心能力。

```csharp
Action log = () => Console.WriteLine("① 写文件");
log += () => Console.WriteLine("② 发网络");
log += () => Console.WriteLine("③ 刷界面");

log();  // 依次输出 ① ② ③
```

底层机制：
- `+=` 实际是 `Delegate.Combine(left, right)`，返回一个**新委托**，其调用列表包含两者。
- `GetInvocationList()` 可拿到列表里**每一个**单独委托，用于逐个调用（见 4.2 异常处理）。

```csharp
// 拆开调用列表，单独处理每个方法
foreach (Action a in log.GetInvocationList())
{
    a();   // 可以包 try/catch，某个失败不影响其它
}
```

**返回值在多播下只保留最后一个**：若委托有返回值（如 `Func<int>`），多播调用后只拿到最后挂上的那个方法的返回值，前面的都被丢弃——这是常见隐蔽 bug，需要逐个调用才能拿到全部。

### 4.2 多播中的异常：一个抛，后面全停

```csharp
Action d = () => Console.WriteLine("A");
d += () => throw new Exception("B 炸了");
d += () => Console.WriteLine("C");  // 永远不会执行

d();  // 输出 A 后抛异常，C 被跳过
```

**正确做法**：用 `GetInvocationList()` 逐个调用并隔离异常：

```csharp
foreach (Action a in d.GetInvocationList())
{
    try { a(); }
    catch (Exception ex) { Console.WriteLine($"回调失败: {ex.Message}"); }
}
```

### 4.3 协变与逆变（variance）

委托支持**返回值协变、参数逆变**，让"签名不完全一致但兼容"的方法也能绑定：

```csharp
// 协变：返回值可以是"更派生"的类型
delegate object CoVar();
string GetString() => "hi";
CoVar c = GetString;   // string → object，合法（协变）

// 逆变：参数可以是"更基类"的类型
delegate void ContraVar(string s);
void Print(object o) => Console.WriteLine(o);
ContraVar cv = Print;  // object 参数方法 → 接收 string 委托，合法（逆变）
```

现代 `Action<in T>` / `Func<out T>` 的 `in`/`out` 泛型修饰符正是为方差设计的，框架已帮你标好。

### 4.4 闭包（Closure）与捕获陷阱

Lambda 捕获外部变量会形成**闭包**，被捕获的变量生命周期被延长到委托活着为止：

```csharp
List<Action> actions = new();
for (int i = 0; i < 3; i++)
{
    int local = i;                 // 关键：每次循环新建一个 local
    actions.Add(() => Console.WriteLine(local));
}
foreach (var a in actions) a();    // 输出 0 1 2（正确）
```

**经典坑（C# 5.0 之前）**：若直接捕获循环变量 `i` 而不复制成 `local`，三个委托会全部打印 `3`（因为捕获的是同一变量，循环结束它已是 3）。C# 5.0 起 `foreach` 的循环变量每轮独立，但 `for` 循环的 `i` 仍是同一个——所以上面显式 `int local = i` 是最稳妥的写法，永远别依赖语言版本细节。

闭包还会**阻止被捕获对象被 GC**，是内存泄漏的常见来源（见第 7 节）。

### 4.5 事件（event）：封装过的多播委托

`event` 关键字本质就是"加了访问限制的委托"：

```csharp
public class Button
{
    // 外部只能 += / -=，不能 = 覆盖，也不能直接 Invoke
    public event Action Clicked;

    public void Fire() => Clicked?.Invoke();  // 只有类内部能触发
}

var b = new Button();
b.Clicked += () => Console.WriteLine("被点了");
// b.Clicked();          // 编译错误：外部不能触发
// b.Clicked = null;     // 编译错误：外部不能整体替换
b.Fire();
```

`event` vs 普通 `public` 委托的区别：

| 维度 | `public Action X` | `public event Action X` |
| --- | --- | --- |
| 外部能否 `X = ...` 整体覆盖 | 能（危险，会清掉别人挂的） | 不能（只能 `+=`/`-=`） |
| 外部能否 `X()` 触发 | 能（破坏封装） | 不能（只有声明类内部能触发） |
| 适合场景 | 全局钩子、需被替换的策略入口 | 对象向外界"广播"发生的事件 |

**经验法则**：类要"对外通知发生了什么"→ 用 `event`；要"对外暴露一个可替换的回调入口"→ 才用 `public`（或 `public static`）委托。

### 4.6 异步 Action 与 async void

`Action` 本身不能 `await`。常见两种异步写法：

```csharp
// 写法一：Action 里塞 async lambda —— 实际是 async void，无法 await，异常难捕获
Action doWork = async () => { await Task.Delay(100); };
doWork();   // 触发即忘，抛异常会直接炸到 SynchronizationContext

// 写法二（推荐）：用 Func<Task> 代替 Action 来表达"异步无返回值"
Func<Task> doWorkAsync = async () => { await Task.Delay(100); Console.WriteLine("done"); };
await doWorkAsync();   // 可 await，异常可被 try/catch
```

**铁律**：`async void` 只应出现在"事件处理器 / 顶层入口"这种"本就是 fire-and-forget"的地方；把它塞进 `Action` 多播链会让异常和时序失控。需要异步且要 await，用 `Func<Task>`。

### 4.7 静态 Action 的生命周期与线程安全

`public static Action` 是**全局共享状态**，带来两个必须正视的问题：

1. **生命周期**：只要 AppDomain 活着它就活着，挂上去的 Lambda 若捕获了对象，那个对象也跟着活——潜在内存泄漏。
2. **线程安全**：多线程同时 `+=`/`-=`/`Invoke` 可能竞态（`Combine`/`Remove` 非原子）。高频并发场景应加锁或用 `Concurrent` 集合自己管理订阅者列表。

```csharp
// 线程安全地触发静态 Action 的模板
private static readonly object _lock = new();
public static Action<string> OnEvent;

public static void Raise(string msg)
{
    Action<string> handlers;
    lock (_lock) { handlers = OnEvent; }   // 先复制引用，缩短锁区间
    handlers?.Invoke(msg);                  // 在锁外调用，避免死锁
}
```

---

## 5. 使用场景

| 场景 | 为什么用委托 / Action | 示例 |
| --- | --- | --- |
| **回调（Callback）** | 把"完成后做什么"交给调用方决定 | 文件下载完执行 `Action onDone` |
| **异步完成通知** | 耗时操作结束主动通知 | `Task.ContinueWith(t => ...)` 内部即委托 |
| **策略模式 / 依赖注入** | 把算法当参数传入，避免继承爆炸 | `Sort(items, (a,b) => a.Age.CompareTo(b.Age))` |
| **事件订阅** | 对象广播状态变化 | `button.Click += OnClick` |
| **LINQ / 函数式** | `Where(Predicate)`、`Select(Func)`、`ForEach(Action)` | `list.ForEach(x => Console.WriteLine(x))` |
| **全局钩子 / 插件** | 跨模块解耦，运行时挂载行为 | `public static Action<string> OnLog` |
| **定时器 / UI 跨线程** | `Timer` 回调、`Control.Invoke(Action)` 把代码抛回 UI 线程 | `this.Invoke(() => label.Text = "完成")` |
| **命令模式轻量版** | 把"要做的事"存成 `Action` 队列 | 撤销/重做栈里存 `Action undo` |

### 5.1 实战：`public static Action` 做全局事件总线

```csharp
// 一个极简全局事件总线，全程序任何地方都能发/收，无需引用彼此
public static class EventBus
{
    // 按事件名分组存放订阅者
    private static readonly Dictionary<string, Action<object>> _handlers = new();

    public static void Subscribe(string topic, Action<object> handler)
    {
        if (_handlers.ContainsKey(topic))
            _handlers[topic] += handler;
        else
            _handlers[topic] = handler;
    }

    public static void Publish(string topic, object payload)
    {
        _handlers.TryGetValue(topic, out var h);
        h?.Invoke(payload);
    }
}

// 模块 A：订阅
EventBus.Subscribe("订单创建", data => Console.WriteLine($"收到订单: {data}"));
// 模块 B：发布（完全不引用 A）
EventBus.Publish("订单创建", orderId);
```

这是 `public static Action`（此处是 `Action<object>`）最典型的价值：**彻底解耦发布者与订阅者**，模块间零引用。

---

## 6. 完整可运行示例：把上面串起来

```csharp
using System;
using System.Collections.Generic;

public class Demo
{
    // ① 全局静态 Action 钩子（日志）
    public static Action<string> OnLog;

    // ② 自定义 delegate（内置委托不支持 ref 时才需要）
    public delegate void RefWriter(ref string s);

    // ③ 事件：对外广播
    public event Action<int> OnProcessed;

    public void Run()
    {
        // 订阅静态日志钩子
        OnLog += msg => Console.WriteLine($"[LOG] {msg}");

        // Func 做策略参数
        Func<int, int, int> op = (a, b) => a + b;
        Console.WriteLine($"3+4={op(3, 4)}");

        // 多播
        Action tick = () => Console.WriteLine("tick1");
        tick += () => Console.WriteLine("tick2");
        tick();

        // 触发事件
        OnProcessed?.Invoke(42);
    }
}

class Program
{
    static void Main()
    {
        var d = new Demo();
        d.OnProcessed += n => Console.WriteLine($"已处理: {n}");
        Demo.OnLog = s => { };   // 静态钩子无需实例
        d.Run();
    }
}
```

---

## 7. 注意事项（十大坑）

1. **空委托调用直接 NullReferenceException**：永远用 `handler?.Invoke(args)`（C# 6+ 空条件运算符），绝不要 `handler(args)`。
2. **多播中一个抛异常，后面全不执行**：需要全部执行时用 `GetInvocationList()` 逐个 try/catch。
3. **多播 Func 只返回最后一个值**：要收集全部结果必须逐个调用。
4. **闭包捕获循环变量**：`for` 循环里先 `int local = i;` 再捕获 `local`，别直接捕获 `i`。
5. **闭包导致内存泄漏**：被捕获的对象无法被 GC，长生命周期的 `static` 委托挂了短对象会拖住它。
6. **`async void` 塞进 Action 不可 await、异常失控**：异步无返回值用 `Func<Task>`。
7. **`public static Action` 是全局可变状态**：多线程下 `+=`/`-=` 需加锁或自己管订阅列表。
8. **该用 `event` 却用 `public` 委托**：外部能整体覆盖别人挂的回调、能直接触发——破坏封装，引发诡异 bug。
9. **忘了 `-=` 注销事件/静态钩子**：长期运行的程序（服务、UI）反复 `+=` 不 `-=` 会累积，既泄漏内存又重复执行。
10. **性能敏感路径滥用委托**：委托调用比直接调用多一次间接跳转，且可能堆分配（尤其捕获变量形成的闭包）；超高频循环里考虑直接调用或 `interface` + 结构体。

### 委托 vs 接口 vs 直接调用（性能与可读性权衡）

| 方式 | 间接层级 | 适合 | 不适合 |
| --- | --- | --- | --- |
| 直接调用 | 0 | 固定逻辑、热点循环 | 需运行时替换行为 |
| 委托 / Action / Func | 1（虚表+调用列表） | 回调、事件、策略、LINQ | 每帧百万次的热点内循环 |
| 接口（如 `IStrategy`） | 1（接口分派） | 多方法成组、需 DI 容器、可测试 | 只传一个方法时过重 |

---

## 8. 术语速查

| 术语 | 一句话 |
| --- | --- |
| Delegate | 所有委托的抽象基类，单方法引用 |
| MulticastDelegate | 支持多方法调用列表的委托基类 |
| 方法组转换 | `Calculate op = Add;` 把方法直接赋给委托变量 |
| 调用列表（Invocation List） | 多播委托里挂的所有方法，可用 `GetInvocationList()` 拿到 |
| 协变 / 逆变 | 返回值可更派生 / 参数可更基类 |
| 闭包 | Lambda 捕获外部变量，延长其生命周期 |
| 事件 event | 加了访问限制的委托，外部只能 `+=`/`-=` 不能触发/覆盖 |
| 空条件调用 | `handler?.Invoke()`，避免空引用崩溃 |
| async void | 只能用于事件处理器/顶层入口的"发后不理"异步，不可 await |

---

## 9. 文字脑图（总结）

```
C# 委托体系
├─ 本质：类型安全的函数引用（MulticastDelegate 子类）
├─ 自定义 delegate
│   └─ 仅当内置不支持 ref/out 或需独特语义时使用
├─ 内置委托（优先用）
│   ├─ Action        无返回值（含 public static Action 全局钩子）
│   ├─ Func          有返回值
│   └─ Predicate<T>  条件判断（≈ Func<T,bool>）
├─ 高级
│   ├─ 多播 +=（注意异常/返回值陷阱）
│   ├─ 协变/逆变
│   ├─ 闭包（循环变量 + 内存泄漏）
│   ├─ event（封装版委托）
│   └─ 异步用 Func<Task> 而非 Action+async void
├─ 场景：回调 / 事件 / 策略 / LINQ / 全局钩子 / 命令队列
└─ 坑：空引用 / 多播异常 / 闭包 / 线程安全 / 忘记 -= / async void
```

---

## 10. 快速选型决策

| 你要做什么 | 选 |
| --- | --- |
| 需要一个"做完通知我"的无返回值回调 | `Action` |
| 需要"算完返回给我" | `Func<T, TResult>` |
| 跨模块全局钩子、无需实例 | `public static Action`（注意线程安全与泄漏） |
| 类对外广播"发生了某事" | `event Action` / `event EventHandler<T>` |
| 传单个算法、可测试、多个方法成组 | 接口 `IStrategy` |
| 需要 ref/out 参数 | 自定义 `delegate` |
| 异步无返回值且要 await | `Func<Task>` |
