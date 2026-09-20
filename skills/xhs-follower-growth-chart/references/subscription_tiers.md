# 付费订阅方案设计

## 订阅等级

### 免费版 (Free)
- **价格**: ¥0
- **账号类型**: 限1个
- **推送频率**: 仅周榜
- **图表类型**: 基础柱状图
- **历史数据**: 最近7天
- **功能限制**:
  - 仅可查看榜单，不可下载高清图表
  - 无趋势分析功能
  - 无数据导出

### 基础版 (Basic)
- **价格**: ¥29/月 或 ¥299/年（省¥49）
- **账号类型**: 限3个
- **推送频率**: 日榜 + 周榜
- **图表类型**: 柱状图、折线图、对比图
- **历史数据**: 最近30天
- **功能**:
  - 高清图表下载 (PNG/SVG)
  - 基础趋势分析
  - 邮件推送
  - 数据导出 (CSV)

### 高级版 (Premium)
- **价格**: ¥99/月 或 ¥999/年（省¥189）
- **账号类型**: 无限制
- **推送频率**: 日榜 + 周榜 + 月榜
- **图表类型**: 全部类型 + 自定义图表
- **历史数据**: 无限制
- **功能**:
  - 全部基础版功能
  - 自定义关注列表
  - 竞品对比分析
  - 涨粉预警通知
  - API访问权限
  - 专属客服支持

## 付费流程

### 1. 用户选择订阅等级
```
用户输入: "订阅基础版"
→ 展示等级详情
→ 确认订阅类型和频率
→ 生成订单
```

### 2. 支付处理
支持的支付方式:
- 微信支付
- 支付宝
- 对公转账（企业用户）

### 3. 订阅激活
支付成功后:
1. 接收支付平台回调
2. 更新用户订阅状态
3. 激活对应权限
4. 发送确认通知
5. 立即生成首份报告

### 4. 续费管理
- 到期前7天发送续费提醒
- 支持自动续费
- 到期后保留7天数据访问权限

## 数据表设计

### subscriptions 表
```sql
CREATE TABLE subscriptions (
    id VARCHAR(32) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    tier ENUM('free', 'basic', 'premium') DEFAULT 'free',
    status ENUM('active', 'expired', 'cancelled') DEFAULT 'active',
    start_date DATE NOT NULL,
    end_date DATE,
    auto_renew BOOLEAN DEFAULT FALSE,
    payment_method VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);
```

### payments 表
```sql
CREATE TABLE payments (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    subscription_id VARCHAR(32),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'CNY',
    status ENUM('pending', 'success', 'failed', 'refunded') DEFAULT 'pending',
    payment_method VARCHAR(20),
    transaction_id VARCHAR(128),
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);
```

## 权限验证

每次用户请求时验证:
1. 查询用户当前订阅等级
2. 检查订阅是否有效（未过期）
3. 验证请求功能是否在权限范围内
4. 记录API调用次数（用于限流）

## 降级策略

当用户从高级版降级:
1. 保留当前订阅周期内的权限
2. 到期后自动降级
3. 超出新等级限制的数据保留30天
4. 发送降级提醒和挽留优惠

## 退款政策

- 7天内无理由退款（首次订阅）
- 按比例退款（年付用户）
- 退款后保留当月访问权限
