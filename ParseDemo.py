from awpy import Demo, stats
from create_hash import set_game_id


class StatsFromDemo:
    def __init__(self, raw_dem, date_and_time='NoData'):
        self.dem = Demo(raw_dem)
        self.total_score = {'CT': {'team': None, 'score': 0}, 'TERRORIST': {'team': None, 'score': 0}}
        self.date_and_time = date_and_time
        self.players_stats = {}
        self.players_count = 0
        self.map = None

        self.game_id = set_game_id(raw_dem, date_and_time)

        self.find_raw_score()
        self.get_players_stats()
        self.find_map()


    def find_raw_score(self):
        for game_round in self.dem.rounds.itertuples():
            if game_round.Index < 12:
                match game_round.winner:
                    case 'CT':
                        self.total_score['CT']['score'] += 1
                    case 'T':
                        self.total_score['TERRORIST']['score'] += 1
            else:
                match game_round.winner:
                    case 'CT':
                        self.total_score['TERRORIST']['score'] += 1
                    case 'T':
                        self.total_score['CT']['score'] += 1


    def is_player_in_list(self, player_name, player_id, player_team_name):
        if player_id not in self.players_stats:
            self.players_stats[player_id] = {'name': player_name, 'team': player_team_name,
                                        'kills': 0, 'deaths': 0, 'assists': 0}
            self.players_count += 1


    @staticmethod
    def check_not_friendly_fire(target_player_team_name, victim_player_team_name) -> bool:
        return target_player_team_name != victim_player_team_name


    def add_value_to_player_score(self, steamid, action):
        self.players_stats[steamid][action] += 1


    def create_score_with_team_names(self, attacker_team_clan_name, attacker_team_name, victim_team_clan_name, victim_team_name):
        self.total_score[attacker_team_name]['team'] = attacker_team_clan_name
        self.total_score[victim_team_name]['team'] = victim_team_clan_name


    def get_players_stats(self):
        usable_colums = ['attacker_name', 'attacker_steamid', 'attacker_team_clan_name', 'attacker_team_name',
                         'assister_name','assister_steamid', 'assister_team_clan_name',
                         'victim_name', 'victim_steamid', 'victim_team_clan_name', 'victim_team_name']

        result = self.dem.kills[usable_colums]

        for event in result.itertuples():
            attacker_name = event.attacker_name
            attacker_steamid = event.attacker_steamid
            attacker_team_clan_name = event.attacker_team_clan_name
            attacker_team_name = event.attacker_team_name
            victim_name = event.victim_name
            victim_steamid = event.victim_steamid
            victim_team_clan_name = event.victim_team_clan_name
            victim_team_name = event.victim_team_name

            if self.players_count < 10:
               self.is_player_in_list(attacker_name, attacker_steamid, attacker_team_clan_name) # проверка на количество игроков в словаре, чтобы не вызывать повторно функцию

            if self.players_count < 10:
               self.is_player_in_list(victim_name, victim_steamid, victim_team_clan_name) # проверка на количество игроков в словаре, чтобы не вызывать повторно функцию

            if attacker_name and self.check_not_friendly_fire(attacker_team_clan_name, victim_team_clan_name):
                self.add_value_to_player_score(attacker_steamid, 'kills')
            self.add_value_to_player_score(victim_steamid, 'deaths')

            assister_name = event.assister_name
            assister_steamid = event.assister_steamid
            assister_team_clan_name = event.assister_team_clan_name

            if assister_name and self.check_not_friendly_fire(assister_team_clan_name, victim_team_clan_name):  # Проверка был ли ассист и не было ли огня по своим
                if self.players_count < 10:
                   self.is_player_in_list(assister_name, assister_steamid, assister_team_clan_name) # проверка на количество игроков в словаре, чтобы не вызывать повторно функцию
                self.add_value_to_player_score(assister_steamid, 'assists')

            if not self.total_score['CT']['team'] and not self.total_score['CT']['team'] and attacker_name and victim_name and self.check_not_friendly_fire(attacker_team_clan_name, victim_team_clan_name): # Названия записываются, когда в словаре нет названий команд, оба игрока существуют и они из разных команд
                self.create_score_with_team_names(attacker_team_clan_name, attacker_team_name, victim_team_clan_name, victim_team_name) #Переименование команд


    def find_map(self):
        self.map = self.dem.header['map_name']