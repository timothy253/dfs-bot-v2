# Data collection module for DFS information
import requests
from datetime import datetime, timedelta
import json

class DataCollector:
    def __init__(self):
        self.data_sources = {
            'espn_wnba': 'http://site.api.espn.com/apis/site/v2/sports/basketball/wnba/scoreboard',
            'wnba_official': 'https://www.wnba.com/games',
            'backup_source': 'https://www.espn.com/wnba/scoreboard'
        }
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; DFS-Bot/1.0)'
        }
    
    def get_today_games(self):
        """Get today's WNBA games with details"""
        print("📊 Fetching today's WNBA games...")
        
        try:
            # Try ESPN API first
            games = self.fetch_espn_games()
            
            if games:
                print(f"✅ Found {len(games)} games from ESPN")
                return games
            else:
                print("⚠️ ESPN API failed, trying backup...")
                return self.get_fallback_games()
                
        except Exception as e:
            print(f"❌ Error fetching games: {e}")
            return self.get_fallback_games()
    
    def fetch_espn_games(self):
        """Fetch games from ESPN API"""
        try:
            response = requests.get(
                self.data_sources['espn_wnba'], 
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            games = []
            
            for event in data.get('events', []):
                try:
                    competition = event['competitions'][0]
                    competitors = competition['competitors']
                    
                    # Extract team info
                    home_team = competitors[0]
                    away_team = competitors[1]
                    
                    game_info = {
                        'id': event['id'],
                        'home_team': home_team['team']['displayName'],
                        'away_team': away_team['team']['displayName'],
                        'home_abbrev': home_team['team']['abbreviation'],
                        'away_abbrev': away_team['team']['abbreviation'],
                        'start_time': event['date'],
                        'status': event['status']['type']['name'],
                        'venue': competition.get('venue', {}).get('fullName', 'Unknown'),
                        'tv_broadcast': self.extract_broadcast_info(competition),
                        'odds': self.extract_odds(competition)
                    }
                    
                    # Add live scores if game is in progress
                    if event['status']['type']['name'] in ['STATUS_IN_PROGRESS', 'STATUS_HALFTIME']:
                        game_info.update({
                            'home_score': int(home_team.get('score', 0)),
                            'away_score': int(away_team.get('score', 0)),
                            'period': event['status'].get('period', 1),
                            'clock': event['status'].get('displayClock', ''),
                            'is_live': True
                        })
                    else:
                        game_info['is_live'] = False
                    
                    games.append(game_info)
                    
                except Exception as e:
                    print(f"⚠️ Error parsing game: {e}")
                    continue
            
            return games
            
        except Exception as e:
            print(f"❌ ESPN API error: {e}")
            return None
    
    def extract_broadcast_info(self, competition):
        """Extract TV broadcast information"""
        try:
            broadcasts = competition.get('broadcasts', [])
            if broadcasts:
                return broadcasts[0].get('names', ['Unknown'])[0]
            return 'Not Available'
        except:
            return 'Unknown'
    
    def extract_odds(self, competition):
        """Extract betting odds if available"""
        try:
            odds = competition.get('odds', [])
            if odds:
                return {
                    'spread': odds[0].get('details', 'N/A'),
                    'total': odds[0].get('overUnder', 'N/A')
                }
            return {'spread': 'N/A', 'total': 'N/A'}
        except:
            return {'spread': 'N/A', 'total': 'N/A'}
    
    def get_fallback_games(self):
        """Fallback game data when APIs fail"""
        print("📋 Using fallback game data...")
        
        # Static game data for today (August 11, 2025)
        fallback_games = [
            {
                'id': 'nyl_min_20250811',
                'home_team': 'New York Liberty',
                'away_team': 'Minnesota Lynx',
                'home_abbrev': 'NYL',
                'away_abbrev': 'MIN',
                'start_time': '2025-08-11T16:30:00Z',
                'status': 'STATUS_SCHEDULED',
                'venue': 'Barclays Center',
                'tv_broadcast': 'ABC',
                'is_live': False,
                'projected_total': 168.5
            },
            {
                'id': 'wsh_dal_20250811',
                'home_team': 'Dallas Wings',
                'away_team': 'Washington Mystics',
                'home_abbrev': 'DAL',
                'away_abbrev': 'WSH',
                'start_time': '2025-08-11T20:00:00Z',
                'status': 'STATUS_SCHEDULED',
                'venue': 'College Park Center',
                'tv_broadcast': 'CBS Sports Network',
                'is_live': False,
                'projected_total': 162.5
            },
            {
                'id': 'atl_phx_20250811',
                'home_team': 'Phoenix Mercury',
                'away_team': 'Atlanta Dream',
                'home_abbrev': 'PHX',
                'away_abbrev': 'ATL',
                'start_time': '2025-08-11T22:00:00Z',
                'status': 'STATUS_SCHEDULED',
                'venue': 'Footprint Center',
                'tv_broadcast': 'NBA TV',
                'is_live': False,
                'projected_total': 159.0
            },
            {
                'id': 'sea_las_20250812',
                'home_team': 'Los Angeles Sparks',
                'away_team': 'Seattle Storm',
                'home_abbrev': 'LAS',
                'away_abbrev': 'SEA',
                'start_time': '2025-08-12
      'start_time': '2025-08-12T00:00:00Z',
                'status': 'STATUS_SCHEDULED',
                'venue': 'Crypto.com Arena',
                'tv_broadcast': 'Local',
                'is_live': False,
                'projected_total': 165.0
            },
            {
                'id': 'conn_lva_20250812',
                'home_team': 'Las Vegas Aces',
                'away_team': 'Connecticut Sun',
                'home_abbrev': 'LVA',
                'away_abbrev': 'CONN',
                'start_time': '2025-08-12T01:00:00Z',
                'status': 'STATUS_SCHEDULED',
                'venue': 'Michelob ULTRA Arena',
                'tv_broadcast': 'NBA TV',
                'is_live': False,
                'projected_total': 175.5
            }
        ]
        
        return fallback_games
    
    def get_injury_news(self):
        """Collect injury and news updates"""
        print("🏥 Checking injury reports...")
        
        try:
            # In a real implementation, this would scrape injury reports
            # For now, return common injury scenarios
            injuries = [
                {
                    'player': 'Example Player',
                    'team': 'TEAM',
                    'status': 'QUESTIONABLE',
                    'injury': 'Ankle',
                    'last_updated': datetime.now().isoformat()
                }
            ]
            
            return injuries
            
        except Exception as e:
            print(f"❌ Error fetching injuries: {e}")
            return []
    
    def get_weather_data(self, city=None):
        """Get weather data (not applicable for indoor WNBA)"""
        # WNBA games are indoors, so weather doesn't affect play
        return {
            'status': 'Indoor sport - weather not applicable',
            'dome': True
        }
    
    def get_pace_data(self, games):
        """Calculate pace data for games"""
        print("⚡ Calculating game pace projections...")
        
        pace_data = {}
        
        for game in games:
            # Estimate pace based on teams and venue
            estimated_pace = self.estimate_game_pace(
                game['home_abbrev'], 
                game['away_abbrev']
            )
            
            pace_data[game['id']] = {
                'estimated_possessions': estimated_pace,
                'projected_total': game.get('projected_total', 165),
                'pace_rating': 'Fast' if estimated_pace > 80 else 'Average' if estimated_pace > 75 else 'Slow'
            }
        
        return pace_data
    
    def estimate_game_pace(self, home_team, away_team):
        """Estimate game pace based on team tendencies"""
        # Team pace ratings (possessions per game)
        team_pace = {
            'LVA': 82,  # Vegas - Fast
            'NYL': 79,  # Liberty - Above average
            'CONN': 77, # Sun - Average
            'MIN': 76,  # Lynx - Average
            'DAL': 80,  # Wings - Fast
            'WSH': 75,  # Mystics - Slow
            'PHX': 78,  # Mercury - Average
            'ATL': 79,  # Dream - Above average
            'SEA': 76,  # Storm - Average
            'LAS': 77   # Sparks - Average
        }
        
        home_pace = team_pace.get(home_team, 77)
        away_pace = team_pace.get(away_team, 77)
        
        # Average the two teams' pace
        return (home_pace + away_pace) / 2
    
    def validate_data_quality(self, data):
        """Validate the quality of collected data"""
        if not data:
            return False
        
        required_fields = ['home_team', 'away_team', 'start_time']
        
        for item in data:
            if not all(field in item for field in required_fields):
                print(f"⚠️ Data quality issue: Missing fields in {item}")
                return False
        
        return True
    
    def get_live_updates(self):
        """Get live game updates"""
        print("🔴 Fetching live updates...")
        
        try:
            games = self.fetch_espn_games()
            live_games = [g for g in games if g.get('is_live', False)]
            
            if live_games:
                print(f"📺 {len(live_games)} live games found")
                return live_games
            else:
                print("📊 No live games currently")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching live updates: {e}")
            return []
    
    def get_historical_data(self, days_back=7):
        """Get historical game data for analysis"""
        print(f"📈 Fetching {days_back} days of historical data...")
        
        # This would typically query a database or API
        # For now, return mock historical data
        historical_games = []
        
        for i in range(days_back):
            date = datetime.now() - timedelta(days=i+1)
            historical_games.append({
                'date': date.isoformat(),
                'games_played': 3,
                'average_total': 168.5,
                'blowout_rate': 0.15
            })
        
        return historical_games
    
    def export_data(self, data, filename=None):
        """Export collected data to file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            filename = f'dfs_data_{timestamp}.json'
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            print(f"💾 Data exported to {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return None
    
    def get_data_summary(self, data):
        """Generate summary of collected data"""
        if not data:
            return "No data available"
        
        summary = {
            'total_games': len(data),
            'live_games': len([g for g in data if g.get('is_live', False)]),
            'upcoming_games': len([g for g in data if not g.get('is_live', False)]),
            'data_quality': 'Good' if self.validate_data_quality(data) else 'Poor',
            'last_updated': datetime.now().strftime('%I:%M %p ET')
        }
        
        return summary
