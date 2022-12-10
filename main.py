from Common import *
import utils

from Bin import Bin 
from Container import Container


# container = Container(20,10,10)
# bins = utils.generate.generate_bins(10, container)

data_path = r"D:\OneDrive\Projects\Coding\Python\Fun\3D_Bin_Packing\test_data.txt"
container, bins = utils.data_utils.read_task(data_path, 3)
axises_rotate = (Axis.WIDTH, Axis.HEIGHT, Axis.LENGTH)
axises_put = (Axis.LENGTH, Axis.HEIGHT, Axis.WIDTH)
logger.info(f"Container: {container}")

for single_bin in bins:
    # logger.info(f"Original bin: {single_bin}")
    single_bin.axis_sort(axises_rotate)
    logger.info(f"Putting bin: {single_bin}")
    # logger.info(f"Bin axis: {utils.axis_utils.lwh_to_axis([single_bin.length, single_bin.width, single_bin.height], axises_put)}")
    bin_place = container.greedy_find_with_heuristics(single_bin, axises_put, True, True)
    logger.info(f"Bin placed at {bin_place}")    
    logger.info("Utilization: {0:.3f}".format(container.space_utilization))
    # container.print_2D_slice(Axis.HEIGHT,0,True)
