from mlrun import get_or_create_ctx
from config.app_conf import AppConf
from core.parquet_table import ParquetTable
from core.k8s_client import K8SClient
from core.params import Params


def get_bytes_from_file(filename):
    with open(filename, "r") as f:
        output = f.read()
    return output


def main(context):
    context.logger.info("loading configuration")
    p_config_path = context.parameters['config_path']
    if p_config_path:
        config_path = p_config_path
    conf = AppConf(context.logger, config_path)
    params = Params()
    params.set_params_from_context(context)
    context.logger.info("generating parquet table")
    schema = get_bytes_from_file(context.artifact_path+"/parquet_schema.txt")
    parquet = ParquetTable(context.logger, conf, params, schema, K8SClient(context.logger))
    parquet.create()


if __name__ == '__main__':
    context = get_or_create_ctx('create-parquet-table')
    main(context)
