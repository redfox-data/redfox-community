# 支付宝充值接管流程（通用）

> 本文件与具体 skill 解耦，可被任意「红狐数据类 skill」直接引用或整份复制。
> 适用场景：skill 的数据接口返回积分不足（body `code=3210`，兼容 `3201`），需唤起支付宝完成充值后继续查询。
> 引用方只需在 SKILL.md 里说明「脚本退出码 3 = 积分不足，按本文件流程处理」，无需重复下列细节。

## 一、触发契约（脚本侧必须实现）

接口积分不足时返回：

```json
{
  "code": 3210,
  "msg": "积分不足，请完成支付后重试",
  "data": {
    "amount": 100,
    "cashierUrl": "https://openapi.alipay.com/gateway.do?...&method=alipay.trade.page.pay&...",
    "goodsName": "RedFox API积分充值（100元=1000积分）",
    "outTradeNo": "RC17925680272927945b769",
    "expireTime": "2026-10-21 16:03:47",
    "points": 1000.0
  }
}
```

字段含义：

| 字段 | 含义 | 用途 |
|------|------|------|
| `data.cashierUrl` | 支付宝收银台链接 | 即支付链接，传给 `--payment-link` |
| `data.amount` | 订单金额（元） | 传给 `--amount` |
| `data.goodsName` | 商品名称 | 传给 `--merchant-info` / `--intent-summary` |
| `data.outTradeNo` | 商户订单号 | 订单追踪（不代表支付成功） |
| `data.expireTime` | 支付截止时间 | 提示用户尽快支付 |

skill 的查询脚本在检测到 `code` 属于 `{3210, 3201}` 时，必须：

- **不**直接报错退出；
- 以**退出码 3** 结束；
- 在 stdout 原样透出支付信息，包在固定标记区块里（金额/商品名已是结构化字段，**无需从 URL 解析**）：

```
===PAYMENT_REQUIRED_JSON_START===
{"need_payment": true, "code": 3210, "msg": "...", "cashierUrl": "<收银台链接原文>", "amount": 100, "goodsName": "<商品名称>", "outTradeNo": "...", "expireTime": "...", "points": 1000.0}
===PAYMENT_REQUIRED_JSON_END===
```

要点：

- 脚本**不改写** `cashierUrl`，原样透出，由 Agent 读取后填充命令参数。
- `3106`（缺 Key）/ `3107`（Key 无效）属于配置问题，必须引导注册/检查 Key，**不得**触发支付流程。

## 二、前置检查（Prerequisite）

在执行任何 `alipay-bot` 命令前：

1. 执行 `npm --version` 确认 `npm` 可用；不可用则停止流程并说明缺少 `npm`。
2. 执行 `which alipay-bot` 确认 CLI 已安装（默认装在 `~/.local/bin/alipay-bot`）。
3. 若未安装，执行安装命令后重试：

```bash
npx -y @alipay/agent-payment@latest install
```

## 三、支付步骤（Agent 编排）

1. 从脚本 stdout 的 `PAYMENT_REQUIRED_JSON` 中读取 `cashierUrl` 原文，作为支付链接。**逐字符完整保留，不要改写、截断、重新编码或压缩。**
2. 读取 `amount`（订单金额，元）与 `goodsName`（商品名称），二者已是结构化字段，直接使用。
3. 调用 `trigger-payment-signal` 压缩链接，得到支付短链：

```bash
alipay-bot trigger-payment-signal \
  --payment-link "<cashierUrl 原文>" \
  --merchant-info "<goodsName>，<amount>元" \
  --amount "<amount>"
```

4. 从 `trigger-payment-signal` 返回 JSON 中读取非空 `paymentLink`（即支付短链）。若为空视为失败并停止。
5. 用支付短链唤起支付宝接管支付，并从输出中解析**查询单号**（`out-shake-no`，形如 `**查询单号**：2026...`）：

```bash
alipay-bot submit-payment \
  --payment-link "<上一步的 paymentLink 支付短链>" \
  --intent-summary "<goodsName>，<amount>元"
```

6. **自动监听到账（不要让用户再手动回一句"支付成功"）**：把付款链接/二维码交付用户后，立即用查询单号轮询支付状态，直到终态：

```bash
alipay-bot poll-payment-status \
  --out-shake-no "<submit-payment 输出的查询单号>" \
  --interval 5000 --max-attempts 60 --json
```

   - 读取返回 JSON 的 `outcome` / `finalStatus`：`success` = 支付已完成（`message: 支付已完成`、`agentOrderDTO.status: SUCCESS`）；`closed` / `timeout` / `error` = 未成功。
   - `--interval 5000 --max-attempts 60` ≈ 轮询 5 分钟，可按收银台 `expireTime` 调整；轮询期间无需用户干预。
   - ⚠️ poll **必须**用 `--out-shake-no`（查询单号）或 `--launch-url`，**不能**用 trigger 的支付短链当 `--payment-link`（会返回 `查询服务未返回支付状态` / `outcome=error`）。
7. `outcome=success` 后，**自动**用用户原始的查询参数重新运行 skill 脚本，走正常逻辑输出结果。仅在 poll 明确返回 success 后才交付；`closed`/`timeout`/`error` 时不交付、不声明充值成功。

## 四、支付接管规则

- `--payment-link` 传给 `trigger-payment-signal` 的必须是 `cashierUrl` 原文；传给 `submit-payment` 的必须是 `trigger-payment-signal` 返回的 `paymentLink` 支付短链，**二者不可混用**。
- 必须逐字符完整保留链接原始值，不要打开、展示、改写、重新编码、压缩或截断。
- 每次充值都重新从本次脚本输出读取 `cashierUrl`，不要复用历史链接（含时间戳与签名，`expireTime` 到期即失效）。
- `--amount` 与 `--merchant-info` 的值必须来自本次响应的 `amount` / `goodsName`，不要替用户编造。
- 支付到账由 `poll-payment-status --out-shake-no` **自动监听**判定，不依赖用户口头确认；只有 poll 返回 `outcome=success` 才重跑脚本并交付结果。

## 五、失败处理

- `npm` 不可用：停止流程，说明本机缺少 `npm`。
- `alipay-bot` 未安装且 `npx -y @alipay/agent-payment@latest install` 失败：停止流程，说明支付宝支付接管 CLI 安装失败。
- `PAYMENT_REQUIRED_JSON` 中没有非空 `cashierUrl`：停止流程，说明未返回收银台链接。
- `trigger-payment-signal` 未返回非空 `paymentLink`：停止流程，说明支付短链生成失败。
- `submit-payment` 未输出查询单号：无法轮询，提示用户在支付宝订单页确认支付状态后再重试。
- `poll-payment-status` 返回 `closed`/`timeout`/`error`：不要交付结果，按状态提示用户（超时未支付可重新发起充值；`error` 多为查询单号有误）。
- 支付成功后重跑脚本仍返回 3210/3201：说明充值未到账或积分仍不足，告知用户稍后重试或联系红狐 hub，**不要反复发起支付**。
