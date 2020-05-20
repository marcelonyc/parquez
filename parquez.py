from mlrun import get_or_create_ctx
from core.input_parser import InputParser
#from utils.logger import Logger
from core.parquet_table import ParquetTable
from core.cron_tab import Crontab
from config.app_conf import AppConf
from core.kv_table import KVTable
from core.kv_view import KVView
from core.presto_client import PrestoClient
from utils.utils import Utils
#import logging

CONFIG_PATH = 'config/parquez.ini'
#LEVEL = logging.INFO


def main(context,view_name="view_name",partition_by='h',partition_interval='1h',real_time_window='1d',historical_retention='1w',config_path=CONFIG_PATH):
    #logger = Logger(LEVEL)
    context.logger.info("Starting to Parquezzzzzzzz")

    parser = InputParser(context.logger)
    args = parser.parse_args(["--view_name", view_name
                                 ,"--partition-by", partition_by
                                 ,"--partition-interval", partition_interval
                                 , "--real-time-window",real_time_window
                                 , "--historical-retention", historical_retention, "--config-path", config_path
                              ])
    context.logger.info("input parsed")

    if args.config is not None:
        config_path = args.config
    else:
        config_path = CONFIG_PATH

    conf = AppConf(context.logger, config_path)
    context.logger.info("loading configuration")

    # should be deleted from 2.3 versions
    context.logger.info("initializing setup")
    utils = Utils(context.logger, conf)
    #utils.copy_to_v3io("v3io-spark2-tools_2.11.jar")

    context.logger.info("validating kv table")
    kv_table = KVTable(context.logger, conf, args.real_time_table_name)
    kv_table.import_table_schema()

    context.logger.info("generating parquet table")
    parquet = ParquetTable(context.logger,conf, utils, args.partition_by, kv_table)
    parquet.generate_script()

    context.logger.info("generating view over kv")
    kv_view = KVView(context.logger, args.real_time_window, conf, kv_table)
    kv_view.generate_crete_view_script()

    context.logger.info("generating presto view")
    prest = PrestoClient(context.logger, conf, args.partition_by, parquet, kv_view, kv_table)
    prest.generate_unified_view()

    context.logger.info("generating cronJob")
    cr = Crontab(context.logger, conf, args.real_time_table_name, args.partition_interval, args.real_time_window,
                 args.historical_retention, args.partition_by)
    cr.create_cron_job()


if __name__ == '__main__':
    context = get_or_create_ctx('parquez')
    main(context)










