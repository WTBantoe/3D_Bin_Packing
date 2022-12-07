import utils
from Bin import Bin 
from Container import Container
from Common import Axis

# container = Container(20,10,10)
# bins = utils.generate.generate_bins(10, container)

data_path = r"D:\OneDrive\Projects\Coding\Python\Fun\3D_Bin_Packing\test_data.txt"
container, bins = utils.data_utils.read_task(data_path, 3)
axises_rotate = (Axis.LENGTH, Axis.WIDTH, Axis.HEIGHT)
axises_put = (Axis.LENGTH, Axis.WIDTH, Axis.HEIGHT)
print(container)
for single_bin in bins:
    # print(single_bin)
    single_bin.axis_sort(axises_rotate)
    print(single_bin)
    # print(utils.axis_utils.lwh_to_axis([single_bin.length, single_bin.width, single_bin.height], axises_put))
    bin_place = container.greedy_find_with_heuristics(single_bin, axises_put)
    print(bin_place)    
    print("Utilization: {0:.3f}".format(container.space_utilization))
    # container.print_2D_slice(Axis.HEIGHT,0,True)
