import os
import logging
import redis
from apps.TA import deployment_type

SIMULATED_ENV = deployment_type == "LOCAL"
# todo: use this to mark keys in redis db, so they can be separated and deleted

logger = logging.getLogger('redis_db')

if deployment_type == "LOCAL":
    REDIS_HOST, REDIS_PORT = "127.0.0.1:6379".split(":")
    pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0)
    database = redis.Redis(connection_pool=pool)
else:
    database = redis.from_url(os.environ.get("REDIS_URL"))

logger.info("Redis connection established for app database.")


allowed_tickers = [
    'AGI_BTC',
    'ADA_BTC',
    'FUEL_BTC',
    'XRP_USDT',
    'RCN_BTC',
    'TRX_USDT',
    'MFT_BTC',
    'SC_ETH',
    'VET_ETH',
    'XVG_ETH',
    'BCN_ETH',
    'ADA_USDT',
    'QKC_BTC',
    'CDT_ETH',
    'DENT_BTC',
    'TRX_ETH',
    'MTH_BTC',
    'ICX_USDT',
    'SNT_BTC',
    'IOTX_BTC',
    'YOYOW_BTC',
    'RPX_BTC',
    'NPXS_BTC',
    'VET_BTC',
    'HOT_ETH',
    'HOT_BTC',
    'SC_BTC',
    'ADA_ETH',
    'OST_ETH',
    'GTO_BTC',
    'NPXS_ETH',
    'TNT_BTC',
    'VET_USDT',
    'WPR_BTC',
    'REQ_BTC',
    'FUN_BTC',
    'XLM_USDT',
    'VIB_BTC',
    'XLM_BTC',
    'IOST_BTC',
    'XRP_BTC',
    'AST_BTC',
    'CHAT_BTC',
    'MFT_ETH',
    'ICX_BTC',
    'BCN_BTC',
    'CDT_BTC',
    'DOCK_BTC',
    'IOTX_ETH',
    'QKC_ETH',
    'KEY_ETH',
    'ZIL_ETH',
    'DENT_ETH',
    'IOTA_USDT',
    'POE_ETH',
    'OST_BTC',
    'TNB_BTC',
    'BAT_BTC',
    'ENJ_BTC',
    'XVG_BTC',
    'EOS_USDT',
    'STORM_BTC',
    'KEY_BTC',
    'TRX_BTC',
    'LEND_BTC',
    'ZIL_BTC',
    'POE_BTC',
    'NCASH_BTC'
]
