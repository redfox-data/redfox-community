#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
optimize-skill-md/scripts/record.py

SKILL.md 优化记录上报脚本
用途：每次使用 optimize-skill-md 技能时调用一次记录接口

记录接口：https://redfox.hk/story/api/skill/record/save
网络实现：使用 requests 库，开启 SSL 证书验证
鉴权方式：从环境变量 REDFOX_API_KEY 读取，通过 X-API-Key 请求头传入
固定参数：SKILL.md优化

用法：
  python record.py
"""

import sys
import os

try:
    import requests
except ImportError:
    print("❌ 缺少依赖：requests")
    print("请执行：pip install requests")
    sys.exit(1)

RECORD_URL = 'https://redfox.hk/story/api/skill/record/save'
SKILL_NAME = 'SKILL.md优化'


def _get_api_key() -> str:
    """从环境变量读取 REDFOX_API_KEY，缺失时提示并退出。"""
    key = os.getenv('REDFOX_API_KEY', '').strip()
    if not key:
        print('❌ 未配置 REDFOX_API_KEY 环境变量')
        print('请执行以下命令配置：')
        print('  export REDFOX_API_KEY="ak_xxxx..."')
        print('获取地址：https://redfox.hk/settings/api-keys?source=github')
        sys.exit(1)
    return key


def save_record():
    """调用记录接口，上报一次技能使用记录。"""
    api_key = _get_api_key()
    payload = {'skillName': SKILL_NAME}
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'X-API-Key': api_key,
    }
    try:
        resp = requests.post(
            RECORD_URL,
            json=payload,
            headers=headers,
            verify=True,   # 开启 SSL 证书验证
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get('code') == 200:
                print('✅ 记录上报成功')
            else:
                print(f'⚠️ 接口返回异常：{data}')
        else:
            print(f'⚠️ HTTP {resp.status_code}：{resp.text}')
    except requests.exceptions.RequestException as e:
        print(f'⚠️ 记录上报失败（不影响主流程）：{e}')


if __name__ == '__main__':
    save_record()
