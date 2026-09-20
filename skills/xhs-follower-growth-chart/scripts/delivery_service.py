#!/usr/bin/env python3
"""
小红书涨粉榜报告推送服务
支持邮件、微信等多种推送方式
"""

import argparse
import json
import sys
from typing import List, Dict, Optional
from datetime import datetime


class DeliveryService:
    """报告推送服务"""
    
    def __init__(self, config: Dict):
        """
        初始化推送服务
        
        Args:
            config: 推送配置
                - email: 邮件配置 (smtp_server, smtp_port, username, password, from_name)
                - wechat: 微信配置 (appid, appsecret, template_id)
        """
        self.config = config
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        content: str,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """
        发送邮件报告
        
        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            content: 邮件内容（HTML格式）
            attachments: 附件路径列表
            
        Returns:
            是否发送成功
        """
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            from email.mime.base import MIMEBase
            from email import encoders
            
            email_config = self.config.get('email', {})
            
            msg = MIMEMultipart()
            msg['From'] = f"{email_config.get('from_name', '小红书榜单')} <{email_config.get('username')}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # 添加HTML内容
            msg.attach(MIMEText(content, 'html', 'utf-8'))
            
            # 添加附件
            if attachments:
                for filepath in attachments:
                    try:
                        with open(filepath, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                        encoders.encode_base64(part)
                        filename = filepath.split('/')[-1]
                        part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                        msg.attach(part)
                    except Exception as e:
                        print(f"Failed to attach {filepath}: {e}")
            
            # 发送邮件
            server = smtplib.SMTP(email_config.get('smtp_server'), email_config.get('smtp_port', 587))
            server.starttls()
            server.login(email_config.get('username'), email_config.get('password'))
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"Email sending failed: {e}")
            return False
    
    def send_wechat_template(
        self,
        openid: str,
        template_id: str,
        data: Dict,
        url: Optional[str] = None
    ) -> bool:
        """
        发送微信模板消息
        
        Args:
            openid: 用户OpenID
            template_id: 模板ID
            data: 模板数据
            url: 跳转链接
            
        Returns:
            是否发送成功
        """
        try:
            import requests
            
            wechat_config = self.config.get('wechat', {})
            
            # 获取access_token
            token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={wechat_config.get('appid')}&secret={wechat_config.get('appsecret')}"
            token_resp = requests.get(token_url).json()
            access_token = token_resp.get('access_token')
            
            if not access_token:
                print(f"Failed to get access_token: {token_resp}")
                return False
            
            # 发送模板消息
            msg_url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"
            payload = {
                "touser": openid,
                "template_id": template_id,
                "data": data
            }
            if url:
                payload["url"] = url
            
            resp = requests.post(msg_url, json=payload).json()
            
            if resp.get('errcode') == 0:
                return True
            else:
                print(f"WeChat API error: {resp}")
                return False
                
        except Exception as e:
            print(f"WeChat sending failed: {e}")
            return False
    
    def generate_email_content(
        self,
        rankings: List[Dict],
        category: str,
        stat_type: str,
        stat_date: str,
        chart_path: Optional[str] = None
    ) -> str:
        """
        生成邮件HTML内容
        
        Args:
            rankings: 排名数据
            category: 账号类型
            stat_type: 统计类型
            stat_date: 统计日期
            chart_path: 图表路径
            
        Returns:
            HTML内容
        """
        type_names = {'daily': '日榜', 'weekly': '周榜', 'monthly': '月榜'}
        type_name = type_names.get(stat_type, stat_type)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
                .header {{ background: #FF2442; color: white; padding: 30px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .header p {{ margin: 10px 0 0; opacity: 0.9; }}
                .content {{ padding: 30px; }}
                .chart {{ text-align: center; margin: 20px 0; }}
                .chart img {{ max-width: 100%; border-radius: 4px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th {{ background: #f8f8f8; padding: 12px; text-align: left; font-weight: 600; color: #333; border-bottom: 2px solid #e0e0e0; }}
                td {{ padding: 12px; border-bottom: 1px solid #e0e0e0; }}
                tr:hover {{ background: #f8f8f8; }}
                .rank {{ font-weight: bold; color: #FF2442; }}
                .growth {{ color: #52c41a; }}
                .footer {{ background: #f8f8f8; padding: 20px; text-align: center; color: #999; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>小红书{category}涨粉{type_name}</h1>
                    <p>统计时间：{stat_date}</p>
                </div>
                <div class="content">
        """
        
        # 添加图表
        if chart_path:
            # 在实际使用时需要将图片转为base64或上传到CDN
            html += f'<div class="chart"><p>📊 排行榜图表</p></div>'
        
        # 添加数据表格
        html += """
                    <table>
                        <thead>
                            <tr>
                                <th>排名</th>
                                <th>账号名称</th>
                                <th>粉丝数</th>
                                <th>涨粉数</th>
                                <th>涨粉率</th>
                            </tr>
                        </thead>
                        <tbody>
        """
        
        for item in rankings[:20]:  # 显示前20
            rank = item.get('ranking', '-')
            name = item.get('account_name', 'Unknown')
            followers = self._format_number(item.get('followers_count', 0))
            growth = self._format_number(item.get('growth_count', 0))
            rate = f"{item.get('growth_rate', 0):.2f}%"
            
            html += f"""
                            <tr>
                                <td class="rank">#{rank}</td>
                                <td>{name}</td>
                                <td>{followers}</td>
                                <td class="growth">+{growth}</td>
                                <td>{rate}</td>
                            </tr>
            """
        
        html += f"""
                        </tbody>
                    </table>
                </div>
                <div class="footer">
                    <p>小红书涨粉榜订阅服务</p>
                    <p>此邮件由系统自动发送，如需取消订阅请联系客服</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def generate_wechat_data(
        self,
        rankings: List[Dict],
        category: str,
        stat_type: str,
        stat_date: str
    ) -> Dict:
        """
        生成微信模板消息数据
        
        Args:
            rankings: 排名数据
            category: 账号类型
            stat_type: 统计类型
            stat_date: 统计日期
            
        Returns:
            模板数据
        """
        type_names = {'daily': '日榜', 'weekly': '周榜', 'monthly': '月榜'}
        type_name = type_names.get(stat_type, stat_type)
        
        # 取前3名
        top3 = rankings[:3]
        top3_text = " | ".join([f"#{i+1} {r.get('account_name', 'Unknown')}" 
                                for i, r in enumerate(top3)])
        
        return {
            "first": {
                "value": f"📊 小红书{category}涨粉{type_name}已更新",
                "color": "#FF2442"
            },
            "keyword1": {
                "value": stat_date,
                "color": "#333333"
            },
            "keyword2": {
                "value": type_name,
                "color": "#333333"
            },
            "keyword3": {
                "value": top3_text,
                "color": "#52c41a"
            },
            "remark": {
                "value": "点击查看完整榜单，了解行业动态！",
                "color": "#666666"
            }
        }
    
    def _format_number(self, num: int) -> str:
        """格式化数字"""
        if num >= 10000:
            return f'{num/10000:.1f}万'
        return str(num)


def main():
    parser = argparse.ArgumentParser(description='小红书涨粉榜报告推送')
    parser.add_argument('--config', type=str, required=True, help='推送配置文件路径')
    parser.add_argument('--action', type=str, required=True,
                       choices=['email', 'wechat', 'generate-email', 'generate-wechat'])
    parser.add_argument('--to', type=str, help='收件人邮箱/OpenID')
    parser.add_argument('--data', type=str, help='排名数据文件(JSON)')
    parser.add_argument('--category', type=str, help='账号类型')
    parser.add_argument('--type', type=str, default='daily', choices=['daily', 'weekly', 'monthly'])
    parser.add_argument('--date', type=str, help='统计日期')
    parser.add_argument('--chart', type=str, help='图表路径')
    parser.add_argument('--output', type=str, help='输出文件路径')
    
    args = parser.parse_args()
    
    # 加载配置
    with open(args.config, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    service = DeliveryService(config)
    
    # 加载排名数据
    rankings = []
    if args.data:
        with open(args.data, 'r', encoding='utf-8') as f:
            rankings = json.load(f)
    
    stat_date = args.date or datetime.now().strftime('%Y-%m-%d')
    
    if args.action == 'generate-email':
        content = service.generate_email_content(
            rankings=rankings,
            category=args.category or '全部',
            stat_type=args.type,
            stat_date=stat_date,
            chart_path=args.chart
        )
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Email content saved to {args.output}")
        else:
            print(content)
    
    elif args.action == 'generate-wechat':
        data = service.generate_wechat_data(
            rankings=rankings,
            category=args.category or '全部',
            stat_type=args.type,
            stat_date=stat_date
        )
        output = json.dumps(data, ensure_ascii=False, indent=2)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"WeChat data saved to {args.output}")
        else:
            print(output)
    
    elif args.action == 'email':
        if not args.to:
            print("Error: --to is required for email action")
            sys.exit(1)
        
        content = service.generate_email_content(
            rankings=rankings,
            category=args.category or '全部',
            stat_type=args.type,
            stat_date=stat_date,
            chart_path=args.chart
        )
        
        subject = f"小红书{args.category or '全部'}涨粉榜 - {stat_date}"
        success = service.send_email(
            to_email=args.to,
            subject=subject,
            content=content,
            attachments=[args.chart] if args.chart else None
        )
        print(json.dumps({"success": success}))
    
    elif args.action == 'wechat':
        if not args.to:
            print("Error: --to is required for wechat action")
            sys.exit(1)
        
        data = service.generate_wechat_data(
            rankings=rankings,
            category=args.category or '全部',
            stat_type=args.type,
            stat_date=stat_date
        )
        
        wechat_config = config.get('wechat', {})
        template_id = wechat_config.get('template_id')
        
        success = service.send_wechat_template(
            openid=args.to,
            template_id=template_id,
            data=data
        )
        print(json.dumps({"success": success}))


if __name__ == '__main__':
    main()
