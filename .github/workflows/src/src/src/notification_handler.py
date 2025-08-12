# Notification system for DFS alerts and updates
import os
import requests
from datetime import datetime
import json

class NotificationHandler:
    def __init__(self):
        self.telegram_token = os.environ.get('TELEGRAM_TOKEN')
        self.telegram_chat_id = os.environ.get('TELEGRAM_CHAT_ID')
        self.notification_methods = []
        
        # Determine available notification methods
        if self.telegram_token and self.telegram_chat_id:
            self.notification_methods.append('telegram')
        
        self.notification_methods.append('console')  # Always available
        
        print(f"📱 Notification methods: {', '.join(self.notification_methods)}")
    
    def send_alerts(self, alerts):
        """Send alerts through all configured methods"""
        if not alerts:
            print("✅ No alerts to send")
            return
        
        # Format the alert message
        message = self.format_alert_message(alerts)
        
        # Send through each method
        for method in self.notification_methods:
            try:
                if method == 'telegram':
                    self.send_telegram_message(message)
                elif method == 'console':
                    self.print_to_console(message)
            except Exception as e:
                print(f"❌ Failed to send via {method}: {e}")
    
    def format_alert_message(self, alerts):
        """Format alerts into a readable message"""
        timestamp = datetime.now().strftime('%I:%M %p ET')
        
        # Create header
        message = f"🚨 DFS ALERT SYSTEM\n"
        message += f"📅 {datetime.now().strftime('%B %d, %Y')}\n"
        message += f"🕐 {timestamp}\n"
        message += "=" * 30 + "\n\n"
        
        # Add alerts
        for i, alert in enumerate(alerts, 1):
            priority = self.get_alert_priority(alert)
            emoji = self.get_priority_emoji(priority)
            
            message += f"{emoji} ALERT #{i}\n"
            message += f"   {alert}\n\n"
        
        # Add footer
        message += f"📊 Total alerts: {len(alerts)}\n"
        message += "💡 Check lineup for potential swaps\n"
        
        return message
    
    def get_alert_priority(self, alert):
        """Determine alert priority based on content"""
        alert_lower = alert.lower()
        
        if any(keyword in alert_lower for keyword in ['blowout', 'foul trouble', 'injury']):
            return 'HIGH'
        elif any(keyword in alert_lower for keyword in ['low total', 'high total', 'pace']):
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def get_priority_emoji(self, priority):
        """Get emoji for alert priority"""
        emoji_map = {
            'HIGH': '🔥',
            'MEDIUM': '⚠️',
            'LOW': '💡'
        }
        return emoji_map.get(priority, '📢')
    
    def send_telegram_message(self, message):
        """Send message via Telegram bot"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            
            # Format message for Telegram
            telegram_message = self.format_for_telegram(message)
            
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': telegram_message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, data=payload, timeout=10)
            
            if response.status_code == 200:
                print("✅ Telegram alert sent successfully")
            else:
                print(f"❌ Telegram API error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Telegram error: {e}")
    
    def format_for_telegram(self, message):
        """Format message for Telegram HTML parsing"""
        # Replace markdown-style formatting with HTML
        formatted = message.replace('**', '<b>').replace('**', '</b>')
        formatted = formatted.replace('*', '<i>').replace('*', '</i>')
        
        return formatted
    
    def print_to_console(self, message):
        """Print alert to console/logs"""
        print("\n" + "="*50)
        print(message)
        print("="*50)
    
    def send_lineup_summary(self, lineups):
        """Send lineup summary notification"""
        if not lineups:
            return
        
        message = self.format_lineup_summary(lineups)
        
        # Send summary
        for method in self.notification_methods:
            try:
                if method == 'telegram':
                    self.send_telegram_message(message)
                elif method == 'console':
                    self.print_to_console(message)
            except Exception as e:
                print(f"❌ Failed to send lineup summary via {method}: {e}")
    
    def format_lineup_summary(self, lineups):
        """Format lineup summary message"""
        timestamp = datetime.now().strftime('%I:%M %p ET')
        
        message = f"📋 LINEUP SUMMARY\n"
        message += f"🕐 Generated at {timestamp}\n"
        message += "=" * 25 + "\n\n"
        
        for lineup in lineups:
            message += f"🎯 {lineup['strategy']} Strategy\n"
            message += f"   💰 Salary: ${lineup['salary']:,}/50,000\n"
            message += f"   📊 Projection: {lineup['projection']:.1f} points\n"
            message += f"   👥 Avg Ownership: {lineup['ownership']:.1f}%\n"
            
            # Top 3 players
            top_players = sorted(lineup['players'], key=lambda x: x['salary'], reverse=True)[:3]
            message += f"   🌟 Key Players: {', '.join(p['name'] for p in top_players)}\n\n"
        
        message += f"📈 Ready for contest entry!\n"
        message += f"🎯 Target contests: GPP + Double Up\n"
        
        return message
    
    def send_swap_recommendation(self, player_out, player_in, reason):
        """Send specific swap recommendation"""
        message = f"🔄 SWAP RECOMMENDATION\n"
        message += f"🕐 {datetime.now().strftime('%I:%M %p ET')}\n\n"
        message += f"❌ SWAP OUT: {player_out}\n"
        message += f"✅ SWAP IN: {player_in}\n"
        message += f"💡 REASON: {reason}\n\n"
        message += f"⏰ Execute swap before game locks!"
        
        # Send with high priority formatting
        for method in self.notification_methods:
            try:
                if method == 'telegram':
                    # Add urgent formatting for Telegram
                    urgent_message = f"🚨 <b>URGENT SWAP ALERT</b> 🚨\n\n{message}"
                    self.send_telegram_message(urgent_message)
                elif method == 'console':
                    print(f"\n🚨 URGENT: {message}")
            except Exception as e:
                print(f"❌ Failed to send swap alert via {method}: {e}")
    
    def send_game_update(self, game_info):
        """Send live game update"""
        message = f"📊 GAME UPDATE\n"
        message += f"{game_info['away_team']} @ {game_info['home_team']}\n"
        message += f"Score: {game_info['away_score']}-{game_info['home_score']}\n"
        message += f"Status: {game_info['status']}\n"
        
        if game_info.get('period'):
            message += f"Period: Q{game_info['period']}\n"
        
        # Only send if significant (blowout, close game, etc.)
        score_diff = abs(game_info['home_score'] - game_info['away_score'])
        
        if score_diff >= 15:
            message += f"\n🚨 BLOWOUT ALERT: {score_diff} point lead!"
            
            for method in self.notification_methods:
                try:
                    if method == 'telegram':
                        self.send_telegram_message(message)
                    elif method == 'console':
                        print(f"\n{message}")
                except Exception as e:
                    print(f"❌ Failed to send game update via {method}: {e}")
    
    def test_notifications(self):
        """Test all notification methods"""
        test_message = f"🧪 DFS Bot Test Message\n"
        test_message += f"🕐 {datetime.now().strftime('%I:%M %p ET')}\n"
        test_message += f"✅ Notification system working!\n"
        test_message += f"📱 Methods: {', '.join(self.notification_methods)}"
        
        print("🧪 Testing notification methods...")
        
        for method in self.notification_methods:
            try:
                if method == 'telegram':
                    self.send_telegram_message(test_message)
                    print(f"  ✅ Telegram test sent")
                elif method == 'console':
                    print(f"  ✅ Console test: {test_message}")
            except Exception as e:
                print(f"  ❌ {method} test failed: {e}")
        
        return len(self.notification_methods) > 0
    
    def send_daily_summary(self, total_alerts, lineup_count, monitor_duration):
        """Send end-of-day summary"""
        message = f"📈 DAILY DFS SUMMARY\n"
        message += f"📅 {datetime.now().strftime('%B %d, %Y')}\n"
        message += "=" * 25 + "\n\n"
        message += f"🚨 Total Alerts: {total_alerts}\n"
        message += f"📋 Lineups Generated: {lineup_count}\n"
        message += f"⏰ Monitor Duration: {monitor_duration}\n\n"
        message += f"🎯 Bot performance: {'🟢 Active' if total_alerts > 0 else '🟡 Quiet day'}\n"
        message += f"💡 Ready for tomorrow's slate!"
        
        for method in self.notification_methods:
            try:
                if method == 'telegram':
                    self.send_telegram_message(message)
                elif method == 'console':
                    self.print_to_console(message)
            except Exception as e:
                print(f"❌ Failed to send daily summary via {method}: {e}")
