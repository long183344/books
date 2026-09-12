# 腾讯云云开发 CloudBase · 开发与部署详解

> 本文源自《本地店 AI 自动化服务方案》—— 该方案把 CloudBase 列为「国内微信生态最省事的一体化后端平台」。
> 本文把它彻底讲透：**CloudBase 是什么、核心能力有哪些、本地怎么开发、函数/数据库/存储/触发器怎么用，
> 以及一条从零到上线的完整部署流水线**，并给出「本地店 AI 自动化」三大服务的 CloudBase 落地映射。
>
> 一句话定位：**CloudBase = 腾讯云的 BaaS + Serverless 一体化后端云平台，微信生态的「亲儿子」，
> 让个人开发者不用买服务器、不用管运维，就能跑通云函数 + 数据库 + 存储 + 定时任务 + 微信云调用。**

---

## 0. 为什么是 CloudBase（与源方案的衔接）

在《本地店 AI 自动化服务方案》里，给本地小店做「AI 店长助手」（客服 Agent / 朋友圈生成 / 表格整理）时，
选型第一要素是：**国内本地店基本走微信生态，能否顺滑对接微信、要不要备案域名**。

对比表里 CloudBase 拿了 ⭐⭐⭐⭐⭐（微信友好度最高），原因是它本身就是腾讯的产品：

| 能力 | 是否原生自带 | 对本地店方案的意义 |
| --- | --- | --- |
| 云函数（跑 LLM 编排逻辑） | ✅ | 替代 Cloudflare Worker 做中枢 |
| 云数据库（存知识库/配置） | ✅ | 替代 KV / D1 |
| 云存储（存 Excel/图片） | ✅ | 表格整理场景直接读文件 |
| 定时触发器（朋友圈 Cron） | ✅ | 直接替代 Cron Triggers |
| 微信云调用（免 token） | ✅ | 直接调企业微信/订阅消息，不用自己管 access_token |
| HTTP 访问服务（云接入） | ✅ | 暴露 HTTPS 给企业微信回调 |

> 结论：源方案里用 Cloudflare Worker + KV + Cron 拼起来的三件套，在 CloudBase 里是**一个平台原生的全家桶**，
> 且天然打通微信——这也是它被列为「最推荐」的原因。本文后面第 6 节会逐项映射。

---

## 1. CloudBase 是什么

### 1.1 定义
- **腾讯云云开发（CloudBase，TCB）**：一站式**后端云服务**，把「计算、数据库、存储、托管、鉴权、微信能力」打包，
  你只写业务逻辑（主要是云函数），其余运维由平台接管。
- 形态上等于 **BaaS（后端即服务）+ FaaS（函数即服务 / Serverless）** 的组合。

### 1.2 与微信的关系（关键认知）
- **微信小程序云开发** = CloudBase 在小程序侧的集成形态（同一套引擎、同一套 API）。
- 除了小程序，CloudBase 也支持 **Web（H5）、公众号、企业微信、Flutter、Node 服务端** 等任意客户端。
- 所以你用 CloudBase 写一次后端，可以同时服务小程序、H5、企业微信机器人。

### 1.3 核心能力矩阵

| 能力 | 说明 | 类比（源方案里是谁） |
| --- | --- | --- |
| 云函数 Cloud Functions | 事件驱动的无服务器计算 | Cloudflare Worker |
| 云数据库 Cloud Database | NoSQL 文档型（JSON，类 MongoDB） | D1 |
| 云存储 Cloud Storage | 文件对象存储 | R2 |
| 静态网站托管 Hosting | 托管前端静态资源 + 默认域名 | Pages |
| 定时触发器 Timer | CRON 触发云函数 | Cron Triggers |
| 云接入 / HTTP 访问 | 把云函数暴露为 HTTPS 接口 | Worker 路由 |
| 微信云调用 Cloud Call | 免 access_token 调微信开放接口 | ——（CloudBase 独有优势） |
| 身份认证 Auth | 微信/手机号/匿名登录 | —— |
| 内容管理 CMS | 可视化数据后台 | —— |

---

## 2. 核心能力详解

### 2.1 云函数（Cloud Functions）—— 整个方案的中枢

**① 运行时**
- Node.js（主流，生态好）、Python、PHP、Java、Go 均支持。
- 本地店 AI 方案建议 **Node.js**（调 LLM SDK、解析企业微信消息最顺手）。

**② 触发方式**
| 触发源 | 场景 |
| --- | --- |
| **HTTP 访问（云接入）** | 企业微信 / 公众号回调、前端 AJAX 调用 |
| **定时触发器 Timer** | 每天定时生成朋友圈、日报 |
| 数据库变更触发 | 数据写入后自动处理（如新订单触发通知） |
| 消息队列 CMQ | 异步解耦、削峰 |
| 调用其他函数 | 函数编排 |

**③ 函数入口（Node.js 示例）**
```javascript
// cloudfunctions/ai-reply/index.js
exports.main = async (event, context) => {
  // event：HTTP 触发时包含 body/headers/queryString；定时触发时为空或自定义参数
  const { text } = event;
  const kb = await db.collection('shop_faq').limit(1).get();
  const reply = await callLLM(`你是奶茶店客服。知识库：${kb} 顾客问：${text}`);
  return { reply };
};
```

**④ 依赖管理**
- 本地 `npm install` 后连同 `node_modules` 一起部署（简单直接）。
- 更优：用**层（Layer）**把 axios / SDK 等公共依赖打包复用，减小每次部署体积、加快冷启动。

**⑤ 环境变量与配置**
- 密钥（LLM API Key、企业微信 Secret）放**环境变量**，不要硬编码进代码。
- CloudBase 控制台「环境 → 云函数 → 配置 → 环境变量」设置，部署后生效。

**⑥ 日志与监控**
- 控制台「日志」实时查看 `console.log`；「监控」看调用次数、错误率、耗时。
- 排错第一现场就是这里。

### 2.2 云数据库（Cloud Database）—— 知识库与配置的归宿

**① 数据模型**
- **文档型（Document）**，按「环境 → 数据库 → 集合 Collection → 文档 Document（JSON）」组织。
- 例：集合 `shop_faq` 存每家店的问答；集合 `shop_config` 存活动规则。

**② 权限模型（非常重要）**
| 权限 | 含义 | 何时用 |
| --- | --- | --- |
| 所有用户可读写 | 任何人可改 | ❌ 几乎不用（危险） |
| 所有用户可读，仅创建者可写 | 公开只读数据 | 公开配置 |
| 仅创建者可读写 | 用户私有数据 | 用户个人数据 |
| 仅管理端（云函数）可读写 | **服务端专属** | ✅ 知识库、配置（推荐） |

- **关键原则**：知识库、配置、对话历史这类数据，权限设「仅管理端」，只能由云函数（服务端）读写，
  前端 SDK 拿不到，避免被刷库。

**③ 增删改查（服务端 SDK）**
```javascript
const tcb = require('@cloudbase/node-sdk');
const app = tcb.init({ env: tcb.SYMBOL_CURRENT_ENV });
const db = app.database();
await db.collection('shop_faq').add({ q: '营业时间', a: '10:00-22:00' });
const res = await db.collection('shop_faq').where({ q: '营业时间' }).get();
```

**④ 索引与聚合**
- 高频查询字段建索引（如 `shop_id`），否则全表扫描慢。
- 支持 `aggregate()` 做分组统计（表格整理场景算销售额可直接用）。

### 2.3 云存储（Cloud Storage）—— 文件与图片

- 上传 Excel / 图片：`app.uploadFile({ cloudPath, fileContent })`。
- 下载 / 临时链接：`app.getTempFileURL({ fileList })`。
- 权限同样分「所有用户/仅创建者/仅管理端」。
- 表格整理服务：老板把 Excel 丢进云存储 → 云函数读出来用 Node 的 `xlsx` 库解析清洗。

### 2.4 静态网站托管（Hosting）—— 前端落地

- 把编译后的前端（Vue/React 产物、纯 HTML）托管到 CloudBase，**自动给默认域名 + HTTPS**。
- 默认域名形如 `xxx.tcloudbaseapp.com`，可绑定自己的已备案域名。
- 适合做：老板用的管理后台网页、给顾客的小程序 H5 落地页。

### 2.5 微信云调用（Cloud Call）—— CloudBase 的独门优势

- **免 access_token**：传统调微信接口要先 `getAccessToken`（还要管过期、刷新），CloudBase 的云调用直接帮你做鉴权。
- 能调：企业微信消息推送、订阅消息、微信支付、小程序码、内容安全（imgSecCheck）等。
- 对应源方案：朋友圈生成后**直接云调用企业微信「客户朋友圈」API 真自动发**，不必再折腾 token。

### 2.6 定时触发器（Timer）—— 朋友圈/日报的发动机

- 在云函数的 `config.json` 里声明，用 **CRON 表达式**配置。
```json
{
  "triggers": [
    {
      "name": "daily-moments",
      "type": "timer",
      "config": "0 0 9 * * * *"   // 每天 09:00（CloudBase 为 7 段式：秒 分 时 日 月 周 年）
    }
  ]
}
```
- 触发时 `event` 为空或自定义参数，函数里直接跑「调 LLM 生成文案 → 云调用推送老板」。

### 2.7 云接入 / HTTP 访问服务 —— 企业微信回调地址

- 在控制台「云接入 → 新建」绑定一个云函数，平台给你一个 `https://xxx.apigw.tencentcs.com/...` 的 HTTPS 地址。
- 把这个地址填到**企业微信后台「接收消息 URL」**，企业微信发来的 XML/JSON 消息就进你的云函数。
- 注意：企业微信会做 **URL 校验（GET 回显 echostr）**，函数里要正确处理 GET 与 POST。

---

## 3. 本地开发环境搭建

### 3.1 注册与开通
1. 注册腾讯云账号并**实名认证**（国内云服务的硬性前提）。
2. 进入 CloudBase 控制台 → 新建**环境**（选「按量计费」或「包年包月」，新用户有免费额度）。
3. 记下**环境 ID（envId）**，后续 CLI/SDK 都要用。

### 3.2 本地工具链
| 工具 | 用途 |
| --- | --- |
| `@cloudbase/cli`（`tcb` 命令） | 命令行登录、初始化、部署、查日志 |
| VS Code 插件「CloudBase」 | 图形化管理环境、一键部署、本地调试 |
| 微信开发者工具 | 小程序云开发一键上传 |
| Node.js / Python | 本地编写与单测 |

```bash
npm install -g @cloudbase/cli      # 装 CLI
tcb login                          # 浏览器扫码登录
tcb env list                       # 查看环境 ID
```

### 3.3 推荐项目结构
```
my-shop-ai/
├─ cloudfunctions/            # 云函数目录
│  ├─ ai-reply/               # 客服 Agent
│  │  ├─ index.js
│  │  ├─ package.json
│  │  └─ config.json          # 触发器（HTTP 访问在控制台开）
│  ├─ moments-gen/            # 朋友圈生成（含定时触发器）
│  │  ├─ index.js
│  │  └─ config.json
│  └─ sheet-clean/            # 表格整理
│     └─ index.js
├─ web/                       # 前端（可选，托管到 Hosting）
├─ .env                       # 本地环境变量（不上传）
└─ README.md
```
> 注意：`.env`、密钥文件**不要**提交；用 CloudBase 控制台的环境变量承载敏感配置。

---

## 4. 云函数开发实战（客服 Agent 骨架）

```javascript
// cloudfunctions/ai-reply/index.js
const tcb = require('@cloudbase/node-sdk');
const app = tcb.init({ env: tcb.SYMBOL_CURRENT_ENV });
const db = app.database();

// 企业微信回调：GET 校验 + POST 收消息
exports.main = async (event) => {
  const { httpMethod, queryString, body } = event;
  if (httpMethod === 'GET') {
    return queryString.echostr;            // URL 校验回显
  }
  const text = parseWeChatMsg(body);       // 解析顾客文本
  // 查这家店的知识库
  const faq = await db.collection('shop_faq').where({ shopId: event.shopId }).get();
  const reply = await callLLM(`你是奶茶店客服。知识库：${JSON.stringify(faq)} 顾客问：${text}`);

  // 兜底：遇到投诉/转人工关键词，推老板，不自己答
  if (/投诉|退货|找老板/.test(text)) {
    await app.callContainer({ /* 云调用推企业微信给老板 */ });
    return '已帮您转接店长~';
  }
  await pushToWeChat(reply);               // 云调用回顾客
  return 'success';
};
```

要点：
- **GET 处理 echostr**（微信校验）与 **POST 处理消息** 在同一函数里分流。
- 知识库从**云数据库**取（替代源方案的 KV）。
- 敏感凭证、LLM Key 走**环境变量**。

---

## 5. 部署流程（本文重点 · 完整流水线）

### 5.1 流程总览
```
本地编码 → tcb login → tcb init(绑定环境) → 部署云函数 → 配置触发器/云接入 → 部署前端(可选) → 验证
```

### 5.2 步骤详解

**Step 1 · 登录**
```bash
tcb login        # 浏览器扫码，生成凭据
```

**Step 2 · 初始化项目（首次）**
```bash
tcb init         # 交互选环境 ID、填项目名，生成 cloudbase 配置
```

**Step 3 · 部署单个云函数**
```bash
cd cloudfunctions/ai-reply
tcb fn deploy ai-reply          # 部署到当前环境
```
- 部署时会自动把 `config.json` 里的**定时触发器**一并创建/更新。

**Step 4 · 部署全部云函数**
```bash
tcb fn deploy --all
```

**Step 5 · 开通云接入（HTTP 地址）**
- 控制台「云接入 → 新建服务 → 绑定云函数 ai-reply」。
- 拿到 HTTPS 地址，填到企业微信后台「接收消息 URL」。
- 设置 API 密钥/限流，防止被刷。

**Step 6 · 部署前端（可选）**
```bash
tcb hosting deploy ./web/dist -e <envId>
# 或控制台拖拽上传
```

**Step 7 · 验证**
- `tcb fn log ai-reply` 看实时日志。
- 用企业微信给店铺发消息，确认能收到 AI 回复。
- 朋友圈：等定时点触发，或控制台「函数 → 测试」手动触发一次看效果。

### 5.3 控制台部署（零命令行）
- 云函数：控制台「新建云函数 → 在线编辑 / 上传 zip」。
- 适合临时改一行、或不想装 CLI 的场景。

### 5.4 微信小程序云开发部署
- 微信开发者工具里点「云开发」开通环境。
- 右键 `cloudfunctions/ai-reply` → 「上传并部署：云端安装依赖」。
- 小程序端用 `wx.cloud.callFunction` 调用，免域名、免 HTTPS 配置。

### 5.5 CI/CD（自动化部署）
- 在 GitHub Actions / 腾讯云 CODING 流水线里：
```yaml
- run: npm i -g @cloudbase/cli
- run: tcb login --apiKeyId ${{secrets.TCB_ID}} --apiKey ${{secrets.TCB_KEY}}
- run: tcb fn deploy --all -e ${{secrets.TCB_ENV}}
```
- 非交互登录用 `--apiKeyId/--apiKey`（在控制台「用户 → 登录授权」生成）。
- 提交代码即自动部署，适合长期维护。

### 5.6 域名与备案（国内合规）
- 默认域名已可用，无需备案即可测试。
- **绑定自己域名**：该域名必须已完成 **ICP 备案**（国内合规硬性要求）。
- 企业微信回调域名也建议用你自己的已备案域名，提升可信度。

---

## 6. 落地「本地店 AI 自动化」的 CloudBase 映射

把源方案的三件套，整套搬进 CloudBase：

| 源方案组件 | CloudBase 对应 | 说明 |
| --- | --- | --- |
| Cloudflare Worker 中枢 | **云函数**（ai-reply / moments-gen / sheet-clean） | 三个函数各司其职 |
| KV / D1 知识库 | **云数据库**（集合 shop_faq / shop_config） | 权限设「仅管理端」 |
| Cron Triggers | **定时触发器**（moments-gen 的 config.json） | 每天 9 点生成朋友圈 |
| 企业微信回调 | **云接入**（HTTP 地址） | 填到企微后台 |
| LLM 调用 | 云函数内 `fetch` / SDK | Key 走环境变量 |
| 朋友圈发布 | **微信云调用**（客户朋友圈 API） | 免 token 真自动发 |
| Excel 表格处理 | **云存储** 存文件 + 云函数 `xlsx` 解析 | 完整 Node 运行时，比纯前端强 |
| 日报推送 | 云函数 + 云调用 / 云数据库聚合 | 定时算销售额 TOP |

**CloudBase 版架构图**
```
顾客 / 店老板
      │
      ▼
企业微信 / 公众号（合规入口）
      │ 回调 URL
      ▼
云接入 HTTPS → 云函数 ai-reply（客服 Agent）
                 ├─ 查 云数据库 shop_faq
                 ├─ 调 国内 LLM（DeepSeek/通义）
                 └─ 云调用 回写企业微信
定时触发器 09:00 → 云函数 moments-gen（朋友圈生成）
                 └─ 云调用 客户朋友圈 API
云函数 sheet-clean：读 云存储 Excel → xlsx 解析 → 聚合 → 云数据库/推送
```

> 一句话：源方案用 Cloudflare 拼出来的全家桶，在 CloudBase 里是**原生一站式**，且微信打通度最高。

---

## 7. 与其他部署方案对比（结合源方案第 4 节）

| 方案 | 微信友好度 | 成本 | 上手 | CloudBase 相对优势 |
| --- | --- | --- | --- | --- |
| **腾讯云 CloudBase** | ⭐⭐⭐⭐⭐ | 低（有免费额度） | 中 | 微信原生打通、全家桶、免备案测试域名 |
| 腾讯云函数 SCF | ⭐⭐⭐⭐⭐ | 低（按量） | 中 | SCF 只算函数，CloudBase 多了库/存储/托管一体化 |
| 轻量 VPS + Docker | ⭐⭐⭐ | ¥30–80/月 | 较高 | VPS 数据全自管，但需自己配回调域名/备案 |
| Cloudflare | ⭐⭐ | 免费起 | 低 | CF 海外生态好，但国内微信回调、访问速度吃亏 |
| Vercel / Railway | ⭐⭐ | 免费→$5 | 低 | 海外，微信生态摩擦大 |
| n8n 自托管 | ⭐⭐⭐ | VPS ¥30 | 低（不写码） | n8n 拖拽快，但深度定制不如写函数 |

> 选型口诀（来自源方案）：**走国内微信生态选腾讯系（CloudBase / SCF）；要完全可控选 VPS；不想写码选 n8n。**

---

## 8. 成本与免费额度

- **新用户免费额度**：CloudBase 提供一定额度的资源包（云函数调用次数、数据库读写、存储容量、流量），
  个人开发者做 1–2 家店 demo 基本够用。
- **按量计费**：超出免费额度后按调用次数、存储、流量计费，单价低，小店量级几乎可忽略。
- **省钱建议**：
  1. 冷启动敏感的函数用「常驻」或减小依赖（用 Layer）；
  2. 定时任务合并，减少函数调用次数；
  3. 大文件走云存储而非数据库；
  4. 前端静态资源开 CDN 缓存，降流量费。

---

## 9. 常见坑与最佳实践

| 坑 | 现象 | 解决 |
| --- | --- | --- |
| 忘记 GET 校验 | 企业微信回调配不上 | 函数同时处理 GET（回显 echostr）与 POST |
| 密钥硬编码 | 泄露风险 | 一律走环境变量 |
| 数据库权限过松 | 被刷库 | 知识库/配置设「仅管理端」 |
| 云函数超时 | LLM 慢导致 504 | 调大超时（默认 3s→可设更长）+ 异步处理 |
| 冷启动慢 | 首次调用卡 | 减小依赖体积、用 Layer、低频可常驻 |
| 绑定域名未备案 | 国内无法访问 | 先备案，或用默认域名测试 |
| 定时触发器不生效 | config.json 没部署 | 部署函数时一并部署触发器，或控制台手动建 |
| 微信 token 过期 | 自管 token 报错 | 改用**云调用**免 token |

**最佳实践清单**
- ✅ 一个服务一个函数，单一职责，易维护。
- ✅ 所有外部凭证进环境变量 / 密钥管理。
- ✅ 数据库按「服务端仅管理端」权限设计。
- ✅ 必须有人工兜底（投诉/转人工关键词触发老板介入）。
- ✅ 日志即排错现场，函数里多打结构化 `console.log`。

---

## 10. 术语速查表

| 术语 | 含义 |
| --- | --- |
| CloudBase / TCB | 腾讯云云开发 |
| 云函数 | 无服务器计算单元（FaaS） |
| 云数据库 | NoSQL 文档型数据库 |
| 云存储 | 文件对象存储 |
| 云接入 / HTTP 访问 | 把云函数暴露成 HTTPS 接口 |
| 定时触发器 Timer | CRON 触发云函数 |
| 微信云调用 | 免 token 调微信开放接口 |
| 层 Layer | 复用依赖包，加速部署 |
| 环境 env | 独立资源集合（envId 标识） |
| 默认域名 | CloudBase 自动分配的 `xxx.tcloudbaseapp.com` |
| ICP 备案 | 国内绑自有域名的合规前提 |

---

## 11. 一页脑图（文字版）

```
                腾讯云 CloudBase（微信亲儿子）
   ┌──────────┬──────────┬──────────┬──────────┬──────────┐
  云函数       云数据库     云存储      静态托管     微信云调用
   │           │           │           │           │
 触发:       文档型      文件/图片    前端H5      免token
 HTTP/定时    shop_faq    Excel      默认域名     企微/支付
   │           │           │          +HTTPS     订阅消息
   └──────────┴──── 中枢编排：本地店 AI 店长助手 ────┘
       客服Agent   朋友圈生成   表格整理
```

---

## 关联文档
- 业务背景与报价：见《本地店 AI 自动化服务方案》（同仓库 `E:\ProgramData\WorkBreak\2026-09-04-15-20-05\本地店AI自动化服务方案.md` 原始讨论）
- 前端如何调用后端：见 `03-编程与开发/Web前后端通信/01-HTML前后端通信详解.md`
```
