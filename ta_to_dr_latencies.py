import numpy as np
from matplotlib import pyplot as plt

def get_value_from_line(_line, _text):
    """
    Gets a value from the entire line passed as a string. E.g:
    "version_number: 2" would return 2 if we provide "version_number:"
    in the _line parameter.
    :param _line: Entire line of text, passed as a string.
    :param _text: The value identifier - E.g. "version_number:"
    :return: Value found, as an integer.
    """
    location = _line.find(_text)
    ret = _line[location:]
    ret = ret.replace(_text + " ", "")
    ret = ret.split(" ")
    ret = int(ret[0])
    return int(ret)


def get_list_of_latencies(td_dts, td_sts, tp_dts, tp_sts):
    """
    This function is going to return a list of latency times corresponding to
    the subtraction of TD leaving MLT system time (a) and the corresponding TP entering
    the trigger app system time (b). (a) - (b) should give latency measurement (1) for
    DUNE DAQ team.
    td_dts :param td_times: The list of TD timestamps, corresponding to the window start
                     which should be the TP time for Prescale trigger only!
    td_sts :param TD System Times
    tp_dts :param TP Data times: The list of TP data start times, to match up with the TD times.
    tp_sts :param TP System times.
    :return: latencies: A list of latency measurements in seconds.
    """
    latencies = []
    td_systimes = []

    for i, td_dt in enumerate(td_dts):
        for j, tp_dt in enumerate(tp_dts):
            if td_dt == tp_dt:
                latency = (td_sts[i] - tp_sts[j]) * 1e-9
                latencies.append(latency)
                td_systimes.append(td_sts[i])

    tp_systemtime = [tp - tp_sts[0] for tp in tp_sts]   # Shift to relative times
    tp_systemtime = [ tp*1e-9 for tp in tp_systemtime ] # Convert to seconds from nanoseconds
    tp_datatime   = [ tp - tp_dts[0] for tp in tp_dts]  # Shift to relative times
    tp_datatime   = [ tp*16e-9 for tp in tp_datatime ]  # Convert to seconds from 62.5 MHz ticks

    tp_d_vs_sys = []
    if len(tp_systemtime) != len(tp_datatime):
        print("Error! Number of TP datas don't match! ")
    else:
        for i in range(len(tp_systemtime)):
            d = abs(tp_systemtime[i] - tp_datatime[i])
            tp_d_vs_sys.append(d)

    print("Collected ", len(latencies), " latency measurements of form TA Arrival to Buffer -> Data Request Arrival for TA.")
    print("Collected ", len(tp_d_vs_sys), " measurements of datatime vs system time.")
    return latencies, td_systimes, tp_d_vs_sys, tp_systemtime


def get_latencies(_file, _output):

    # Get a set of inserted TP data from the log file.
    print("Opening and extracting meaningful info from log file...")
    log_file = open(_file)
    data = log_file.readlines()
    log_file.close()

    ta_dt = []
    ta_st = []
    dr_dt = []
    dr_st = []

    td_lat = []
    td_ts = []

    run_number = 1

    for line in data:
        if "Start of run" in line:
            location = line.find("Start of run")
            line = (line[location:])
            run_number = get_value_from_line(line, "Start of run")
        if "Got TA at the TABuffer" in line:
            location = line.find("Got TA at the TABuffer")
            line = (line[location:])
            ta_dt.append(get_value_from_line(line, "datatime is:"))
            ta_st.append(get_value_from_line(line, "and system time is:"))
        if "Got TA data request" in line:
            location = line.find("Got TA data request")
            line = (line[location:])
            dr_dt.append(get_value_from_line(line, "datatime starting:"))
            td_ts.append(get_value_from_line(line, "system time is:"))

    print("Got a set of ", len(ta_st), " TAs data and ", len(dr_st), " sent data_request data.")
    latencies, dr_systime, ta_data_vs_sys, ta_systemtime = get_list_of_latencies(dr_dt, dr_st, ta_dt, ta_st)
    return latencies, dr_systime, ta_data_vs_sys, ta_systemtime, run_number

def measure_tardy_tpset_latencies(_file):

    print("Opening and extracting meaningful info from log file...")
    log_file = open(_file)
    data = log_file.readlines()
    log_file.close()
    latencies = []

    for line in data:
        if "Start of run" in line:
            location = line.find("Start of run")
            line = (line[location:])
            run_number = get_value_from_line(line, "Start of run")
        if "Set start time" in line:
            location = line.find("Set start time")
            line = (line[location:])
            tpset_start = get_value_from_line(line, "Set start time")
            last_sent_time = get_value_from_line(line, "last sent time")
            latencies.append(last_sent_time - tpset_start)

    latencies = [l*16e-9 for l in latencies]
    print("Got list of TA->DR latencies.")
    return latencies, run_number


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sterilize DAQ log to get the latency timestamps")
    parser.add_argument('-f' '--file',   dest='file',     help='DAQ log file input')
    parser.add_argument('-o' '--output', dest='output',   default='', help='Plot output')

    args = parser.parse_args()
    latencies, dr_systimes, ta_d_v_s, ta_sys, run_number = get_latencies(args.file, args.output)
    print("Finished processing run ", run_number)

    # Setup subplots
    title = "Trigger System TA -> DR Latency Measurement - Run No. " + str(run_number)
    fig = plt.subplot(111)
    fig.set_xlabel(r"TA Buffer Insertion $\rightarrow$ Data Request (seconds)", fontweight="bold")
    fig.set_ylabel("Relative Frequency", fontweight="bold")
    fig.set_title(title, fontweight="bold")
    fig.hist(latencies, bins=75)
    fig.grid('both')

    fig_name = "saved_plots/ta_to_dr_latencies_run_" + str(run_number) + ".png"
    plt.savefig(fig_name)
    # Clear figure
    plt.clf()

    title = "Trigger System TA -> DR Latency Measurement - Run No. " + str(run_number)
    fig = plt.subplot(111)
    fig.set_xlabel("Relative System Time (s)", fontweight="bold")
    fig.set_ylabel(r"TA Buffer Inception $\rightarrow$ Data Request (s)", fontweight="bold")
    fig.set_title(title, fontweight="bold")
    fig.plot(dr_systimes, latencies)
    fig.grid('both')

    fig_name = "saved_plots/ta_to_dr_latencies_vs_run_time_" + str(run_number) + ".png"
    plt.savefig(fig_name)
    plt.clf()

    title = "TA System Time - TA Data Time - Run No. " + str(run_number)
    fig = plt.subplot(111)
    fig.set_xlabel("Relative TA System Time (s)", fontweight="bold")
    fig.set_ylabel("TA System Time - TA Data Time (s)", fontweight="bold")
    fig.set_title(title, fontweight="bold")
    fig.plot(ta_sys, ta_d_v_s)   # Ignore the first few TPs, might be flushing from previous run.
    fig.grid('both')
    # plt.show()

    fig_name = "saved_plots/datatime_vs_system_time_TAs_" + str(run_number) + ".png"
    plt.savefig(fig_name)
    plt.clf()

    tpset_lateness, run_number = measure_tardy_tpset_latencies(args.file)
    title = "TPSet Lateness Distribution - Run No. " + str(run_number)
    fig = plt.subplot(111)
    fig.set_xlabel("TPSet Latency - Seconds", fontweight="bold")
    fig.set_ylabel("Frequency", fontweight="bold")
    fig.set_title(title, fontweight="bold")
    fig.hist(tpset_lateness[20:], bins=20)   # Ignore the first few TPs, might be flushing from previous run.
    fig.grid('both')

    fig_name = "saved_plots/tpset_tardy_lateness_distribution_" + str(run_number) + ".png"
    plt.savefig(fig_name)
    plt.clf()







