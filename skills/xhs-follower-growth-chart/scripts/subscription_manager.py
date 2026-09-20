#!/usr/bin/env python3
"""
小红书涨粉榜订阅管理脚本
支持订阅创建、查询、更新、取消等功能
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from enum import Enum


class SubscriptionTier(Enum):
    """订阅等级"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"


class SubscriptionFrequency(Enum):
    """订阅频率"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class SubscriptionManager:
    """订阅管理器"""
    
    # 订阅等级配置
    TIER_CONFIG = {
        SubscriptionTier.FREE: {
            "max_categories": 1,
            "frequencies": [SubscriptionFrequency.WEEKLY],
            "chart_types": ["bar"],
            "price": 0,
            "name": "免费版"
        },
        SubscriptionTier.BASIC: {
            "max_categories": 3,
            "frequencies": [SubscriptionFrequency.DAILY, SubscriptionFrequency.WEEKLY],
            "chart_types": ["bar", "trend", "comparison"],
            "price": 29,
            "name": "基础版"
        },
        SubscriptionTier.PREMIUM: {
            "max_categories": 999,  # 无限制
            "frequencies": [SubscriptionFrequency.DAILY, SubscriptionFrequency.WEEKLY, SubscriptionFrequency.MONTHLY],
            "chart_types": ["bar", "trend", "comparison", "custom"],
            "price": 99,
            "name": "高级版"
        }
    }
    
    def __init__(self, storage_path: str = "subscriptions.json"):
        """
        初始化订阅管理器
        
        Args:
            storage_path: 订阅数据存储路径
        """
        self.storage_path = storage_path
        self.subscriptions = self._load_subscriptions()
    
    def _load_subscriptions(self) -> Dict:
        """加载订阅数据"""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"subscriptions": [], "users": {}}
    
    def _save_subscriptions(self):
        """保存订阅数据"""
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.subscriptions, f, ensure_ascii=False, indent=2)
    
    def create_subscription(
        self,
        user_id: str,
        categories: List[str],
        frequency: str,
        tier: str = "free",
        email: Optional[str] = None,
        wechat_id: Optional[str] = None
    ) -> Dict:
        """
        创建新订阅
        
        Args:
            user_id: 用户唯一标识
            categories: 订阅的账号类型列表
            frequency: 订阅频率 (daily/weekly/monthly)
            tier: 订阅等级 (free/basic/premium)
            email: 邮箱地址
            wechat_id: 微信ID
            
        Returns:
            订阅信息字典
        """
        tier_enum = SubscriptionTier(tier)
        freq_enum = SubscriptionFrequency(frequency)
        config = self.TIER_CONFIG[tier_enum]
        
        # 验证权限
        if len(categories) > config["max_categories"]:
            raise ValueError(f"等级 {tier} 最多订阅 {config['max_categories']} 个类型")
        
        if freq_enum not in config["frequencies"]:
            raise ValueError(f"等级 {tier} 不支持 {frequency} 频率")
        
        subscription = {
            "id": self._generate_id(),
            "user_id": user_id,
            "categories": categories,
            "frequency": frequency,
            "tier": tier,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "last_sent_at": None,
            "next_send_at": self._calculate_next_send(frequency),
            "email": email,
            "wechat_id": wechat_id,
            "send_count": 0
        }
        
        self.subscriptions["subscriptions"].append(subscription)
        
        # 更新用户信息
        if user_id not in self.subscriptions["users"]:
            self.subscriptions["users"][user_id] = {
                "created_at": datetime.now().isoformat(),
                "subscriptions": []
            }
        self.subscriptions["users"][user_id]["subscriptions"].append(subscription["id"])
        
        self._save_subscriptions()
        return subscription
    
    def update_subscription(
        self,
        subscription_id: str,
        categories: Optional[List[str]] = None,
        frequency: Optional[str] = None,
        tier: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict:
        """
        更新订阅
        
        Args:
            subscription_id: 订阅ID
            categories: 新的账号类型列表
            frequency: 新的频率
            tier: 新的等级
            status: 新的状态
            
        Returns:
            更新后的订阅信息
        """
        sub = self._get_subscription(subscription_id)
        if not sub:
            raise ValueError(f"订阅 {subscription_id} 不存在")
        
        # 检查等级权限
        check_tier = SubscriptionTier(tier) if tier else SubscriptionTier(sub["tier"])
        check_cats = categories if categories else sub["categories"]
        check_freq = SubscriptionFrequency(frequency) if frequency else SubscriptionFrequency(sub["frequency"])
        
        config = self.TIER_CONFIG[check_tier]
        
        if len(check_cats) > config["max_categories"]:
            raise ValueError(f"等级 {check_tier.value} 最多订阅 {config['max_categories']} 个类型")
        
        if check_freq not in config["frequencies"]:
            raise ValueError(f"等级 {check_tier.value} 不支持 {frequency} 频率")
        
        # 更新字段
        if categories:
            sub["categories"] = categories
        if frequency:
            sub["frequency"] = frequency
            sub["next_send_at"] = self._calculate_next_send(frequency)
        if tier:
            sub["tier"] = tier
        if status:
            sub["status"] = status
        
        sub["updated_at"] = datetime.now().isoformat()
        self._save_subscriptions()
        return sub
    
    def cancel_subscription(self, subscription_id: str) -> bool:
        """
        取消订阅
        
        Args:
            subscription_id: 订阅ID
            
        Returns:
            是否成功
        """
        sub = self._get_subscription(subscription_id)
        if not sub:
            return False
        
        sub["status"] = "cancelled"
        sub["cancelled_at"] = datetime.now().isoformat()
        self._save_subscriptions()
        return True
    
    def get_user_subscriptions(self, user_id: str) -> List[Dict]:
        """
        获取用户的所有订阅
        
        Args:
            user_id: 用户ID
            
        Returns:
            订阅列表
        """
        return [s for s in self.subscriptions["subscriptions"] 
                if s["user_id"] == user_id and s["status"] == "active"]
    
    def get_due_subscriptions(self) -> List[Dict]:
        """
        获取到期的订阅（需要发送报告）
        
        Returns:
            到期订阅列表
        """
        now = datetime.now()
        due = []
        
        for sub in self.subscriptions["subscriptions"]:
            if sub["status"] != "active":
                continue
            
            next_send = datetime.fromisoformat(sub["next_send_at"])
            if next_send <= now:
                due.append(sub)
        
        return due
    
    def mark_sent(self, subscription_id: str):
        """
        标记订阅已发送
        
        Args:
            subscription_id: 订阅ID
        """
        sub = self._get_subscription(subscription_id)
        if sub:
            sub["last_sent_at"] = datetime.now().isoformat()
            sub["next_send_at"] = self._calculate_next_send(sub["frequency"])
            sub["send_count"] = sub.get("send_count", 0) + 1
            self._save_subscriptions()
    
    def get_tier_info(self, tier: Optional[str] = None) -> Dict:
        """
        获取订阅等级信息
        
        Args:
            tier: 等级名称，None返回所有
            
        Returns:
            等级配置信息
        """
        if tier:
            t = SubscriptionTier(tier)
            return {
                "tier": t.value,
                **self.TIER_CONFIG[t]
            }
        
        return {
            t.value: {"tier": t.value, **config}
            for t, config in self.TIER_CONFIG.items()
        }
    
    def _get_subscription(self, subscription_id: str) -> Optional[Dict]:
        """根据ID获取订阅"""
        for sub in self.subscriptions["subscriptions"]:
            if sub["id"] == subscription_id:
                return sub
        return None
    
    def _generate_id(self) -> str:
        """生成唯一ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _calculate_next_send(self, frequency: str) -> str:
        """计算下次发送时间"""
        now = datetime.now()
        
        if frequency == "daily":
            next_send = now + timedelta(days=1)
            next_send = next_send.replace(hour=9, minute=0, second=0)
        elif frequency == "weekly":
            days_until_monday = (7 - now.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 7
            next_send = now + timedelta(days=days_until_monday)
            next_send = next_send.replace(hour=9, minute=0, second=0)
        elif frequency == "monthly":
            if now.month == 12:
                next_send = now.replace(year=now.year + 1, month=1, day=1, hour=9, minute=0, second=0)
            else:
                next_send = now.replace(month=now.month + 1, day=1, hour=9, minute=0, second=0)
        else:
            next_send = now + timedelta(days=1)
        
        return next_send.isoformat()


def main():
    parser = argparse.ArgumentParser(description='小红书涨粉榜订阅管理')
    parser.add_argument('--storage', type=str, default='subscriptions.json',
                       help='订阅数据存储路径')
    
    subparsers = parser.add_subparsers(dest='action', help='操作类型')
    
    # 创建订阅
    create_parser = subparsers.add_parser('create', help='创建订阅')
    create_parser.add_argument('--user-id', type=str, required=True)
    create_parser.add_argument('--categories', type=str, required=True,
                              help='账号类型，逗号分隔')
    create_parser.add_argument('--frequency', type=str, required=True,
                              choices=['daily', 'weekly', 'monthly'])
    create_parser.add_argument('--tier', type=str, default='free',
                              choices=['free', 'basic', 'premium'])
    create_parser.add_argument('--email', type=str)
    create_parser.add_argument('--wechat-id', type=str)
    
    # 更新订阅
    update_parser = subparsers.add_parser('update', help='更新订阅')
    update_parser.add_argument('--id', type=str, required=True)
    update_parser.add_argument('--categories', type=str)
    update_parser.add_argument('--frequency', type=str)
    update_parser.add_argument('--tier', type=str)
    update_parser.add_argument('--status', type=str)
    
    # 取消订阅
    cancel_parser = subparsers.add_parser('cancel', help='取消订阅')
    cancel_parser.add_argument('--id', type=str, required=True)
    
    # 查询订阅
    list_parser = subparsers.add_parser('list', help='列出订阅')
    list_parser.add_argument('--user-id', type=str)
    list_parser.add_argument('--due', action='store_true', help='只显示到期的订阅')
    
    # 等级信息
    tier_parser = subparsers.add_parser('tiers', help='查看订阅等级信息')
    tier_parser.add_argument('--tier', type=str)
    
    # 标记已发送
    sent_parser = subparsers.add_parser('mark-sent', help='标记已发送')
    sent_parser.add_argument('--id', type=str, required=True)
    
    args = parser.parse_args()
    
    if not args.action:
        parser.print_help()
        sys.exit(1)
    
    manager = SubscriptionManager(storage_path=args.storage)
    
    if args.action == 'create':
        categories = [c.strip() for c in args.categories.split(',')]
        result = manager.create_subscription(
            user_id=args.user_id,
            categories=categories,
            frequency=args.frequency,
            tier=args.tier,
            email=args.email,
            wechat_id=args.wechat_id
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.action == 'update':
        categories = [c.strip() for c in args.categories.split(',')] if args.categories else None
        result = manager.update_subscription(
            subscription_id=args.id,
            categories=categories,
            frequency=args.frequency,
            tier=args.tier,
            status=args.status
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.action == 'cancel':
        success = manager.cancel_subscription(args.id)
        print(json.dumps({"success": success}))
    
    elif args.action == 'list':
        if args.due:
            results = manager.get_due_subscriptions()
        elif args.user_id:
            results = manager.get_user_subscriptions(args.user_id)
        else:
            results = manager.subscriptions["subscriptions"]
        print(json.dumps(results, ensure_ascii=False, indent=2))
    
    elif args.action == 'tiers':
        result = manager.get_tier_info(args.tier)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.action == 'mark-sent':
        manager.mark_sent(args.id)
        print(json.dumps({"success": True}))


if __name__ == '__main__':
    main()
