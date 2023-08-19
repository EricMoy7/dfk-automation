from questing_actions.questing import Questing
import logging
import time
import sys

log_format = '%(asctime)s|%(name)s|%(levelname)s: %(message)s'

logger = logging.getLogger("DFK-hero")
logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.INFO, format=log_format, stream=sys.stdout)

Quester = Questing(
    # Network, QuestId, Attempts, Pool, logger
    'Crystalvale',
    logger)

Quester.generate_player_hero_list()
Quester.get_active_quests()
Quester.get_active_heroes()

Quester.filter_active_heroes(25, 'Fishing')
lvl0_heroes_fishing = Quester.filter_ready_prof_0('Fishing')
lvl10_heroes_fishing = Quester.filter_ready_prof_10('Fishing')
Quester.run_batches(Quester.chunk_hero_list(Quester.readable_hero_to_idlist(lvl0_heroes_fishing), 6), 0, 5, 'Fishing')
Quester.run_batches(Quester.chunk_hero_list(Quester.readable_hero_to_idlist(lvl10_heroes_fishing), 6), 10, 5, 'Fishing')

Quester.filter_active_heroes(25, 'Foraging')
lvl0_heroes_fishing = Quester.filter_ready_prof_0('Foraging')
lvl10_heroes_fishing = Quester.filter_ready_prof_10('Foraging')
Quester.run_batches(Quester.chunk_hero_list(Quester.readable_hero_to_idlist(lvl0_heroes_fishing), 6), 0, 5, 'Foraging')
Quester.run_batches(Quester.chunk_hero_list(Quester.readable_hero_to_idlist(lvl10_heroes_fishing), 6), 10, 5, 'Foraging')

