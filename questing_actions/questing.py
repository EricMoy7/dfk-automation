from dfktools.hero.utils import utils as hero_utils
from dfktools.quests.utils import utils as QuestUtils
from dfktools.hero import hero_core
from dfktools.quests import quest_core_v3
from dfktools.hero.heroes import Heroes
from dfktools.quests.quest_v3 import Quest


import os
from web3 import Web3
import itertools

import utils.net as NetData

class Questing:
    def __init__(self, network_name, quest_id, attempts, level, pool_type, logger, tx_timeout = 30 ):
        self.rpc = self.decode_rpc(network_name)
        self.network_name = network_name
        self.logger = logger

        self.quest_type = self.decode_quest_type(quest_id)
        self.attempts = attempts
        self.level = level
        self.pool_type = pool_type
        
        private_key = os.environ["PRIVATE_KEY"]
        self.private_key = private_key
        self.w3 = Web3(Web3.HTTPProvider(self.rpc))
        self.account_address = self.w3.eth.account.from_key(private_key).address

        self.nonce = self.w3.eth.get_transaction_count(self.account_address)
        self.tx_timeout = tx_timeout

        self.gas = {'maxFeePerGas': 25, 'maxPriorityFeePerGas': 2}

        return

    def decode_rpc(self, network_name):
        return NetData.networks.get(network_name).get('NetworkUrl')

    def decode_quest_type(self, quest_type_id):
        return QuestUtils.v3_quest_types.get(quest_type_id)

    def generate_quest_object(self):
        self.InstanceQuest = Quest(NetData.networks.get(self.network_name).get('ContractQuest'), self.rpc, self.logger)

    def generate_hero_object(self):
        self.InstanceHero = Heroes(NetData.networks.get(self.network_name).get('HeroQuest'), self.rpc, self.logger)

    def get_active_quests(self):
        # Not sure if quest instance updates if used again for active quests
        # TODO: Check if active quests are refreshed if using same quest object instance
        # Temp solution is to remake the object on every run as below
        self.generate_quest_object()
        
        self.active_quests = self.InstanceQuest.get_active_quests(self.account_address)
        return self.active_quests

    def get_active_heroes(self):
        self.active_heroes = list(itertools.chain.from_iterable([hero[3] for hero in self.active_quests]))
        return self.active_heroes
    
    def filter_active_heroes(self, min_stam):
        self.ready_hero_list = list(filter(lambda hero: hero.get('info').get('statGenes').get('profession') == prof
                                        and self.InstanceQuest.get_current_stamina(hero.get('id') >= min_stam)
                                        and hero.get('id' not in self.active_heroes),
                                        self.active_heroes))
        return self.ready_hero_list

    
    def filter_ready_prof_0(self):      
        return list(filter(lambda hero: hero.get('professions').get(self.quest_type) < 100,
                                    self.ready_hero_list))
        
    def filter_ready_prof_10(self):
        return list(filter(lambda hero: hero.get('professions').get(self.quest_type) >= 100,
                                   self.ready_hero_list))
    
    def run_batches(self, batched_list):
            for chunk in batched_list:
                try:
                    self.InstanceQuest.start_quest(chunk, 
                                                # Type needs to be changed as well
                                                self.quest_type, 
                                                self.attempts, 
                                                self.level,
                                                # Gardening/Mining Crystal needs pool id
                                                0, 
                                                self.private_key, 
                                                self.nonce, 
                                                self.gas, 
                                                self.tx_timeout)
                except Exception as error:
                    # logger.warn(error)
                    continue
    
    @staticmethod
    def chunk_hero_list(hero_list, n):
        return [hero_list[i:i+n] for i in range(0, len(hero_list), n)]