import logging
import time
import sys
from web3 import Web3
import os
import itertools

from dfktools.hero.utils import utils as hero_utils
from dfktools.hero import hero_core
from dfktools.quests import quest_core_v3
from dfktools.hero.heroes import Heroes
from dfktools.quests.quest_v3 import Quest
from dfktools.quests.utils import utils as quest_utils
import dfktools.quests.professions.gardening as garden

def start_quests():
    serendale2_rpc_server = 'https://klaytn.rpc.defikingdoms.com/'
    crystalvale_rpc_server = 'https://subnets.avax.network/defi-kingdoms/dfk-chain/rpc'

    account_address = os.environ["ACCOUNT_ADDRESS"]
    # Remove
    private_key = os.environ["PRIVATE_KEY"]
    w3_serendale2 = Web3(Web3.HTTPProvider(serendale2_rpc_server))
    w3_crystalvale = Web3(Web3.HTTPProvider(crystalvale_rpc_server))

    log_format = '%(asctime)s|%(name)s|%(levelname)s: %(message)s'

    logger = logging.getLogger("DFK-hero")
    logger.setLevel(logging.DEBUG)
    logging.basicConfig(level=logging.INFO, format=log_format, stream=sys.stdout)

    logger.info("Starting Quests")

    with open('hero/femaleFirstName.json', 'r') as f:
        female_first_names = hero_utils.parse_names(f.read())
        logger.info("Female hero first name loaded")

    with open('hero/maleFirstName.json', 'r') as f:
        male_first_names = hero_utils.parse_names(f.read())
        logger.info("Male hero first name loaded")

    with open('hero/lastName.json', 'r') as f:
        last_names = hero_utils.parse_names(f.read())
        logger.info("Hero last name loaded")

    InstanceHero = Heroes(hero_core.CRYSTALVALE_CONTRACT_ADDRESS, 'https://subnets.avax.network/defi-kingdoms/dfk-chain/rpc', logger)
    InstanceQuest = Quest(quest_core_v3.CRYSTALVALE_CONTRACT_ADDRESS, 'https://subnets.avax.network/defi-kingdoms/dfk-chain/rpc', logger)

    my_heroes = InstanceHero.get_users_heroes(account_address)

    hero_list = []
    for idx, hero in enumerate(my_heroes):
        # logger.info("Processing crystalvale hero #" + str(idx))
        hero = InstanceHero.get_hero(hero)
        readable_hero = InstanceHero.human_readable_hero(hero, male_first_names, female_first_names, last_names)
        hero_list.append(readable_hero)

    professions = {
        'fishing': quest_core_v3.QUEST_TYPE_FISHING,
        'mining': quest_core_v3.QUEST_TYPE_GOLD_MINING,
        'foraging': quest_core_v3.QUEST_TYPE_FORAGING,
        'gardening': quest_core_v3.QUEST_TYPE_GARDENING
    }

    lvl_bracket = [(0,99), (100,500)]

    # Need to account for netgative stamina
    # get_current_stamina if negative will cause overflow
    for lvls in lvl_bracket:
        logger.info(f'Starting quest for heroes from {lvls[0]} to {lvls[1]}')
        for key, quest_type in professions.items():
            active_quests = InstanceQuest.get_active_quests(account_address)
            active_heroes = list(itertools.chain.from_iterable([hero[3] for hero in active_quests]))
            prof_heros = list(filter(lambda x: x.get('info').get('statGenes').get('profession') == key 
                                    and InstanceQuest.get_current_stamina(x.get('id')) >= 25
                                    and x.get('id') not in active_heroes
                                    and x.get('professions').get(key) >= lvls[0]
                                    and x.get('professions').get(key) <= lvls[1],
                                    hero_list))
            
            # print(len(prof_heros))
            if len(prof_heros) > 0:
                hero_ids = [hero.get('id') for hero in prof_heros]

                # gas_price_gwei_serendale = {'maxFeePerGas': 55, 'maxPriorityFeePerGas': 25}  # EIP-1559
                gas_price_gwei_crystalvale = {'maxFeePerGas': 25, 'maxPriorityFeePerGas': 2}  # EIP-1559
                tx_timeout = 30

                attempts = 25 if key == 'mining' else 5
                level = 10 if lvls == (100,500) else 0
                n = 2 if key == 'gardening' else 6

                for chunk in [hero_ids[i:i+n] for i in range(0, len(hero_ids), n)]:
                    print(f'Processing chunk {chunk}')
                    try:
                        InstanceQuest.start_quest(chunk, 
                                            # Type needs to be changed as well
                                            quest_type, 
                                            attempts, 
                                            level,
                                            1 if key == 'gardening' else 0, 
                                            private_key, 
                                            w3_crystalvale.eth.get_transaction_count(account_address), 
                                            gas_price_gwei_crystalvale, 
                                            tx_timeout)
                    except Exception as error:
                        # logger.warn(error)
                        continue

            else:
                logger.info(f'No {key} heroes available')
