from questing_actions.questing import Questing

from dfktools.quests.professions import gardening as GardenTools

import utils.net as NetData

class Gardening(Questing):
    def __init__(self, network_name, logger):
        super().__init__(network_name, logger)
    
    def get_active_pools(self):
        active_quests = super().get_active_quests()
        self.active_pool_ids = list(map(lambda x: x[9], active_quests))
        return self.active_pool_ids
    
    def hero_distributed_pools(self, hero_list):
        if not hasattr(self, 'active_pool_ids'):
            self.get_active_pools()
        
        gardening_pool_ids = range(1,13)

        occurances = list(map(lambda x: self.active_pool_ids.count(x), gardening_pool_ids))

        batches = self.chunk_hero_list(self.readable_hero_to_idlist(hero_list), 2)

        distributed_heroes = []

        # Round robin algo with pre filled active quests (buckets)
        j = 1
        while len(batches) > 0:
            for i, pool_occurances in enumerate(occurances):
                if (pool_occurances < j) and len(batches) > 0:
                    occurances[i] += 1
                    distributed_heroes.append((batches[0], i))
                    batches.pop(0)
            j += 1
        
        self.distributed_heroes = distributed_heroes
        return distributed_heroes
    
    def run_batches(self, batched_list, level, attempts, quest_type):
            quest_id = NetData.networks.get(self.network_name).get('Questing').get(quest_type).get('ID')

            for chunk in batched_list:
                try:
                    self.InstanceQuest.start_quest(chunk[0], 
                                                # Type needs to be changed as well
                                                quest_id, 
                                                attempts, 
                                                level,
                                                chunk[1], 
                                                self.private_key, 
                                                self.w3.eth.get_transaction_count(self.account_address), 
                                                self.gas, 
                                                self.tx_timeout)
                except Exception as error:
                    print(error)
                    continue

    
    @staticmethod
    def chunk_hero_list(hero_list, n):
        batches = [hero_list[i:i+n] for i in range(0, len(hero_list), n)]
        force_coupling_batches = list(filter(lambda x: len(x) == 2, batches))
        return force_coupling_batches

        

