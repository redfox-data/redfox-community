#!/usr/bin/env python3
"""
小红书账号涨粉榜数据查询脚本
通过API接口获取榜单数据（使用原生socket + SSL，不发送SNI）
"""

import argparse
import json
import os
import re
import sys
import socket
import ssl
from urllib.parse import urlparse
from typing import List, Dict, Optional
from datetime import datetime, timedelta


class HTTPSClient:
    """原生HTTPS客户端（不发送SNI）"""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def post(self, url: str, json_body: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
        """
        发送POST请求（JSON body，不发送SNI）

        Args:
            url: 请求URL
            json_body: JSON请求体
            headers: 请求头

        Returns:
            解析后的JSON响应
        """
        payload = json.dumps(json_body or {}, ensure_ascii=False).encode('utf-8')

        parsed = urlparse(url)
        host = parsed.hostname
        port = parsed.port or 443
        path = parsed.path or '/'

        # 创建socket连接
        sock = socket.create_connection((host, port), timeout=self.timeout)

        # 包装SSL上下文（不发送SNI）
        # 注意：这是数据源接口的要求，必须使用此方式才能正常访问
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        # 不传递server_hostname，这样就不会发送SNI（数据源接口要求）
        ssock = context.wrap_socket(sock, server_hostname=None)

        try:
            # 构建HTTP请求
            default_headers = {
                'Host': host,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.0 Edg/120.0.0.0',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Content-Type': 'application/json',
                'Content-Length': str(len(payload)),
                'Connection': 'close'
            }

            if headers:
                default_headers.update(headers)

            header_lines = '\r\n'.join([f"{k}: {v}" for k, v in default_headers.items()])
            request = f"POST {path} HTTP/1.1\r\n{header_lines}\r\n\r\n"

            # 发送请求
            ssock.send(request.encode('utf-8') + payload)

            # 接收响应
            response = b''
            while True:
                chunk = ssock.recv(4096)
                if not chunk:
                    break
                response += chunk

            # 解析响应
            return self._parse_response(response)

        finally:
            ssock.close()

    def _parse_response(self, response: bytes) -> Dict:
        """解析HTTP响应"""
        # 分离头部和主体
        header_end = response.find(b'\r\n\r\n')
        if header_end == -1:
            raise ValueError("Invalid HTTP response")

        headers = response[:header_end].decode('utf-8', errors='ignore')
        body = response[header_end + 4:]

        # 检查是否分块传输
        if 'Transfer-Encoding: chunked' in headers:
            body = self._decode_chunked(body)

        # 尝试解析JSON
        try:
            return json.loads(body.decode('utf-8'))
        except json.JSONDecodeError:
            return {'raw': body.decode('utf-8', errors='ignore')}

    def _decode_chunked(self, data: bytes) -> bytes:
        """解码分块传输编码"""
        result = b''
        while data:
            line_end = data.find(b'\r\n')
            if line_end == -1:
                break

            chunk_size_hex = data[:line_end].decode('ascii').split(';')[0].strip()
            chunk_size = int(chunk_size_hex, 16)

            if chunk_size == 0:
                break

            chunk_start = line_end + 2
            chunk_end = chunk_start + chunk_size
            result += data[chunk_start:chunk_end]

            data = data[chunk_end + 2:]

        return result


class RankingAPIClient:
    """涨粉榜API客户端"""

    # 官方鉴权接口（POST，需 API Key，按次计费）
    API_URL = "https://redfox.hk/story/api/xhsData/query"

    # 调用来源标识（随请求上报，供数据源统计渠道来源）
    SOURCE = "小红书达人涨粉榜查询-GitHub"

    # 日期类型映射
    DATE_TYPE_MAP = {
        'daily': 1,      # 日榜
        'weekly': 2,     # 周榜
        'monthly': 3     # 月榜
    }

    # 支持的类目列表（25个固定类目）
    VALID_CATEGORIES = [
        '综合全部',
        '出行代步',
        '医疗保健',
        '休闲爱好',
        '综合杂项',
        '婚庆婚礼',
        '居家装修',
        '影视娱乐',
        '星座情感',
        '拍摄记录',
        '学习教育',
        '旅行度假',
        '亲子育儿',
        '日常生活',
        '科学探索',
        '数码科技',
        '时尚穿搭',
        '化妆美容',
        '个人护理',
        '美味佳肴',
        '职业发展',
        '宠物天地',
        '新闻资讯',
        '体育锻炼',
        '潮流鞋包'
    ]

    # 单个类目数据上限
    MAX_LIMIT = 100

    # 数据查询范围限制
    QUERY_RANGE_LIMITS = {
        'daily': 30,      # 日榜最多查前30天
        'weekly': 8,      # 周榜最多查前8周
        'monthly': 3      # 月榜最多查前3个月
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化API客户端

        Args:
            api_key: redfox.hk 平台 API Key，未传时依次尝试环境变量与 shell 配置文件
        """
        self.http_client = HTTPSClient()
        # API Key 优先级：显式传参 > 环境变量 REDFOX_API_KEY > shell 配置文件
        self.api_key = (
            api_key
            or os.environ.get('REDFOX_API_KEY')
            or self._load_api_key_from_shell_configs()
        )

    def _load_api_key_from_shell_configs(self) -> Optional[str]:
        """
        从 shell 配置文件中读取 REDFOX_API_KEY（环境变量未设置时的兜底）

        扫描常见 shell 配置文件，支持以下写法：
        - bash/zsh: export REDFOX_API_KEY=ak_xxx / REDFOX_API_KEY=ak_xxx
        - PowerShell: $env:REDFOX_API_KEY = "ak_xxx"
        """
        home = os.path.expanduser('~')
        candidates = [
            os.path.join(home, '.zshrc'),               # macOS/Linux zsh
            os.path.join(home, '.bashrc'),              # bash / Git Bash
            os.path.join(home, '.bash_profile'),        # macOS bash 登录 shell
            os.path.join(home, '.profile'),             # 通用登录 shell
            # Windows PowerShell 用户配置文件
            os.path.join(home, 'Documents', 'WindowsPowerShell', 'Microsoft.PowerShell_profile.ps1'),
            os.path.join(home, 'Documents', 'PowerShell', 'Microsoft.PowerShell_profile.ps1'),
        ]
        # bash/zsh：export 可选；PowerShell：$env: 写法（引号可选）
        patterns = [
            re.compile(r'^\s*(?:export\s+)?REDFOX_API_KEY\s*=\s*["\']?([\w\-\.]+)', re.M),
            re.compile(r'^\s*\$env:REDFOX_API_KEY\s*=\s*["\']?([\w\-\.]+)', re.M),
        ]
        for path in candidates:
            try:
                if not os.path.isfile(path):
                    continue
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                for pat in patterns:
                    m = pat.search(content)
                    if m:
                        return m.group(1).strip()
            except OSError:
                continue
        return None

    def validate_category(self, category: Optional[str]) -> tuple[bool, str]:
        """
        校验类目是否有效

        Args:
            category: 类目名称

        Returns:
            (是否有效, 错误信息)
        """
        if category is None:
            return True, ""

        if category not in self.VALID_CATEGORIES:
            valid_list = "、".join(self.VALID_CATEGORIES)
            return False, f"无效的类目'{category}'。仅支持以下25个类目：{valid_list}"

        return True, ""

    def validate_limit(self, limit: int) -> int:
        """
        校验并限制返回条数

        Args:
            limit: 请求的条数

        Returns:
            限制后的条数（最大100）
        """
        if limit > self.MAX_LIMIT:
            print(f"⚠️  请求条数{limit}超过上限{self.MAX_LIMIT}，已自动调整为{self.MAX_LIMIT}", file=sys.stderr)
            return self.MAX_LIMIT
        return limit

    def query_rankings(
        self,
        category: Optional[str] = None,
        stat_type: str = 'daily',
        stat_date: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict]:
        """
        查询涨粉排行榜

        Args:
            category: 账号类型（如：化妆美容、穿搭、美食等），默认"综合全部"
            stat_type: 统计类型（daily/weekly/monthly）
            stat_date: 统计日期（YYYY-MM-DD），None表示昨天
            limit: 返回条数（最大100）

        Returns:
            排名数据列表
        """
        # 默认使用"综合全部"
        if category is None:
            category = '综合全部'

        # 校验类目
        is_valid, error_msg = self.validate_category(category)
        if not is_valid:
            print(f"❌ {error_msg}", file=sys.stderr)
            return []

        # 校验并限制条数
        limit = self.validate_limit(limit)

        # 统计日期：未指定时默认前天（数据有1天延迟：4月20日可获取4月18日数据）
        if not stat_date:
            stat_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')

        # 无 Key：给出配置指引后直接返回（API Key 为查询的必要条件）
        if not self.api_key:
            print("⚠️  未检测到 API Key：环境变量 REDFOX_API_KEY 未设置，shell 配置文件"
                  "（~/.zshrc / ~/.bashrc / PowerShell profile 等）中也未找到，无法查询。\n"
                  "请配置后重试：export REDFOX_API_KEY=<你的apikey>\n"
                  "  - macOS/Linux：将 export REDFOX_API_KEY=<值> 追加到 ~/.zshrc（zsh）或 ~/.bashrc（bash），"
                  "然后 source 对应文件使其全局生效\n"
                  "  - Windows：执行 [Environment]::SetEnvironmentVariable('REDFOX_API_KEY', '<值>', 'User') "
                  "设置用户级永久环境变量（需重启终端生效）\n"
                  "  - API Key 可在 redfox.hk 注册后于个人中心获取（新注册用户赠送免费积分），格式 ak_xxxxxxxx\n"
                  "  - 也可通过 --api-key 参数临时传入；配置后可用 echo $REDFOX_API_KEY / echo %REDFOX_API_KEY% 验证", file=sys.stderr)
            return []

        try:
            # 官方鉴权接口（POST /story/api/xhsData/query）
            body = {
                'dateType': self.DATE_TYPE_MAP.get(stat_type, 1),
                'rankDate': stat_date,
                'type': category,
                'source': self.SOURCE
            }
            # 鉴权请求头：X-API-KEY 为主；同时发送官方文档示例的 REDFOX_API_KEY 头，双发兼容
            headers = {
                'X-API-KEY': self.api_key,
                'REDFOX_API_KEY': self.api_key
            }
            data = self.http_client.post(self.API_URL, json_body=body, headers=headers)

            if data.get('code') == 2000 and 'data' in data:
                return self._parse_v2_response(data, limit)
            else:
                print(f"API Error: {data.get('msg', 'Unknown error')}", file=sys.stderr)
                return []

        except Exception as e:
            print(f"Request failed: {e}", file=sys.stderr)
            return []

    def _parse_v2_response(self, data: Dict, limit: int) -> List[Dict]:
        """
        解析官方鉴权接口返回数据

        实际返回字段：
        - accountRanking: 排名
        - accountName: 账号名称
        - accountLink: 账号主页链接
        - category: 类目
        - fansCount: 粉丝数（如 "375.00w"）
        - fansGrowth: 涨粉数（如 "1.11w"）
        - likedGrowth: 点赞增长
        - commentsGrowth: 评论增长
        - collectedGrowth: 收藏增长
        - sharedGrowth: 分享增长
        - newNoteCount: 新增笔记数
        - avatar: 头像URL
        - rankDate: 统计日期
        - rankPeriod: 排名周期（日/周/月）
        """
        rankings = []
        items = data.get('data', [])

        if not items or not isinstance(items, list):
            return rankings

        period_map = {'日': 'daily', '周': 'weekly', '月': 'monthly'}
        for item in items[:limit]:
            if not isinstance(item, dict):
                continue

            followers = self._parse_w_number(item.get('fansCount'))
            growth = self._parse_w_number(item.get('fansGrowth'))
            # 官方接口无涨粉率字段，按 涨粉数/(粉丝数-涨粉数) 计算
            base = followers - growth
            rate = round(growth / base * 100, 4) if base > 0 else 0.0

            ranking = {
                'ranking': item.get('accountRanking', 0),
                'account_id': item.get('accountLink') or '',
                'account_name': item.get('accountName') or 'Unknown',
                'category': item.get('category') or '',
                'followers_count': followers,
                'growth_count': growth,
                'growth_rate': rate,
                'avatar_url': item.get('avatar') or '',
                'stat_date': item.get('rankDate') or '',
                'stat_type': period_map.get(item.get('rankPeriod') or '', 'daily'),
                'account_link': item.get('accountLink') or '',
                'new_note_count': self._parse_number(item.get('newNoteCount')),
                'liked_growth': self._parse_w_number(item.get('likedGrowth')),
                'comments_growth': self._parse_w_number(item.get('commentsGrowth')),
                'collected_growth': self._parse_w_number(item.get('collectedGrowth')),
                'shared_growth': self._parse_w_number(item.get('sharedGrowth')),
            }
            rankings.append(ranking)

        return rankings

    def _parse_number(self, value) -> int:
        """解析数字"""
        if value is None:
            return 0
        try:
            return int(float(str(value).replace(',', '')))
        except (ValueError, TypeError):
            return 0

    def _parse_w_number(self, value) -> int:
        """解析带 w/万 后缀的数字（如 "375.00w" -> 3750000）"""
        if value is None:
            return 0
        try:
            s = str(value).strip().replace(',', '')
            if s.endswith('w') or s.endswith('万'):
                return int(float(s[:-1]) * 10000)
            return int(float(s))
        except (ValueError, TypeError):
            return 0

    def get_categories(self) -> List[str]:
        """获取支持的账号类型列表"""
        default_categories = [
            '综合全部',
            '出行代步',
            '医疗保健',
            '休闲爱好',
            '综合杂项',
            '婚庆婚礼',
            '居家装修',
            '影视娱乐',
            '星座情感',
            '拍摄记录',
            '学习教育',
            '旅行度假',
            '亲子育儿',
            '日常生活',
            '科学探索',
            '数码科技',
            '时尚穿搭',
            '化妆美容',
            '个人护理',
            '美味佳肴',
            '职业发展',
            '宠物天地',
            '新闻资讯',
            '体育锻炼',
            '潮流鞋包'
        ]
        return default_categories

    def get_available_dates(self, stat_type: str = 'daily', days: int = 30) -> List[str]:
        """获取可用的统计日期列表"""
        dates = []
        today = datetime.now()

        for i in range(days):
            date = today - timedelta(days=i+1)
            dates.append(date.strftime('%Y-%m-%d'))

        return dates


def main():
    parser = argparse.ArgumentParser(description='小红书涨粉榜数据查询（API方式，无SNI）')
    parser.add_argument('--category', type=str, help='账号类型（如：化妆美容、穿搭、美食）')
    parser.add_argument('--type', type=str, default='daily',
                       choices=['daily', 'weekly', 'monthly'],
                       help='统计类型')
    parser.add_argument('--date', type=str, help='统计日期(YYYY-MM-DD)，默认昨天')
    parser.add_argument('--limit', type=int, default=20, help='返回条数')
    parser.add_argument('--output', type=str, help='输出文件路径')
    parser.add_argument('--action', type=str, default='rankings',
                       choices=['rankings', 'categories', 'dates'],
                       help='操作类型')
    parser.add_argument('--api-key', type=str,
                       help='redfox.hk 平台 API Key（优先级：本参数 > 环境变量 REDFOX_API_KEY > shell 配置文件）')

    args = parser.parse_args()

    client = RankingAPIClient(api_key=args.api_key)

    if args.action == 'rankings':
        results = client.query_rankings(
            category=args.category,
            stat_type=args.type,
            stat_date=args.date,
            limit=args.limit
        )
    elif args.action == 'categories':
        results = client.get_categories()
    elif args.action == 'dates':
        results = client.get_available_dates(stat_type=args.type)
    else:
        results = []

    output = json.dumps(results, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Results saved to {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()
