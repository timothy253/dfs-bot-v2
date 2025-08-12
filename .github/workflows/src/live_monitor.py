# Live game monitoring for swap opportunities
import requests
from datetime import datetime
import json

class LiveMonitor:
    def __init__(self):
        self.alerts = []
        self.your_lineup = {
            "Kelsey Plum": "LVA",
            "Sabrina Ionescu": "NYL", 
            "Breanna Stewart": "NYL",
            "A'ja Wilson": "LVA",
            "Napheesa Collier": "MIN",
            "Alyssa Thomas": "CONN"
        }
        
    def check_games(self):
        """Main monitoring function"""
        print("🔄 Checking live games...")
        
        # Get live scores
        games = self.get_live_scores()
        
        if not games:
            print("⚠️ No live game data available")
            return []
        
        # Analyze each game
        for game in games:
            self.analyze_game(game)
        
        return self.alerts
    
    def get_live_scores(self):
        """Fetch live WNBA scores"""
        try:
            url = "http://site.api.espn.com/apis/site/v2/sports/basketball/wnba/scoreboard"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self.parse_espn_data(data)
            else:
                print(f"❌ ESPN API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching scores: {e}")
            return []
    
    def parse_espn_data(self, data):
        """Parse ESPN scoreboard data"""
        games = []
        
        for event in data.get('events', []):
            try:
                competitors = event['competitions'][0]['competitors']
                
                game_info = {
                    'home_team': competitors[0]['team']['abbreviation'],
                    'away_team': competitors[1]['team']['abbreviation'], 
                    'home_score': int(competitors[0].get('score', 0)),
                    'away_score': int(competitors[1].get('score', 0)),
                    'status': event['status']['type']['name'],
                    'period': event['status'].get('period', 1),
                    'clock': event['status'].get('displayClock', ''),
                    'game_id': event['id']
                }
                
                games.append(game_info)
                
            except Exception as e:
                print(f"⚠️ Error parsing game: {e}")
                continue
        
        return games
    
    def analyze_game(self, game):
        """Analyze game for swap opportunities"""
        score_diff = abs(game['home_score'] - game['away_score'])
        total_score = game['home_score'] + game['away_score']
        
        # Check for blowouts
        if score_diff >= 15 and game['period'] >= 3:
            self.check_blowout_impact(game, score_diff)
        
        # Check pace/total
        if game['period'] >= 2:
            projected_total = (total_score / game['period']) * 4
            self.check_pace_impact(game, projected_total)
        
        # Check your players' teams
        self.check_player_teams(game)
    
    def check_blowout_impact(self, game, score_diff):
        """Check if blowout affects your players"""
        if game['home_score'] > game['away_score']:
            losing_team = game['away_team']
            winning_team = game['home_team']
        else:
            losing_team = game['home_team']
            winning_team = game['away_team']
        
        # Check if your players are affected
        affected_players = []
        for player, team in self.your_lineup.items():
            team_abbrev = self.map_team_name(team)
            if team_abbrev == losing_team:
                affected_players.append(player)
        
        if affected_players:
            alert = f"🚨 BLOWOUT ALERT: {game['away_team']} @ {game['home_team']} "
            alert += f"({game['away_score']}-{game['home_score']}) "
            alert += f"Your players at risk: {', '.join(affected_players)}"
            self.alerts.append(alert)
    
    def check_pace_impact(self, game, projected_total):
        """Check game pace impact"""
        if projected_total < 160:
            alert = f"⚠️ LOW TOTAL: {game['away_team']} @ {game['home_team']} "
            alert += f"projecting {projected_total:.0f} total - Consider pivoting"
            self.alerts.append(alert)
        
        elif projected_total > 180:
            alert = f"🔥 HIGH TOTAL: {game['away_team']} @ {game['home_team']} "
            alert += f"projecting {projected_total:.0f} total - Great for stacks!"
            self.alerts.append(alert)
    
    def check_player_teams(self, game):
        """Check if game involves your players' teams"""
        your_teams = set(self.map_team_name(team) for team in self.your_lineup.values())
        game_teams = {game['home_team'], game['away_team']}
        
        if your_teams.intersection(game_teams):
            print(f"📊 Monitoring: {game['away_team']} @ {game['home_team']} (your players involved)")
    
    def map_team_name(self, team_code):
        """Map team codes to ESPN abbreviations"""
        mapping = {
            'LVA': 'LV',    # Las Vegas Aces
            'NYL': 'NY',    # New York Liberty  
            'MIN': 'MIN',   # Minnesota Lynx
            'CONN': 'CONN', # Connecticut Sun
            'DAL': 'DAL',   # Dallas Wings
            'WSH': 'WAS'    # Washington Mystics
        }
        return mapping.get(team_code, team_code)
    
    def get_swap_recommendations(self):
        """Generate specific swap recommendations"""
        recommendations = []
        
        for alert in self.alerts:
            if "BLOWOUT" in alert:
                recommendations.append({
                    'type': 'BLOWOUT_SWAP',
                    'action': 'Consider swapping players from losing team',
                    'urgency': 'HIGH'
                })
            elif "LOW TOTAL" in alert:
                recommendations.append({
                    'type': 'PACE_PIVOT', 
                    'action': 'Pivot from game stack to individual plays',
                    'urgency': 'MEDIUM'
                })
        
        return recommendations
