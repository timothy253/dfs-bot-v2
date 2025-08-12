# DFS Bot Main Entry Point
from src.lineup_optimizer import LineupOptimizer
from src.live_monitor import LiveMonitor
from src.notification_handler import NotificationHandler
from src.data_collector import DataCollector
import os
from datetime import datetime

class DFSBot:
    def __init__(self):
        print("🤖 DFS Bot initializing...")
        self.optimizer = LineupOptimizer()
        self.monitor = LiveMonitor()
        self.notifier = NotificationHandler()
        self.data_collector = DataCollector()
        
    def run(self):
        """Main bot execution"""
        print(f"🔄 DFS Bot running at {datetime.now().strftime('%I:%M %p ET')}")
        
        try:
            # Collect today's games
            games = self.data_collector.get_today_games()
            print(f"📊 Found {len(games)} games today")
            
            # Generate optimal lineups
            lineups = self.optimizer.generate_lineups(count=4)
            print(f"🎯 Generated {len(lineups)} lineups")
            
            # Monitor live games for alerts
            alerts = self.monitor.check_games()
            
            # Send notifications if alerts exist
            if alerts:
                print(f"🚨 {len(alerts)} alerts found")
                self.notifier.send_alerts(alerts)
            else:
                print("✅ No alerts - lineup looking good")
            
            # Print lineup summary
            self.print_lineup_summary(lineups)
            
        except Exception as e:
            error_msg = f"❌ Bot error: {str(e)}"
            print(error_msg)
            self.notifier.send_alerts([error_msg])
    
    def print_lineup_summary(self, lineups):
        """Print lineup summary to console"""
        print("\n" + "="*50)
        print("📋 LINEUP SUMMARY")
        print("="*50)
        
        for lineup in lineups:
            print(f"\n🎯 {lineup['strategy']} Lineup:")
            print(f"   Salary: ${lineup['salary']:,}")
            print(f"   Projection: {lineup['projection']:.1f}")
            print(f"   Players: {len(lineup['players'])}")

if __name__ == "__main__":
    print("🚀 Starting DFS Automation Bot")
    print("="*50)
    
    bot = DFSBot()
    bot.run()
    
    print("="*50)
    print("✅ Bot execution complete")
