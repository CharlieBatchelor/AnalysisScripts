from matplotlib import pyplot as plt
import numpy as np

data = np.genfromtxt('/Users/s2112263/dunedaq_debugging/vdcb_debugging/apa3_logs/tps/sample50k.txt', delimiter=' ')
data = data.transpose()

# chan map = lin_no, source_id, crate, slot, link, felix_card, felix_slr, felix_link, wire, offlinechannel
# chan_map = np.genfromtxt('VDColdboxChannelMap_lut.csv', delimiter=',')
# chan_map = chan_map.transpose()
#
# map_channels = chan_map[9][:n]
# map_sids = chan_map[0][:n]

fig = plt.subplot(111)
legend_properties = {'weight': 'bold'}

n=50000
startTime = data[0][:n]
time_shift = startTime[0]
channel = data[3][:n]
# adc = data[4][:n]
startTime -= time_shift
startTime *= 16e-9

label="Input TPs - Event Display"
# label="Input TPs - Histogram"
fig.set_xlabel("Relative Time (s)")
fig.set_ylabel("Channel ID")
fig.set_title("APA3 Run 19915: 12 Links SW TPG TPs", fontweight='bold')
# fig.set_title("VDCB Run: 12 Links SW TPG - Noisy Channel Filtered TPs", fontweight='bold')

fig.scatter(channel, startTime, s=2, label=label)
fig.legend(prop=legend_properties)
# # # fig.set_ylim(2624, 3200)
# # # fig.set_xlim(0, 400)
#
plt.show()