from dfktools.hero.utils import utils as hero_utils
from dfktools.quests.utils import utils as QuestUtils
from dfktools.hero import hero_core
from dfktools.quests import quest_core_v3
from dfktools.hero.heroes import Heroes
from dfktools.quests.quest_v3 import Quest
from dfktools.quests.utils import utils as quest_utils

import os
import time
from pathlib import Path

from web3 import Web3
import itertools

import utils.net as NetData

from dotenv import load_dotenv

class Questing:
    def __init__(self, network_name, logger, tx_timeout = 30 ):
        load_dotenv()
        self.rpc = self.decode_rpc(network_name)
        self.network_name = network_name
        self.logger = logger
        
        private_key = os.environ["PRIVATE_KEY"]
        self.private_key = private_key
        self.w3 = Web3(Web3.HTTPProvider(self.rpc))
        self.account_address = self.w3.eth.account.from_key(private_key).address
        self.tx_timeout = tx_timeout

        self.gas = {'maxFeePerGas': 25, 'maxPriorityFeePerGas': 2}

        self.generate_quest_object()
        self.generate_hero_object()

        return

    def decode_rpc(self, network_name):
        return NetData.networks.get(network_name).get('NetworkUrl')

    def decode_quest_type(self, quest_type_id):
        return QuestUtils.v3_quest_types.get(quest_type_id)

    def generate_quest_object(self):
        self.InstanceQuest = Quest(NetData.networks.get(self.network_name).get('ContractQuest'), self.rpc, self.logger)

    def generate_hero_object(self):
        self.InstanceHero = Heroes(NetData.networks.get(self.network_name).get('ContractHero'), self.rpc, self.logger)

    def generate_player_hero_list(self):
        with open(Path(__file__).parent / '../hero/femaleFirstName.json', 'r') as f:
            female_first_names = hero_utils.parse_names(f.read())

        with open(Path(Path(__file__).parent / '../hero/maleFirstName.json'), 'r') as f:
            male_first_names = hero_utils.parse_names(f.read())

        with open(Path(Path(__file__).parent / '../hero/lastName.json'), 'r') as f:
            last_names = hero_utils.parse_names(f.read())

        my_heroes = self.InstanceHero.get_users_heroes(self.account_address)
        hero_list = []
        for idx, hero in enumerate(my_heroes):
            # logger.info("Processing crystalvale hero #" + str(idx))
            hero = self.InstanceHero.get_hero(hero)
            readable_hero = self.InstanceHero.human_readable_hero(hero, male_first_names, female_first_names, last_names)
            hero_list.append(readable_hero)
        self.player_heroes = hero_list
        return self.player_heroes

    def get_active_quests(self):
        # Not sure if quest instance updates if used again for active quests
        # TODO: Check if active quests are refreshed if using same quest object instance
        # Temp solution is to remake the object on every run as below
        self.generate_quest_object()
        
        self.active_quests = self.InstanceQuest.get_active_quests(self.account_address)
        return self.active_quests

    def get_active_heroes(self):
        # Dependencies
        if not hasattr(self, 'active_quests'):
            self.get_active_quests()

        self.active_heroes = list(itertools.chain.from_iterable([hero[3] for hero in self.active_quests]))
        return self.active_heroes
    
    def filter_active_heroes(self, min_stam, quest_name):
        # Dependencies
        if not hasattr(self, 'player_heroes'):
            self.generate_player_hero_list()
        
        if not hasattr(self, 'active_heroes'):
            self.get_active_heroes()


        self.ready_hero_list = list(filter(lambda hero: 
                                        hero.get('info').get('statGenes').get('profession') == quest_name.lower()
                                        and self.InstanceQuest.get_current_stamina(hero.get('id')) >= min_stam
                                        and hero.get('id') not in self.active_heroes
                                        ,
                                        self.player_heroes))
        return self.ready_hero_list

    
    def filter_ready_prof_0(self, quest_name):      
        return list(filter(lambda hero: hero.get('professions').get(quest_name.lower()) < 100,
                                    self.ready_hero_list))
        
    def filter_ready_prof_10(self, quest_name):
        return list(filter(lambda hero: hero.get('professions').get(quest_name.lower() ) >= 100,
                                   self.ready_hero_list))
    
    def run_batches(self, batched_list, level, attempts, quest_type, pool = 0):
            quest_id = NetData.networks.get(self.network_name).get('Questing').get(quest_type).get('ID')

            for chunk in batched_list:
                try:
                    self.InstanceQuest.start_quest(chunk, 
                                                # Type needs to be changed as well
                                                quest_id, 
                                                attempts, 
                                                level,
                                                pool, 
                                                self.private_key, 
                                                self.w3.eth.get_transaction_count(self.account_address), 
                                                self.gas, 
                                                self.tx_timeout)
                except Exception as error:
                    print(error)
                    continue
    
    def finish_completed_quests(self):
        active_quests = self.active_quests
        completed_active_quests = list(filter(lambda x: x[7] < time.time(), active_quests))

        if len(completed_active_quests) > 0:
            for quest in completed_active_quests:
                tx_receipt = self.InstanceQuest.complete_quest(quest[3][0], 
                                                               self.private_key, self.w3.eth.get_transaction_count(self.account_address), 
                                                               self.gas, 
                                                               self.tx_timeout)
                quest_result = self.InstanceQuest.parse_complete_quest_receipt(tx_receipt)
                quest_rewards = quest_utils.human_readable_quest_results(quest_result, very_human=True)
                self.logger.info("Rewards: {}".format(str(quest_rewards)))
        else:
            self.logger.info("No active quests to complete")
    
    @staticmethod
    def chunk_hero_list(hero_list, n):
        return [hero_list[i:i+n] for i in range(0, len(hero_list), n)]
    
    @staticmethod
    def readable_hero_to_idlist(readable_hero_list):
        return [hero.get('id') for hero in readable_hero_list]
    