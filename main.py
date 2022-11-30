import utils
from Bin import Bin 
from Container import Container
from Common import Axis

container = Container(20,10,10)
bins = utils.generate.generate_bins(10, container)
for single_bin in bins:
    print(single_bin)
    print(container.greedy_find(single_bin,(Axis.HEIGHT, Axis.LENGTH, Axis.WIDTH)))
    print("Utilization: {0:.3f}".format(container.space_utilization))
    container.print_2D_slice(Axis.HEIGHT,0,True)


