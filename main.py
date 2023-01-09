from Common import *
import utils.args_utils
import utils.log_utils
import os
import time

task_args, type_args, method_args, config_args = utils.args_utils.get_args()
utils.log_utils.SingleLogger().get_log_path(LOG_DIR, task_args, type_args, method_args, config_args)
LOGGER = utils.log_utils.SingleLogger().get_logger()

from Bin import Bin 
from Container import Container
import utils.data_utils

# 自定义随机箱子测试
# container = Container(20,10,10)
# bins = utils.generate.generate_bins(10, container)

data_path = os.path.abspath(os.path.join(PROJECT_ROOT,"test_data.txt"))
# 这里读取数据，两个数字分别是箱子的种类和选取的index，index从1开始
container, bins = utils.data_utils.read_task(data_path, task_args.bin_types, task_args.test_index) 
bins_volumn_sum = sum([single_bin.volume for single_bin in bins])
LOGGER.info(f"Container: {container}")

start_time = time.time()
if type_args.type == "online":
    for single_bin in bins:
        bin_place = container.online_search(single_bin, task_args.strict_level, method_args.method, **config_args.__dict__)
        LOGGER.info(f"Bin placed at {bin_place}")    
        LOGGER.info("Utilization: {0:.3f}".format(container.space_utilization))
        # container.print_2D_slice(Axis.HEIGHT,0,True)
elif type_args.type == "offline":
    bin_places = container.offline_search(bins, task_args.strict_level, method_args.method, **config_args.__dict__ )
    LOGGER.info("Utilization: {0:.3f}".format(container.space_utilization))
end_time = time.time()
time_spent = end_time - start_time
single_time_spent = time_spent / len(bins)
theory_utilization = min(bins_volumn_sum / container.volumn, 1)
score = container.space_utilization / theory_utilization
LOGGER.info(f"Time spent: {time_spent}")
LOGGER.info(f"Single time spent: {single_time_spent}")
LOGGER.info(f"Space utilization: {container.space_utilization}")
LOGGER.info(f"Theory space utilization: {theory_utilization}")
LOGGER.info(f"Score: {score}")
