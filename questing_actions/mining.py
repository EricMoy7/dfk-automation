from questing_actions.questing import Questing

class Mining(Questing):
    def __init__(self, network_name, logger):
        super().__init__(network_name, logger)
    
    @staticmethod
    def chunk_hero_list(hero_list, n):
        batches = [hero_list[i:i+n] for i in range(0, len(hero_list), n)]
        force_coupling_batches = list(filter(lambda x: len(x) == 6, batches))
        return force_coupling_batches

        