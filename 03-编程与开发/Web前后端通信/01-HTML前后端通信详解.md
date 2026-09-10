# HTML 前后端通信详解

> 从两段真实业务代码出发，逐行拆解 jQuery 旧式 AJAX 的两种写法，对比差异，再扩展到
> **从表单提交到 WebSocket** 的全部主流通信技术、HTTP 协议基础、数据序列化、跨域、
> 认证安全、前后端分离架构与实时通信协议，最后给出**现代化重写方案**与常见误区。
>
> 一句话定位：**前端（浏览器里的 HTML/JS）与后端（服务器程序）之间，靠 HTTP/HTTPS
> 这一"快递网络"传递结构化数据（JSON 为主），需要实时双向时再叠加 WebSocket。**

---

## 0. 写在前面：为什么从这两段代码讲起

用户论坛里常看到这样两段"祖传"前端代码（jQuery 时代典型写法）：

```javascript
function save_config() {
    if (!confirm('是否保存信息?'))
      return;
    let o = {};
    o['user'] = $(a_user).val();
    o['dir1'] = $(a_dir1).val();
    o['dir2'] = $(a_dir2).val();
    if ($(a_pass).val().trim() != '') {
      o['pass'] = $(a_pass).val().trim();
    }
   let s = JSON.stringify(o);
   $.post(head_dl_update + '?cmd=1', s);
 }

function call_post(url, data, on_call) {
    $.ajax({
      url: url,
      type: 'POST',
      data: data,
      async: false,
      success: function (ss) {
        on_call(ss);
      }
    });
  }
```

它们都在"把数据 POST 给后端"，但**写法层级、异步性、是否能拿到返回值**天差地别。
本文先拆这两段，再把这个点放大成完整的"前后端通信知识地图"。

---

## 1. 代码逐行拆解

### 1.1 `save_config()` —— `$.post` 语法糖版

| 行 | 含义 |
| --- | --- |
| `if (!confirm(...)) return;` | 浏览器原生弹窗确认；用户取消则直接退出（**confirm 本身是同步阻塞**） |
| `let o = {}` | 用一个普通对象收集表单字段 |
| `o['user'] = $(a_user).val()` | `$(a_user)` 是 jQuery 选择器（或 DOM 元素），`.val()` 取输入框值 |
| `if ($(a_pass).val().trim() != '')` | **安全细节**：密码框非空才放进对象，避免用空串覆盖后端已有密码 |
| `let s = JSON.stringify(o)` | 把对象序列化成 **JSON 字符串** `s` |
| `$.post(head_dl_update + '?cmd=1', s)` | 发 POST 请求；`?cmd=1` 是查询参数；`s` 作为请求体 |

**关键特征：**
- 用的是 `$.post()` —— jQuery 对 `$.ajax()` 的**简写封装**。
- **没有 success / error 回调**：请求发出去就结束，**前端永远不知道成功还是失败**。
- `data` 传的是字符串 `s`，jQuery 发现是字符串就**原样当请求体发送**，不会二次序列化。

### 1.2 `call_post()` —— `$.ajax` 完整版

| 配置 | 含义 |
| --- | --- |
| `url` | 请求地址 |
| `type: 'POST'` | HTTP 方法为 POST |
| `data` | 透传调用方传入的数据（对象或字符串都行） |
| `async: false` | **同步请求**：浏览器主线程被卡住，直到服务器响应才继续 |
| `success: function(ss){ on_call(ss); }` | 成功回调，把响应体 `ss` 交给 `on_call` 处理 |

**关键特征：**
- 用的是 `$.ajax()` —— jQuery AJAX 的**底层完整 API**，可配置项最全。
- 有 `success` 回调，**能拿到并返回后端响应**。
- `async: false` 让调用方可以"**等结果再继续**"，但代价是**冻结 UI**。

---

## 2. 两种写法的本质对比（本文核心）

> 先给结论：`$.post` 本质就是 `$.ajax({ type:'POST', ... })` 的语法糖，
> 两者的差别不在"能力"，而在"**默认配置与你的用法**"。

| 对比维度 | `save_config`（$.post 版） | `call_post`（$.ajax 版） |
| --- | --- | --- |
| API 层级 | `$.post` —— 语法糖（简写） | `$.ajax` —— 底层完整 API |
| 底层等价 | `$.ajax({type:'POST', url, data:s})` | 直接就是 `$.ajax` |
| **异步性** | **异步**（默认 `async:true`，不阻塞 UI） | **同步**（`async:false`，**冻结浏览器**） |
| **能否拿返回值** | 不能（无回调） | 能（`success` → `on_call(ss)`） |
| 错误处理 | 无（失败静默） | 无（没写 `error` 回调） |
| data 处理 | 传 JSON 字符串，原样发出 | 透传（对象→表单串；字符串→原样） |
| Content-Type | 默认 `application/x-www-form-urlencoded` | 默认同左（与 data 实际内容可能不符） |
| 典型用途 | 单向"上报/保存"，不关心结果 | 需要读后端返回再继续的逻辑 |

### 2.1 `$.post` 是 `$.ajax` 的语法糖（证据）

jQuery 源码层面，`$.post` 约等于：

```javascript
function post(url, data, success, dataType) {
  return $.ajax({ type: 'POST', url, data, success, dataType });
}
```

所以 `save_config` 里的 `$.post(url, s)` 完全等价于：

```javascript
$.ajax({ type: 'POST', url: url, data: s });
```

区别只在于：**你有没有把 `success` 传进去**。

### 2.2 异步 vs 同步（最重要的认知差）

- **异步（async:true，默认）**：浏览器发请求后**立刻继续执行后面的 JS**，响应回来时通过回调/Promise 通知你。UI 不卡。
- **同步（async:false）**：JS 执行到这行**原地等待**，服务器不回就一直卡着，**整个页面（标签页）失去响应**。

> ⚠️ `async:false` 在 **XMLHttpRequest 主线程同步请求已被现代浏览器废弃**，jQuery 3.0+ 也对该选项发出弃用警告。
> 它"能拿到返回值"的便利，完全可以用 `async/await` + `fetch` 更优雅地实现（见第 11 节）。

### 2.3 "发了就忘" vs "处理响应"

`save_config` 属于**单向通知型**：配置保存这种场景，用户点确认后前端通常不依赖返回值；
但**至少应给个成功/失败的提示**。`call_post` 属于**请求-响应型**：调用方需要后端算出的结果。

---

## 3. 这两段代码暴露的三个隐患

### 隐患 1：`save_config` 发了就忘，用户无反馈
- 网络断了、后端 500、权限不足 —— 前端**毫无感知**，用户以为保存成功，实则丢失。
- **修复**：补 `success`/`error` 回调，弹出"保存成功/失败"。

### 隐患 2：`call_post` 的 `async:false` 冻结 UI
- 网络慢时页面**完全卡死**，用户以为浏览器崩了。
- 主线程同步 XHR 已被标准废弃，未来可能直接不支持。
- **修复**：改成异步 + `Promise`/回调，或用 `fetch`。

### 隐患 3：JSON 字符串当 data，Content-Type 却不是 JSON
- `$.post(url, s)` 中 `s` 是 `"{"user":".."}"` 这种字符串；jQuery 直接塞进请求体。
- 但默认 `Content-Type: application/x-www-form-urlencoded`。
- 后端若按"表单"解析会失败；若按"JSON"解析，又因 Content-Type 不是 `application/json` 可能拒绝。
- **修复二选一**：
  - 传**对象**让 jQuery 自动转表单串（后端按表单收）；或
  - 显式设 `contentType: 'application/json'` 并发送 JSON 字符串（后端按 JSON 收）。

```javascript
// 正确发 JSON 的 jQuery 写法
$.ajax({
  url: url, type: 'POST',
  contentType: 'application/json; charset=UTF-8',
  data: JSON.stringify(o),          // 字符串
  success: ..., error: ...
});
```

---

## 4. 前后端通信全景：从表单到 WebSocket

这两段代码只是"冰山一角"。完整的技术演进如下：

### 4.1 最原始：HTML 表单提交（Form Submit）
```html
<form action="/save" method="post">
  <input name="user"><button>提交</button>
</form>
```
- 浏览器原生，无需 JS。
- **缺点**：提交后**整页刷新跳转**，体验差，无法局部更新。

### 4.2 AJAX 鼻祖：XMLHttpRequest（XHR，2005 前后）
- 第一个让"不刷新页面也能请求"的 API（AJAX 一词由此而来）。
- 原生、啰嗦、回调地狱。
- jQuery 的 `$.ajax` 就是对 XHR 的封装。

### 4.3 jQuery 时代：`$.ajax` / `$.post` / `$.get` / `$.getJSON`
- 抹平浏览器差异，API 友好（本文代码即此范式）。
- 今天仍大量存在于遗留系统，但新项目已不推荐。

### 4.4 现代原生：Fetch API（ES2015+）
```javascript
const res = await fetch('/api/save', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(o)
});
const data = await res.json();
```
- 原生、**基于 Promise**、语法简洁、可配合 `async/await`。
- 默认**不携带 Cookie**（需 `credentials: 'include'`）。
- **特别注意**：HTTP 错误状态码（404/500）**不会 reject**，需手动 `if (!res.ok) throw`。

### 4.5 工程化首选：Axios
- 第三方库，基于 XHR（浏览器）/http（Node）。
- 自动 JSON 序列化/反序列化、拦截器、超时、取消请求、错误按状态码 reject。
- 大型前端项目（Vue/React）最常用。

### 4.6 全双工实时：WebSocket
- 一次 HTTP 握手升级为**长连接**，之后**双向实时**收发（服务器可主动推）。
- 适合聊天、行情、实时监控、协同编辑。

### 4.7 服务器单向推送：SSE（Server-Sent Events）
- 基于 HTTP，服务器**单向**持续推文本流，浏览器用 `EventSource` 接收。
- 比 WebSocket 轻，适合日志流、通知。

### 4.8 轮询 / 长轮询
- 轮询：定时 `setInterval` 发请求查新数据（简单但浪费）。
- 长轮询：请求挂起直到有数据才返回（类实时，已被 SSE/WS 取代）。

### 技术对比总表

| 技术 | 年代 | 是否原生 | 异步 | 能否拿响应 | 实时 | 现状 |
| --- | --- | --- | --- | --- | --- | --- |
| Form 提交 | 1990s | ✅ | 否（整页刷新） | 靠跳转页 | 否 | 仍用（简单表单） |
| XHR | 2000s | ✅ | ✅ | ✅ | 否 | 被封装 |
| jQuery $.ajax | 2006+ | ❌（库） | ✅ | ✅ | 否 | 遗留系统 |
| Fetch | 2015+ | ✅ | ✅(Promise) | ✅ | 否 | **现代原生标配** |
| Axios | 2014+ | ❌（库） | ✅ | ✅ | 否 | **工程化首选** |
| WebSocket | 2011+ | ✅ | ✅(事件) | ✅(双向) | ✅全双工 | 实时场景 |
| SSE | 2009+ | ✅ | ✅(事件) | ✅(单向) | ✅单向推 | 通知/流 |

---

## 5. HTTP 协议基础（通信基石）

### 5.1 请求-响应模型 + 无状态
- 每次请求**独立**：客户端发请求 → 服务器返回响应 → 连接关闭（HTTP/1.1 可复用）。
- **无状态**：服务器默认不记得"上一个请求是谁"，状态靠 Cookie/Session/Token 维持。

### 5.2 常用方法

| 方法 | 语义 | 是否带 body | 幂等 |
| --- | --- | --- | --- |
| GET | 取资源 | 否（参数在 URL） | ✅ |
| POST | 新建/提交 | ✅ | ❌ |
| PUT | 整体替换 | ✅ | ✅ |
| PATCH | 局部修改 | ✅ | ❌ |
| DELETE | 删除 | 多否 | ✅ |
| HEAD | 只取响应头 | 否 | ✅ |
| OPTIONS | 预检/探测 | 否 | ✅ |

> 本文的 `$.post` 对应 **POST**；`$.ajax({type:'POST'})` 同理。

### 5.3 状态码（必须记住的几组）

| 段 | 含义 | 典型 |
| --- | --- | --- |
| 2xx | 成功 | 200 OK / 201 Created / 204 No Content |
| 3xx | 重定向 | 301 永久 / 302 临时 / 304 缓存未变 |
| 4xx | 客户端错 | 400 参数错 / 401 未认证 / 403 禁止 / 404 不存在 / 422 校验失败 |
| 5xx | 服务端错 | 500 内部错 / 502 网关错 / 503 过载 / 504 超时 |

> 注意：**Fetch 在 4xx/5xx 时不会抛异常**，需 `res.ok` 判断；Axios 会直接 reject。

### 5.4 关键请求头 / 响应头

| 头 | 作用 |
| --- | --- |
| `Content-Type` | 请求体/响应体格式（见 5.5） |
| `Authorization` | 认证凭证（Bearer Token / Basic） |
| `Cookie` | 会话标识 |
| `Accept` | 客户端能接受的响应格式 |
| `Origin` | 跨域请求来源（CORS 用） |
| `Access-Control-Allow-Origin` | 服务器允许的来源（CORS 用） |
| `Cache-Control` | 缓存策略 |

### 5.5 Content-Type 全解（前后端必对齐）

| Content-Type | 适用 | 示例 body |
| --- | --- | --- |
| `application/json` | **现代 API 主流** | `{"user":"a","pass":"x"}` |
| `application/x-www-form-urlencoded` | 传统表单 / jQuery 默认 | `user=a&pass=x` |
| `multipart/form-data` | **文件上传** | 二进制分块 |
| `text/plain` | 纯文本 | 任意字符串 |

> 第 3 节隐患 3 的根因：**body 是 JSON，Content-Type 却是 urlencoded** → 前后端约定不一致。

---

## 6. 数据序列化格式

| 格式 | 特点 | 用法 |
| --- | --- | --- |
| **JSON** | 轻量、前后端通用、现代标配 | `JSON.stringify` / `JSON.parse` |
| FormData | 表单/文件上传天然支持 | `new FormData(form)` |
| URLSearchParams | 拼 `a=1&b=2` | `new URLSearchParams(obj)` |
| XML | 老式 SOAP / 早期 AJAX | 已淘汰 |
| Blob / ArrayBuffer | 二进制（图片、音视频、文件） | 文件下载/上传 |

**jQuery 对 `data` 的处理逻辑：**
- 传**对象** → 自动 `$.param()` 序列化成 `a=1&b=2`（urlencoded）。
- 传**字符串** → 原样当请求体（如本文 `save_config` 的 JSON 串）。
- 传 **FormData** → 直接发（需 `processData:false` + 不设 contentType，让浏览器自己定 boundary）。

```javascript
// 文件上传的正确姿势
let fd = new FormData();
fd.append('file', fileInput.files[0]);
$.ajax({ url, type:'POST', data: fd, processData:false, contentType:false });
```

---

## 7. 跨域与同源策略

### 7.1 同源策略（SOP）
"同源" = **协议 + 域名 + 端口** 三者全同。不同源的前端 JS **默认不能**读另一个源的资源。

### 7.2 CORS（跨域资源共享，现代正解）
- 简单请求：后端响应头带 `Access-Control-Allow-Origin: *`（或具体域名）即可。
- 非简单请求（带自定义头、JSON body、PUT 等）：浏览器先发 **OPTIONS 预检**，通过才发真请求。

### 7.3 JSONP（老式跨域，与 jQuery 强相关）
```javascript
$.getJSON('https://api.com/data?callback=?', fn); // 利用 <script> 不受同源限制
```
- 只支持 GET，靠后端把数据包成 `callback({...})` 返回。
- 已被 CORS 取代，仅遗留系统使用。

### 7.4 代理（开发期最常用）
- 开发服务器（Vite/Webpack）配 `proxy`，前端请求 `/api` → 服务器转发到真实后端，**绕过浏览器跨域**。
- 生产用 Nginx 反向代理同理。

---

## 8. 身份认证与安全

### 8.1 会话维持三件套
| 方案 | 机制 | 特点 |
| --- | --- | --- |
| Cookie + Session | 服务器存会话，浏览器带 Cookie | 传统、易 CSRF |
| JWT（Token） | 服务器签令牌，前端每次放 `Authorization` 头 | 无状态、易扩展 |
| OAuth2 / OIDC | 第三方授权（微信/Google 登录） | 委托授权 |

### 8.2 HTTPS
- 所有通信应走 **HTTPS**（TLS 加密），否则 Token/密码明文裸奔。

### 8.3 三大前端安全坑
- **XSS**：恶意脚本注入页面 → 窃取 Cookie/Token。应对：转义输出、CSP、`HttpOnly` Cookie。
- **CSRF**：诱骗用户浏览器向已登录站点发请求。应对：CSRF Token、`SameSite` Cookie。
- **敏感信息泄露**：别在前端硬编码密钥；密码别明文传（至少 HTTPS + 后端哈希）。

> 回到本文代码：`save_config` 把密码 `pass` 明文放进 JSON 发出 —— 必须保证链路是 HTTPS，且后端加盐哈希存储。

---

## 9. 前后端分离与现代架构

### 9.1 接口风格
| 风格 | 特点 |
| --- | --- |
| **RESTful** | 资源 + HTTP 方法，URL 表意（`GET /users/1`），JSON 交互，最主流 |
| GraphQL | 前端按字段精确取数，一次拿全，避免过度/不足请求 |
| gRPC / RPC | 高性能二进制，服务间内部调用，前端多用 REST |

### 9.2 架构演进
- **前后端不分离**（JSP/PHP 模板）：HTML 由后端拼好直接返回。
- **前后端分离**：前端独立工程（Vue/React），通过 API 拿数据渲染 SPA。
- **BFF（Backend For Frontend）**：加一层专为前端聚合的网关，减少前端多次请求。
- **API 网关**：统一鉴权、限流、路由。

---

## 10. 实时通信协议详解

| 协议 | 连接 | 方向 | 适用 |
| --- | --- | --- | --- |
| 轮询 | 短连接反复建 | 客户端→服务器 | 实时要求低、实现简单 |
| 长轮询 | 挂起直到有数据 | 客户端→服务器（伪实时） | 过渡方案 |
| **SSE** | 长连接 | 服务器→客户端（单向） | 通知、日志流、行情推送 |
| **WebSocket** | 长连接 | **双向全双工** | 聊天、协同、实时监控 |

### WebSocket 要点
- 握手：`GET` + `Upgrade: websocket` + `Sec-WebSocket-Key` → 101 Switching Protocols。
- 之后走二进制/文本帧，极低开销。
- 需**心跳**（定时 ping/pong）防止中间代理断开；需**断线重连**逻辑。

---

## 11. 现代重写：把两段代码升级

### 11.1 用 Fetch 重写 `save_config`（异步、有反馈、发 JSON）

```javascript
async function save_config() {
  if (!confirm('是否保存信息?')) return;
  const o = {
    user: document.querySelector(a_user).value,
    dir1: document.querySelector(a_dir1).value,
    dir2: document.querySelector(a_dir2).value,
  };
  const pass = document.querySelector(a_pass).value.trim();
  if (pass !== '') o.pass = pass;

  try {
    const res = await fetch(head_dl_update + '?cmd=1', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(o),
    });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    alert('保存成功');
  } catch (e) {
    alert('保存失败：' + e.message);
  }
}
```

### 11.2 用 Fetch + Promise 重写 `call_post`（去掉 async:false）

```javascript
function call_post(url, data, on_call) {
  return fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: typeof data === 'string' ? data : JSON.stringify(data),
  })
    .then(res => {
      if (!res.ok) throw new Error('HTTP ' + res.status);
      return res.text();          // 或 res.json()
    })
    .then(on_call)
    .catch(err => console.error('请求失败', err));
}
```

### 11.3 用 Axios 版本（工程化最佳）

```javascript
import axios from 'axios';

async function save_config() {
  if (!confirm('是否保存信息?')) return;
  const o = { /* ...收集... */ };
  try {
    const { data } = await axios.post(head_dl_update + '?cmd=1', o);
    alert('保存成功');
  } catch (e) {
    alert('保存失败：' + e.message);
  }
}
```
> Axios **自动**把对象转 JSON 并设好 `Content-Type`，错误按状态码 reject，省心。

---

## 12. 常见误区与调试技巧

### 误区清单
1. **"POST 比 GET 安全"** —— 错。两者都明文（除非 HTTPS），GET 参数在 URL 更易泄露。
2. **"Fetch 失败会抛异常"** —— 错。仅网络层失败才 reject，4xx/5xx 需手动判断。
3. **"`async:false` 能方便拿返回值"** —— 代价是冻结 UI，已废弃，改用 `await`。
4. **"JSON 字符串直接当 data 发没问题"** —— 需对齐 Content-Type，否则后端解析错。
5. **"前端校验就够了"** —— 前端校验只是体验，后端必须再校验（前端可被绕过）。
6. **"跨域是前端 bug"** —— 跨域是浏览器策略，需后端配 CORS 或走代理。

### 调试技巧
- **Network 面板**：看请求方法、URL、请求头、请求体、响应状态码与内容。
- **console.log** 打印 `res` 与 `res.status`。
- **Postman / curl** 先验证后端接口，再对接前端。
- **CORS 报错**：看 Console 的 `Access-Control-Allow-Origin` 提示，找后端。
- **断点**：在 `success`/`.then` 内打断点看数据。

---

## 13. 术语速查表

| 术语 | 一句话 |
| --- | --- |
| AJAX | 异步 JS + XML，不刷新页面发请求的老概念 |
| XHR | 原生异步请求对象，AJAX 的基础 |
| Fetch | 现代原生请求 API，基于 Promise |
| Axios | 流行的第三方 HTTP 库 |
| SOP | 同源策略，限制跨源访问 |
| CORS | 跨域资源共享，合法的跨域方案 |
| JSONP | 老式跨域（script 标签 hack），仅 GET |
| REST | 资源式 API 风格 |
| WebSocket | 全双工实时长连接 |
| SSE | 服务器单向推送 |
| JWT | JSON Web Token，无状态认证 |
| CSRF / XSS | 两种前端常见攻击 |

---

## 14. 一页脑图（文字版总结）

```
                前端 HTML/JS
                     │
        ┌────────────┼─────────────────────────┐
        │            │                          │
   非实时请求      实时通道                    辅助机制
        │            │                          │
  ┌─────┴────┐   ┌──┴────┐   ┌────────┐   ┌────┴─────┐
 Form提交   AJAX   WebSocket  SSE     跨域CORS   认证JWT
  (刷新)  ┌─┴─┐    (双向)  (单推)       代理       Cookie/Session
        XHR  Fetch                  JSONP(老)
        jQuery Axios
        (本文代码)
```

> **本文两段代码归属**：`save_config` → jQuery `$.post`（语法糖、异步、无回调）；
> `call_post` → jQuery `$.ajax`（底层、同步 `async:false`、有 success 回调）。
> 现代项目请直接用 **Fetch / Axios + async/await**，告别 `async:false` 与"发了就忘"。

---

## 文件清单与关联

- 本文档：`03-编程与开发/Web前后端通信/01-HTML前后端通信详解.md`
- 关联主题：
  - 协议栈基础 → `04-网络与安全/`
  - 同源/HTTPS/认证 → `04-网络与安全/`
  - 工业相机采集（也是前后端/设备通信） → `07-算法/机器视觉硬件/`
```
