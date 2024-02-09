from questing_actions.questing import Questing
from questing_actions.gardening import Gardening
from questing_actions.mining import Mining

import logging
import time
import sys
from logging.handlers import TimedRotatingFileHandler
import warnings

warnings.filterwarnings('ignore') 

log_handler = TimedRotatingFileHandler('runtime.log', when='D', interval=1, 
                                       backupCount=10, encoding='utf-8', delay=False)

log_format = '%(asctime)s|%(name)s|%(levelname)s: %(message)s'
log_handler.setFormatter(log_format)

logger = logging.getLogger("DFK-hero")
logger.setLevel(logging.DEBUG)

logger.addHandler(log_handler)
logging.basicConfig(level=logging.INFO, format=log_format, stream=sys.stdout)

while True:
    try:
        Quester = Questing('Crystalvale',logger)
        Miner = Mining('Crystalvale', logger)
        Gardener = Gardening('Crystalvale', logger)

        Quester.generate_player_hero_list()
        Quester.get_active_quests()
        Quester.get_active_heroes()
    

        logger.info('Starting Fishing Quests')
        Quester.filter_active_heroes(25, 'Fishing')
        lvl0_heroes_fishing = Quester.filter_ready_prof_0('Fishing')
        lvl10_heroes_fishing = Quester.filter_ready_prof_10('Fishing')
        Quester.run_batches(Quester.chunk_hero_list(Quester.readable_hero_to_idlist(lvl0_heroes_fishing), 6), 0, 5, 'Fishing')
        Quester.run_batches(Quester.chunk_hero_list(Quester.readable_hero_to_idlist(lvl10_heroes_fishing), 6), 10, 5, 'Fishing')

        logger.info('Starting Foraging Quests')
        Quester.filter_active_heroes(25, 'Foraging')
        lvl0_heroes_fishing = Quester.filter_ready_prof_0('Foraging')
        lvl10_heroes_fishing = Quester.filter_ready_prof_10('Foraging')
        Quester.run_batches(Quester.chunk_hero_list(Quester.readable_hero_to_idlist(lvl0_heroes_fishing), 6), 0, 5, 'Foraging')
        Quester.run_batches(Quester.chunk_hero_list(Quester.readable_hero_to_idlist(lvl10_heroes_fishing), 6), 10, 5, 'Foraging')

        logger.info('Starting Gardening Quests')
        Gardener.filter_active_heroes(25, 'Gardening')
        lvl0_gardeners = Gardener.filter_ready_prof_0('Gardening')
        lvl10_gardeners = Gardener.filter_ready_prof_10('Gardening')
        lvl0_gardeners_dist = Gardener.hero_distributed_pools(lvl0_gardeners)
        lvl10_gardeners_dist = Gardener.hero_distributed_pools(lvl10_gardeners)
        Gardener.run_batches(lvl0_gardeners_dist, 0, 25, 'Gardening')
        Gardener.run_batches(lvl10_gardeners_dist, 10, 25, 'Gardening')

        logger.info('Starting Gold Mining Quests')
        ready_miners = Miner.filter_active_heroes(25, 'Mining')
        Miner.run_batches(Miner.chunk_hero_list(Miner.readable_hero_to_idlist(ready_miners), 6), 0, 25, 'Mining')

        logger.info('Attempting to finish quests')
        Quester.finish_completed_quests()

        for remaining in range(600, 0, -1):
            sys.stdout.write("\r")
            sys.stdout.write("{:2d} seconds remaining.".format(remaining)) 
            sys.stdout.flush()
            time.sleep(1)
    
    except Exception as Error:
        # logger.warn(Error)
        continue

