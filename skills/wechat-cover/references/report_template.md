# 爆款封面分析报告 HTML 模板

## 文件说明

本文件为爆款封面分析报告与设计方案的 HTML 模板，技能执行时直接读取本模板填充数据。

**文件路径**：`references/report_template.md`

**⚠️ 重要：按风格类型分类展示封面，不要逐张输出分析结果！**

---

## 完整HTML模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="referrer" content="no-referrer">
    <title>爆款封面分析报告 - {关键词}主题</title>
</head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;line-height:1.6;color:#333;background:#f5f5f5;padding:20px">
    <div style="max-width:1200px;margin:0 auto;background:#fff;border-radius:12px;padding:30px;box-shadow:0 2px 12px rgba(0,0,0,0.08)">
        
        <!-- 报告标题 -->
        <h1 style="color:#1a1a1a;margin-bottom:30px;font-size:28px;border-bottom:3px solid #1890ff;padding-bottom:15px">📊 爆款封面分析报告</h1>
        
        <!-- 数据来源信息 -->
        <div style="background:#e6f7ff;padding:12px 16px;border-radius:8px;margin-bottom:20px">
            <strong>关键词：</strong>{关键词} | <strong>数据来源：</strong>公众号爆款雷达接口 | <strong>分析数量：</strong>{分析数量}张封面
        </div>
        
        <!-- ========== 风格类型分类展示区域 ========== -->
        {风格类型分类列表}
        
        <!-- ========== 设计方案区域 ========== -->
        <hr style="border-top:2px dashed #e8e8e8;margin:40px 0">
        
        <h1 style="color:#1a1a1a;margin-bottom:30px;font-size:28px;border-bottom:3px solid #1890ff;padding-bottom:15px">🎯 爆款封面设计方案</h1>
        
        {设计方案列表}
        
        <!-- ========== 方案选择询问区域 ========== -->
        <hr style="border-top:2px dashed #e8e8e8;margin:40px 0">
        
        <div style="background:#fafafa;border-radius:12px;padding:24px;margin:20px 0;border:1px solid #e8e8e8">
            <h2 style="margin:0 0 16px;font-size:20px;color:#1890ff">🎯 请选择您想要的封面设计方案</h2>
            
            <div style="font-size:15px;line-height:2;color:#333">
                <div style="margin-bottom:8px"><strong>方案一：</strong>{方案一风格名称} - {方案一核心视觉}</div>
                <div style="margin-bottom:8px"><strong>方案二：</strong>{方案二风格名称} - {方案二核心视觉}</div>
                <div style="margin-bottom:16px"><strong>方案三：</strong>{方案三风格名称} - {方案三核心视觉}</div>
                
                <div style="color:#666">
                    <strong>💡 请选择：</strong><br>
                    A. 回复"方案1"、"方案2"或"方案3"直接选择方案<br>
                    B. 如果您有产品图、人物图或场景图想作为参考，可以和方案编号一起发送<br>
                    <span style="margin-left:24px">例如：直接发送图片 + "方案1"</span>
                </div>
            </div>
        </div>
        
    </div>
</body>
</html>
```

---

## 模板填充规范

### 1. 风格类型分类列表填充格式（核心展示区域）

**⚠️ 重要：按风格类型分类展示封面，每个风格类型包含风格描述和代表性封面图**

每种风格类型的HTML结构：
```html
<div style="background:#fafafa;border-radius:12px;padding:24px;margin:20px 0;border:1px solid #e8e8e8">
    <div style="font-size:20px;font-weight:600;color:#1890ff;margin-bottom:8px">{风格名称}</div>
    <span style="display:inline-block;background:#e6f7ff;padding:4px 12px;border-radius:4px;font-size:14px;color:#1890ff;margin-bottom:12px">出现频次：{出现次数}/{总分析数}</span>
    <div style="color:#52c41a;font-weight:500;margin:12px 0">核心视觉：{核心视觉描述}</div>
    <div style="color:#666;font-size:15px;line-height:1.8;margin-bottom:16px">关键特征：{关键特征描述}</div>
    
    <!-- 该风格的代表性封面图（最多5张，横向排列） -->
    <div style="display:flex;flex-wrap:wrap;gap:12px;margin-top:16px">
        <a href="{coverUrl}" target="_blank" style="width:180px;height:77px;border-radius:6px;overflow:hidden;display:block">
            <img src="{coverUrl}" style="width:100%;height:100%;object-fit:cover;object-position:center" alt="封面示例">
        </a>
        <!-- 更多封面图... -->
    </div>
</div>
```

**注意**：
- 每个风格类型最多展示5张代表性封面图
- 过滤掉尺寸过小（宽或高<10px）和空白图片
- 封面图容器比例固定为2.35:1

### 2. 设计方案列表填充格式

每个方案的HTML结构：
```html
<!-- 方案{N} -->
<div style="background:#fafafa;border-radius:12px;padding:24px;margin:25px 0;border:2px solid #1890ff">
    <h2 style="font-size:20px;font-weight:600;color:#1890ff;margin-bottom:12px">方案{N}：{风格名称}</h2>
    <div style="color:#52c41a;font-weight:500;margin:10px 0;font-size:16px">核心视觉：{核心视觉描述}</div>
    
    <h3 style="color:#333;margin:20px 0 15px;font-size:18px">案例参考</h3>
    <div style="background:#fff;border:1px solid #e8e8e8;border-radius:8px;padding:20px;margin:15px 0;display:flex;gap:20px;align-items:flex-start">
        <a href="{coverUrl}" target="_blank" style="width:300px;height:128px;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.1);display:block;flex-shrink:0">
            <img src="{coverUrl}" style="width:100%;height:100%;object-fit:cover;object-position:center;display:block" alt="封面图">
        </a>
        <div style="flex:1">
            <div style="font-size:18px;font-weight:500;margin-bottom:10px">
                <a href="{oriUrl}" target="_blank" style="color:#1890ff;text-decoration:none;font-weight:500">{标题}</a>
            </div>
            <div style="color:#666;font-size:14px;margin:8px 0">作者：{作者名}</div>
            <span style="display:inline-block;background:#fff7e6;color:#fa8c16;padding:4px 12px;border-radius:4px;font-size:13px;font-weight:500">阅读：{阅读数}</span>
        </div>
    </div>
    
    <h3 style="color:#333;margin:20px 0 15px;font-size:18px">生图提示词</h3>
    <div style="background:#f6ffed;border:1px solid #b7eb8f;border-radius:8px;padding:16px;margin:20px 0">
        <div style="color:#52c41a;font-weight:600;margin-bottom:8px">公众号封面图</div>
        <div style="color:#333;font-size:14px;line-height:1.8;background:#fff;padding:12px;border-radius:4px;word-break:break-all">
            2.35:1横版比例（900x383像素）。参考封面：{coverUrl}。{风格描述}。
        </div>
    </div>
</div>
```

---

## 字段说明

| 占位符 | 说明 | 数据来源 |
|--------|------|----------|
| `{关键词}` | 用户输入的主题关键词 | 用户输入 |
| `{分析数量}` | 实际分析的封面图数量 | 接口返回数据（过滤后） |
| `{风格类型分类列表}` | **按风格类型分类的封面展示HTML** | 分析归类后生成 |
| `{风格名称}` | 风格类型名称 | 分析归类 |
| `{出现次数}` | 该风格出现的次数 | 统计 |
| `{总分析数}` | 总分析封面数量 | 统计 |
| `{核心视觉描述}` | 该风格的核心视觉特征 | 分析总结 |
| `{关键特征描述}` | 该风格的关键特征 | 分析总结 |
| `{设计方案列表}` | 3个设计方案的HTML | 分析后生成 |
| `{方案一风格名称}` | 方案一的风格名称 | 分析总结 |
| `{方案一核心视觉}` | 方案一的核心视觉描述 | 分析总结 |
| `{方案二风格名称}` | 方案二的风格名称 | 分析总结 |
| `{方案二核心视觉}` | 方案二的核心视觉描述 | 分析总结 |
| `{方案三风格名称}` | 方案三的风格名称 | 分析总结 |
| `{方案三核心视觉}` | 方案三的核心视觉描述 | 分析总结 |
| `{coverUrl}` | 封面图URL | 接口返回的 coverUrl 字段 |
| `{oriUrl}` | 原文链接URL | 接口返回的 oriUrl 字段 |
| `{标题}` | 文章标题 | 接口返回的 title 字段 |
| `{作者名}` | 作者名称 | 接口返回的 userName 字段 |
| `{阅读数}` | 阅读量 | 接口返回的 clicksCount 字段 |

---

## 样式规范

| 元素 | 样式规则 |
|------|----------|
| 封面图容器比例 | 2.35:1 (180x77px 或 300x128px) |
| 封面图适配 | object-fit: cover, object-position: center |
| 内联样式 | 所有样式必须内联，禁止使用class |
| 禁止hover | 不添加任何hover效果 |
| 防盗链 | 必须包含 meta referrer 标签 |

---

## 输出文件命名

生成HTML报告时，文件名格式：
```
爆款封面分析报告_{关键词}.html
```

保存路径：当前工作目录（使用相对路径 ./）
