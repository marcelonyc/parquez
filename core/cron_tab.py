import os
import re
from core.params import Params
from config.app_conf import AppConf

PARTITION_BY_RE = r"([0-9]+)([a-zA-Z]+)"


# def get_shell_path():
#     shell_path = os.getcwd() + "/sh/"
#     if "/tests/" in shell_path:
#         shell_path = shell_path.replace('tests/', '')
#     return shell_path


def window_parser(window_type):
    m = re.match(PARTITION_BY_RE, window_type)
    result = ""
    if m.group(2) == 'm':
        result = m.group(1) + " minutes"
    if m.group(2) == 'h':
        result = m.group(1) + " hours"
    if m.group(2) == 'd':
        result = m.group(1) + " days"
    if m.group(2) == 'M':
        result = m.group(1) + " months"
    return result


class CronTab(object):
    def __init__(self, logger, conf: AppConf, params: Params, project_path=""):
        self.logger = logger
        self.conf = conf
        self.kv_table_name = params.real_time_table_name
        self.partition_interval = params.partition_interval
        self.key_value_window = params.real_time_window
        self.historical_retention = params.historical_retention
        self.partition_by = params.partition_by
        self.project_path = project_path

    def create_cron_string(self):
        m = re.match(PARTITION_BY_RE, self.partition_interval)
        if m.group(2) == 'm':
            result = "*/" + m.group(1) + " * * * * "
        if m.group(2) == 'h':
            result = "0 " + "*/" + m.group(1) + " * * * "
        if m.group(2) == 'd':
            if m.group(1) == 1:
                result = "0 0 " + "* * * "
            else:
                result = "0 0 " + "*/" + m.group(1) + " * * "
        if m.group(2) == 'M':
            result = "0 0 0" + "*/" + m.group(1) + " * "
        if m.group(2) == 'DW':
            result = "0 0 0 0 " + "*/" + m.group(1)
        return result

    def create_cron_command(self):
        args2 = "'" + window_parser(self.key_value_window) + "'"
        args3 = "'" + window_parser(self.historical_retention) + "'"
        args4 = "'" + self.partition_by + "'"
        args5 = "'" + self.conf.v3io_container + "'"
        args6 = "'" + self.conf.hive_schema + "'"
        args7 = "'" + self.conf.compression + "'"
        args8 = "'" + self.conf.coalesce + "'"

        command = self.project_path + "/sh/parquetinizer.sh " + self.kv_table_name + " " + \
                  args2 + " " + args3 + " " + args4 + " " + args5 + " " + args6 + " " + args7 + " " + args8

        self.logger.info(command)
        return command

    # def run_command(self):
    #     command = self.create_cron_command()
    #     self.k8sClient.exec_shell_cmd(command)
