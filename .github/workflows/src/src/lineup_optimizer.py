# DFS Lineup Optimization Engine
import json
from itertools import combinations
import random

class LineupOptimizer:
    def __init__(self):
        self.salary_cap = 50000
        self.player_pool = self.load_player_pool()
        
    def load_player_pool(self):
        """Load current WNBA player pool with projections"""
        return {
            "guards": [
                {"name": "A'ja Wilson", "position": "F", "salary": 11800, "projection": 52.5, "team": "LVA", "ownership": 35, "game": "vs CONN"},
                {"name": "Breanna Stewart", "position": "F", "salary": 10500, "projection": 45.8, "team": "NYL", "ownership": 32, "game": "vs MIN"},
                {"name": "Sabrina Ionescu", "position": "G", "salary": 9200, "projection": 38.2, "team": "NYL", "ownership": 28, "game": "vs MIN"},
                {"name": "Napheesa Collier", "position": "F", "salary": 8800, "projection": 41.3, "team": "MIN", "ownership": 22, "game": "@ NYL"},
                {"name": "Kelsey Plum", "position": "G", "salary": 7800, "projection": 32.8, "team": "LVA", "ownership": 18, "game": "vs CONN"},
                {"name": "Alyssa Thomas", "position": "F", "salary": 7200, "projection": 35.4, "team": "CONN", "ownership": 15, "game": "@ LVA"},
                {"name": "Paige Bueckers", "position": "G", "salary": 7200, "projection": 35.7, "team": "DAL", "ownership": 20, "game": "vs WSH"},
                {"name": "DeWanna Bonner", "position": "F", "salary": 6900, "projection": 32.1, "team": "CONN", "ownership": 12, "game": "@ LVA"},
                {"name": "Jackie Young", "position": "G", "salary": 6800, "projection": 29.5, "team": "LVA", "ownership": 14, "game": "vs CONN"},
                {"name": "Kayla McBride", "position": "G", "salary": 5400, "projection": 26.8, "team": "MIN", "ownership": 10, "game": "@ NYL"},
                {"name": "Courtney Williams", "position": "G", "salary": 3900, "projection": 24.2, "team": "MIN", "ownership": 8, "game": "@ NYL"},
                {"name": "Briann January", "position": "G", "salary": 4200, "projection": 18.9, "team": "CONN", "ownership": 6, "game": "@ LVA"}
            ]
        }
    
    def generate_lineups(self, count=5):
        """Generate multiple optimized lineups"""
        print(f"🎯 Generating {count} optimal lineups...")
        
        lineups = []
        strategies = ["Ceiling", "Balanced", "Contrarian", "Game Stack", "Value"]
        
        for i in range(count):
            strategy = strategies[i % len(strategies)]
            lineup = self.build_lineup_by_strategy(strategy)
            
            if lineup and self.validate_lineup(lineup):
                lineup['strategy'] = strategy
                lineup['number'] = i + 1
                lineups.append(lineup)
                print(f"  ✅ {strategy} lineup: ${lineup['salary']}/50000, {lineup['projection']:.1f} proj")
            else:
                print(f"  ❌ Failed to build {strategy} lineup")
        
        return lineups
    
    def build_lineup_by_strategy(self, strategy):
        """Build lineup based on specific strategy"""
        players = self.player_pool["guards"]  # All players in one pool for simplicity
        
        if strategy == "Ceiling":
            return self.build_ceiling_lineup(players)
        elif strategy == "Balanced":
            return self.build_balanced_lineup(players)
        elif strategy == "Contrarian":
            return self.build_contrarian_lineup(players)
        elif strategy == "Game Stack":
            return self.build_game_stack_lineup(players)
        elif strategy == "Value":
            return self.build_value_lineup(players)
        else:
            return self.build_balanced_lineup(players)
    
    def build_ceiling_lineup(self, players):
        """Build highest ceiling lineup"""
        # Sort by projection, take top players within salary
        sorted_players = sorted(players, key=lambda x: x['projection'], reverse=True)
        
        selected = []
        total_salary = 0
        
        for player in sorted_players:
            if len(selected) < 6 and total_salary + player['salary'] <= self.salary_cap:
                selected.append(player)
                total_salary += player['salary']
        
        return self.create_lineup_object(selected)
    
    def build_balanced_lineup(self, players):
        """Build balanced risk/reward lineup"""
        # Target: 1-2 high salary, 2-3 mid salary, 1-2 value plays
        
        high_salary = [p for p in players if p['salary'] >= 9000]
        mid_salary = [p for p in players if 6000 <= p['salary'] < 9000]
        value_plays = [p for p in players if p['salary'] < 6000]
        
        selected = []
        
        # Add 1 high salary player
        if high_salary:
            selected.append(max(high_salary, key=lambda x: x['projection']))
        
        # Add 3 mid salary players
        mid_sorted = sorted(mid_salary, key=lambda x: x['projection']/x['salary']*1000, reverse=True)
        selected.extend(mid_sorted[:3])
        
        # Fill with value plays
        remaining_salary = self.salary_cap - sum(p['salary'] for p in selected)
        value_sorted = sorted(value_plays, key=lambda x: x['projection'], reverse=True)
        
        for player in value_sorted:
            if len(selected) < 6 and player['salary'] <= remaining_salary:
                selected.append(player)
                remaining_salary -= player['salary']
        
        return self.create_lineup_object(selected)
    
    def build_contrarian_lineup(self, players):
        """Build low-ownership contrarian lineup"""
        # Sort by low ownership, but maintain reasonable projections
        contrarian_players = sorted(players, key=lambda x: x['ownership'])
        
        selected = []
        total_salary = 0
        
        for player in contrarian_players:
            if (len(selected) < 6 and 
                total_salary + player['salary'] <= self.salary_cap and
                player['projection'] >= 20):  # Minimum projection threshold
                selected.append(player)
                total_salary += player['salary']
        
        return self.create_lineup_object(selected)
    
    def build_game_stack_lineup(self, players):
        """Build lineup stacking specific games"""
        # Focus on Aces vs Sun game (highest projected total)
        lva_conn_players = [p for p in players if p['team'] in ['LVA', 'CONN']]
        nyl_min_players = [p for p in players if p['team'] in ['NYL', 'MIN']]
        
        selected = []
        
        # Take 3 from LVA/CONN game
        lva_conn_sorted = sorted(lva_conn_players, key=lambda x: x['projection'], reverse=True)
        selected.extend(lva_conn_sorted[:3])
        
        # Take 2 from NYL/MIN game  
        nyl_min_sorted = sorted(nyl_min_players, key=lambda x: x['projection'], reverse=True)
        selected.extend(nyl_min_sorted[:2])
        
        # Fill last spot with best remaining value
        remaining_salary = self.salary_cap - sum(p['salary'] for p in selected)
        remaining_players = [p for p in players if p not in selected]
        
        for player in sorted(remaining_players, key=lambda x: x['projection'], reverse=True):
            if player['salary'] <= remaining_salary:
                selected.append(player)
                break
        
        return self.create_lineup_object(selected)
    
    def build_value_lineup(self, players):
        """Build best points-per-dollar lineup"""
        # Calculate value score (projection per $1000 salary)
        for player in players:
            player['value'] = player['projection'] / (player['salary'] / 1000)
        
        value_sorted = sorted(players, key=lambda x: x['value'], reverse=True)
        
        selected = []
        total_salary = 0
        
        for player in value_sorted:
            if len(selected) < 6 and total_salary + player['salary'] <= self.salary_cap:
                selected.append(player)
                total_salary += player['salary']
        
        return self.create_lineup_object(selected)
    
    def create_lineup_object(self, players):
        """Create standardized lineup object"""
        if len(players) != 6:
            return None
        
        total_salary = sum(p['salary'] for p in players)
        total_projection = sum(p['projection'] for p in players)
        avg_ownership = sum(p['ownership'] for p in players) / len(players)
        
        return {
            'players': players,
            'salary': total_salary,
            'projection': total_projection,
            'ownership': avg_ownership,
            'salary_remaining': self.salary_cap - total_salary
        }
    
    def validate_lineup(self, lineup):
        """Validate lineup meets requirements"""
        if not lineup:
            return False
        
        # Check salary cap
        if lineup['salary'] > self.salary_cap:
            return False
        
        # Check player count
        if len(lineup['players']) != 6:
            return False
        
        # Check position requirements (simplified for WNBA)
        guards = sum(1 for p in lineup['players'] if p['position'] == 'G')
        forwards = sum(1 for p in lineup['players'] if p['position'] == 'F')
        
        # WNBA DK format: need at least 2G, 3F, 1 UTIL
        if guards < 2 or forwards < 3:
            return False
        
        return True
    
    def export_to_csv(self, lineups):
        """Export lineups to DraftKings CSV format"""
        csv_content = "G,G,F,F,F,UTIL\n"
        
        for lineup in lineups:
            row = []
            players = lineup['players']
            
            # Sort players by position for DK format
            guards = [p for p in players if p['position'] == 'G']
            forwards = [p for p in players if p['position'] == 'F']
            
            # Fill positions
            row.extend([g['name'] for g in guards[:2]])  # G, G
            row.extend([f['name'] for f in forwards[:3]])  # F, F, F
            
            # UTIL (remaining player)
            remaining = [p for p in players if p not in guards[:2] and p not in forwards[:3]]
            if remaining:
                row.append(remaining[0]['name'])
            else:
                row.append(players[-1]['name'])  # Fallback
            
            csv_content += ",".join(row) + "\n"
        
        return csv_content
    
    def get_stack_recommendations(self):
        """Get game stacking recommendations"""
        recommendations = [
            {
                'game': 'LVA vs CONN',
                'reason': 'Highest projected total (175+)',
                'players': ['A\'ja Wilson', 'Kelsey Plum', 'Alyssa Thomas'],
                'priority': 'HIGH'
            },
            {
                'game': 'NYL vs MIN', 
                'reason': 'Championship rematch, high pace',
                'players': ['Breanna Stewart', 'Sabrina Ionescu', 'Napheesa Collier'],
                'priority': 'MEDIUM'
            },
            {
                'game': 'DAL vs WSH',
                'reason': 'Paige Bueckers debut value',
                'players': ['Paige Bueckers'],
                'priority': 'MEDIUM'
            }
        ]
        
        return recommendations
    
    def optimize_for_contest_type(self, contest_type, lineup_count=1):
        """Optimize lineups for specific contest types"""
        if contest_type == "GPP":
            # Tournament play - high ceiling, lower ownership
            return [self.build_ceiling_lineup(self.player_pool["guards"])]
        
        elif contest_type == "Cash":
            # Cash games - high floor, consistent scoring
            return [self.build_balanced_lineup(self.player_pool["guards"])]
        
        elif contest_type == "Single Entry":
            # Single entry tournaments - balanced approach
            return [self.build_game_stack_lineup(self.player_pool["guards"])]
        
        else:
            # Default - generate multiple strategies
            return self.generate_lineups(lineup_count)
