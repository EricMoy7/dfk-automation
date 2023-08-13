import logging
import time
import sys
from web3 import Web3
from dotenv import load_dotenv
import os
import time

from dfktools.hero.utils import utils as hero_utils
from dfktools.hero import hero_core
from dfktools.quests import quest_core_v3
from dfktools.hero.heroes import Heroes
from dfktools.quests.quest_v3 import Quest
from dfktools.quests.utils import utils as quest_utils

import utils.rpcs as RPCS

load_dotenv()

def finish_quests():
    serendale2_rpc_server = RPCS.SERENDALE2_RPC_SERVER
    crystalvale_rpc_server = RPCS.CRYSTALVALE_RPC_SERVER

    account_address = os.environ["ACCOUNT_ADDRESS"]
    # Remove
    private_key = os.environ["PRIVATE_KEY"]
    w3_serendale2 = Web3(Web3.HTTPProvider(serendale2_rpc_server))
    w3_crystalvale = Web3(Web3.HTTPProvider(crystalvale_rpc_server))


    log_format = '%(asctime)s|%(name)s|%(levelname)s: %(message)s'

    logger = logging.getLogger("DFK-hero")
    logger.setLevel(logging.DEBUG)
    logging.basicConfig(level=logging.INFO, format=log_format, stream=sys.stdout)

    InstanceHero = Heroes(hero_core.CRYSTALVALE_CONTRACT_ADDRESS, 'https://subnets.avax.network/defi-kingdoms/dfk-chain/rpc', logger)
    InstanceQuest = Quest(quest_core_v3.CRYSTALVALE_CONTRACT_ADDRESS, 'https://subnets.avax.network/defi-kingdoms/dfk-chain/rpc', logger)


    active_quests = InstanceQuest.get_active_quests(account_address)
    finished_active_quests = list(filter(lambda x: x[7] < time.time(), active_quests))
    len(finished_active_quests)

    gas_price_gwei_serendale = {'maxFeePerGas': 55, 'maxPriorityFeePerGas': 25}  # EIP-1559
    gas_price_gwei_crystalvale = {'maxFeePerGas': 30, 'maxPriorityFeePerGas': 10}  # EIP-1559
    tx_timeout = 30

    if len(finished_active_quests) > 0:
        for quest in finished_active_quests:
            tx_receipt = InstanceQuest.complete_quest(quest[3][0], private_key, w3_crystalvale.eth.get_transaction_count(account_address), gas_price_gwei_crystalvale, tx_timeout)
            quest_result = InstanceQuest.parse_complete_quest_receipt(tx_receipt)
            quest_rewards = quest_utils.human_readable_quest_results(quest_result, very_human=True)
            logger.info("Rewards: {}".format(str(quest_rewards)))
    else:
        logger.info("No active quests to complete")
    

