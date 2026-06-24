#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证 searchUser 接口效果
=========================
测试 gzhData/searchUser 接口在A股大V发现场景的实际效果

Usage:
    python3 verify_search_user.py
    python3 verify_search_user.py --keyword "A股"
    python3 verify_search_user.py --count 50
"""

import json
import os
import sys
import time
from pathlib import Path
import urllib.request
import urllib.error


# ─── 配置 ─────────────────────────────────────────────────────────────────────────
SEARCH_USER_URL = "https://redfox.hk/story/api/gzhData/searchUser"
ACCOUNT_QUERY_URL = "https://redfox.hk/story/api/gzhUser/query"
CONFIG_DIR = Path.home() / ".qoder" / "apis"
CONFIG_FILE = CONFIG_DIR / "redfox.json"
ENV_KEY = "REDFOX_API_KEY"
SOURCE = "A股公众号大V-验证脚本"

# 测试关键词
TEST_KEYWORDS = ["A股", "股票", "股市", "券商", "基金投资"]


# ─── API Key 管理 ──────────────────────────────────────────────────────────────────
def get_api_key():
    """Get API key: env var > config file."""
    env_key = os.environ.get(ENV_KEY)
    if env_key:
        return env_key
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text())
            key = data.get("api_key")
            if key:
                return key
        except (json.JSONDecodeError, OSError):
            pass
    return None


# ─── HTTP 请求 ─────────────────────────────────────────────────────────────────────
def _http_post(url, body, api_key):
    """发送POST请求，返回解析后的JSON dict"""
    try:
        data_bytes = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": api_key,
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        return {"__http_error__": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"__error__": str(e)}


# ─── Step 1: searchUser 搜索账号 ──────────────────────────────────────────────────
def test_search_user(api_key, keywords, max_per_keyword=20):
    """测试 searchUser 接口，直接搜索A股相关账号
    
    Returns:
        list: 账号列表
    """
    all_accounts = []
    seen_names = set()
    
    print(f"\n{'='*80}")
    print(f"📡 Step 1: 测试 searchUser 接口")
    print(f"{'='*80}\n")
    
    for keyword in keywords:
        print(f"🔍 搜索关键词: {keyword}")
        
        body = {
            "keyword": keyword,
            "offset": 0,
            "sortType": "_4",  # 最热排序（按阅读数）
        }
        
        result = _http_post(SEARCH_USER_URL, body, api_key)
        
        if "__http_error__" in result:
            print(f"  ❌ HTTP错误: {result['__http_error__']}")
            continue
        if "__error__" in result:
            print(f"  ❌ 请求异常: {result['__error__']}")
            continue
        if result.get("code") != 2000:
            print(f"  ❌ 接口返回失败: code={result.get('code')}, msg={result.get('msg')}")
            continue
        
        data = result.get("data", {})
        total = data.get("total", 0)
        accounts = data.get("list", [])
        
        print(f"  ✅ 成功 | 总数: {total} | 返回: {len(accounts)} 个账号")
        
        # 分析返回的账号
        new_count = 0
        for acc in accounts:
            name = acc.get("accountName", "").strip()
            if not name or name in seen_names:
                continue
            
            seen_names.add(name)
            new_count += 1
            
            # 提取关键字段
            account_info = {
                "accountName": name,
                "account": acc.get("account", ""),  # 微信号
                "redfoxIndex": acc.get("redfoxIndex", 0),
                "description": acc.get("description", ""),
                "verifyInfo": acc.get("verifyInfo", ""),
                "accountType": acc.get("accountType", ""),
                "lastArticleTitle": acc.get("lastArticleTitle", ""),
                "lastPublishTime": acc.get("lastPublishTime", ""),
                "tags": acc.get("tags", ""),
            }
            all_accounts.append(account_info)
        
        print(f"  📊 新增去重账号: {new_count} 个")
        
        # 打印前3个账号详情
        for i, acc in enumerate(accounts[:3]):
            print(f"\n  示例账号 {i+1}:")
            print(f"    名称: {acc.get('accountName')}")
            print(f"    微信号: {acc.get('account')}")
            print(f"    红狐指数: {acc.get('redfoxIndex')}")
            print(f"    账号分类: {acc.get('accountType')}")
            print(f"    认证信息: {acc.get('verifyInfo')}")
            print(f"    最新文章: {acc.get('lastArticleTitle')}")
            desc = acc.get('description') or ""
            print(f"    简介: {desc[:50]}..." if len(desc) > 50 else f"    简介: {desc}")
        
        print()
        time.sleep(0.5)  # 限流
    
    return all_accounts


# ─── Step 2: gzhUser/query 批量查询验证 ───────────────────────────────────────────
def test_gzh_user_query(api_key, accounts, test_count=5):
    """测试 gzhUser/query 接口，验证是否能用 searchUser 返回的 account 字段查询
    
    Args:
        accounts: searchUser 返回的账号列表
        test_count: 测试前N个账号
    """
    print(f"\n{'='*80}")
    print(f"📡 Step 2: 测试 gzhUser/query 批量查询")
    print(f"{'='*80}\n")
    
    if not accounts:
        print("❌ 无账号可测试")
        return
    
    # 取前 test_count 个账号测试
    test_accounts = accounts[:test_count]
    
    print(f"🔍 测试前 {len(test_accounts)} 个账号的详情查询...\n")
    
    for i, acc in enumerate(test_accounts):
        account_name = acc.get("accountName")
        account_wei = acc.get("account")  # 微信号
        
        print(f"[{i+1}] 测试账号: {account_name}")
        print(f"    微信号: {account_wei}")
        
        # 方式1: 用 accountName 查询
        body1 = {
            "accountNames": [account_name],
            "source": SOURCE,
        }
        
        result1 = _http_post(ACCOUNT_QUERY_URL, body1, api_key)
        
        if result1.get("code") == 2000:
            data1 = result1.get("data", {})
            if isinstance(data1, list) and len(data1) > 0:
                detail = data1[0]
                print(f"    ✅ 方式1(accountName) 成功")
                print(f"       avgReadCount: {detail.get('avgReadCount', 'N/A')}")
                print(f"       redfoxIndex: {detail.get('redfoxIndex', 'N/A')}")
                
                # 检查 works 字段
                works = detail.get("works", [])
                if works:
                    latest_work = works[0]
                    print(f"       最新文章: {latest_work.get('title', 'N/A')}")
                    print(f"       workUrl: {'✅ 有' if latest_work.get('workUrl') else '❌ 空'}")
                    print(f"       readCount: {latest_work.get('readCount', 'N/A')}")
                else:
                    print(f"       works: ❌ 无作品数据")
            else:
                print(f"    ⚠️ 方式1(accountName) 返回空数据")
        else:
            print(f"    ❌ 方式1(accountName) 失败: code={result1.get('code')}")
        
        time.sleep(0.3)
        
        # 方式2: 用 account(微信号) 查询
        if account_wei:
            body2 = {
                "accountNames": [account_wei],
                "source": SOURCE,
            }
            
            result2 = _http_post(ACCOUNT_QUERY_URL, body2, api_key)
            
            if result2.get("code") == 2000:
                data2 = result2.get("data", {})
                if isinstance(data2, list) and len(data2) > 0:
                    detail2 = data2[0]
                    print(f"    ✅ 方式2(微信号) 成功")
                    print(f"       avgReadCount: {detail2.get('avgReadCount', 'N/A')}")
                    print(f"       redfoxIndex: {detail2.get('redfoxIndex', 'N/A')}")
                else:
                    print(f"    ⚠️ 方式2(微信号) 返回空数据")
            else:
                print(f"    ❌ 方式2(微信号) 失败: code={result2.get('code')}")
        else:
            print(f"    ⏭️ 方式2(微信号) 跳过（无微信号）")
        
        print()
        time.sleep(0.3)


# ─── Step 3: 垂直度分类验证 ──────────────────────────────────────────────────────
def analyze_vertical_classification(accounts):
    """分析 searchUser 返回账号的垂直度和分类情况"""
    print(f"\n{'='*80}")
    print(f"📊 Step 3: 垂直度与分类分析")
    print(f"{'='*80}\n")
    
    if not accounts:
        print("❌ 无账号可分析")
        return
    
    # A股垂直度关键词
    vertical_keywords = [
        "证券", "股票", "A股", "炒股", "股市", "牛熊", "复盘", "涨跌",
        "基金", "投资", "理财", "金融", "期货",
        "财经", "财联社", "经济报道", "经济新闻",
        "投研", "策略", "研报", "宏观",
    ]
    
    # 官媒关键词
    official_keywords = [
        "报社", "报业", "日报", "晚报", "传媒", "媒体", "新闻", "通讯社",
        "时事新闻", "政府",
    ]
    
    vertical_count = 0
    official_count = 0
    kol_count = 0
    no_description = 0
    
    print(f"📈 账号垂直度分析（共 {len(accounts)} 个）:\n")
    
    for acc in accounts:
        name = acc.get("accountName", "")
        desc = (acc.get("description") or "").lower()
        verify = (acc.get("verifyInfo") or "").lower()
        acc_type = (acc.get("accountType") or "").lower()
        
        # 判断是否A股垂直
        is_vertical = any(kw in desc for kw in vertical_keywords)
        
        # 判断是否官媒
        is_official = any(kw in verify or kw in acc_type or kw in desc for kw in official_keywords)
        
        if is_vertical:
            vertical_count += 1
        
        if is_official:
            official_count += 1
        else:
            kol_count += 1
        
        if not desc:
            no_description += 1
    
    print(f"  A股垂直账号: {vertical_count}/{len(accounts)} ({vertical_count/len(accounts)*100:.1f}%)")
    print(f"  官媒/机构: {official_count}/{len(accounts)} ({official_count/len(accounts)*100:.1f}%)")
    print(f"  个人大V: {kol_count}/{len(accounts)} ({kol_count/len(accounts)*100:.1f}%)")
    print(f"  无简介: {no_description}/{len(accounts)} ({no_description/len(accounts)*100:.1f}%)")
    
    # 打印示例
    print(f"\n  官媒示例:")
    official_accounts = [acc for acc in accounts if any(kw in (acc.get("verifyInfo") or "").lower() or kw in (acc.get("accountType") or "").lower() for kw in official_keywords)]
    for acc in official_accounts[:3]:
        print(f"    - {acc['accountName']} | {acc.get('accountType')} | {(acc.get('verifyInfo') or '')[:30]}")
    
    print(f"\n  个人大V示例:")
    kol_accounts = [acc for acc in accounts if not any(kw in (acc.get("verifyInfo") or "").lower() or kw in (acc.get("accountType") or "").lower() for kw in official_keywords)]
    for acc in kol_accounts[:3]:
        desc = acc.get('description') or ""
        print(f"    - {acc['accountName']} | 红狐指数: {acc.get('redfoxIndex')} | {desc[:30]}")


# ─── 主函数 ──────────────────────────────────────────────────────────────────────
def main():
    api_key = get_api_key()
    if not api_key:
        print("❌ 未找到API Key，请设置环境变量 REDFOX_API_KEY 或配置文件")
        sys.exit(1)
    
    print("🚀 开始验证 searchUser 接口效果")
    print(f"⏰ 测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: 测试 searchUser
    accounts = test_search_user(api_key, TEST_KEYWORDS)
    
    print(f"\n✅ searchUser 测试完成:")
    print(f"   发现账号总数: {len(accounts)}")
    
    redfox_indices = [float(a['redfoxIndex']) for a in accounts if a.get('redfoxIndex') is not None]
    if redfox_indices:
        print(f"   红狐指数范围: {min(redfox_indices):.1f} - {max(redfox_indices):.1f}")
    
    # 保存原始数据
    output_file = Path("search_user_test_result.json")
    output_file.write_text(json.dumps(accounts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"   原始数据已保存至: {output_file}")
    
    # Step 2: 测试 gzhUser/query
    test_gzh_user_query(api_key, accounts, test_count=5)
    
    # Step 3: 垂直度分析
    analyze_vertical_classification(accounts)
    
    # 总结
    print(f"\n{'='*80}")
    print(f"📋 验证总结")
    print(f"{'='*80}\n")
    
    print("✅ searchUser 接口能力:")
    print("   1. 直接返回账号列表（含红狐指数、简介、分类）")
    print("   2. 支持最热排序（按阅读数）")
    print("   3. 返回 accountType 辅助分类")
    print("   4. 返回 lastArticleTitle（最新文章标题）")
    
    print("\n⚠️ 需要注意:")
    print("   1. 无时间范围过滤参数（可能搜到历史账号）")
    print("   2. 需配合 gzhUser/query 获取 avgReadCount 和 works")
    print("   3. 返回的 account 是微信号，需验证是否可用于 gzhUser/query")
    
    print("\n🎯 建议:")
    if len(accounts) >= 50:
        print(f"   ✅ 数据充足（{len(accounts)}个账号），可考虑替代 hotArticle 方案")
    else:
        print(f"   ⚠️ 数据较少（{len(accounts)}个账号），建议保留 hotArticle 作为补充")
    
    print()


if __name__ == "__main__":
    main()
