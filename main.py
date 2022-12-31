from Common import *
import utils

from Bin import Bin 
from Container import Container

# container = Container(20,10,10)
# bins = utils.generate.generate_bins(10, container)

data_path = r"D:\OneDrive\Projects\Coding\Python\Fun\3D_Bin_Packing\test_data.txt"
container, bins = utils.data_utils.read_task(data_path, 3, 3) # 这里读取数据，两个数字分别是箱子的种类和选取的index，index从1开始
axises_rotate = (Axis.LENGTH, Axis.WIDTH, Axis.HEIGHT)
axises_put = (Axis.WIDTH, Axis.LENGTH, Axis.HEIGHT)
logger.info(f"Container: {container}")

start_time = time.time()
bins_volumn_sum = 0
for single_bin in bins:
    bins_volumn_sum += single_bin.volume
    single_bin.axis_sort(axises_rotate)
    logger.info(f"Putting bin: {single_bin}")
    # bin_place = container.brute_find_part(single_bin, axises_rotate, axises_put, (0,0,0), 3) # 这是第一种方法，暴力搜索
    # bin_place = container.brute_find_with_heuristics(single_bin, axises_rotate, axises_put, True, 3) # 这是第二种方法，候选点搜索
    bin_place = container.greedy_search(single_bin, axises_rotate, axises_put, 1) # 这是第三种方法，贪心算法
    # bin_place = container.sub_space_find(single_bin, axises_rotate, axises_put, 1) # 这是第四种方法，子空间搜索
    container.update_history(single_bin, bin_place)
    logger.info(f"Bin placed at {bin_place}")    
    logger.info("Utilization: {0:.3f}".format(container.space_utilization))
    # container.print_2D_slice(Axis.HEIGHT,0,True)
end_time = time.time()
time_spent = end_time - start_time
single_time_spent = time_spent / len(bins)
theory_utilization = min(bins_volumn_sum / container.volumn, 1)
score = container.space_utilization / theory_utilization
logger.info(f"Time spent: {time_spent}")
logger.info(f"Single time spent: {single_time_spent}")
logger.info(f"Space utilization: {container.space_utilization}")
logger.info(f"Theory space utilization: {theory_utilization}")
logger.info(f"Score: {score}")
