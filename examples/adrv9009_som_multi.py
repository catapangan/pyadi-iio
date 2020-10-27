# type: ignore

import csv
import time

import adi
import matplotlib.pyplot as plt
import numpy as np
import scipy.io as sio
from scipy import signal


def measure_phase_and_delay(chan0, chan1, window=None):
    assert len(chan0) == len(chan1)
    if window == None:
        window = len(chan0)
    phases = []
    delays = []
    indx = 0
    sections = len(chan0) // window
    for sec in range(sections):
        chan0_tmp = chan0[indx : indx + window]
        chan1_tmp = chan1[indx : indx + window]
        indx = indx + window + 1
        cor = np.correlate(chan0_tmp, chan1_tmp, "full")
        # plt.plot(np.real(cor))
        # plt.plot(np.imag(cor))
        # plt.plot(np.abs(cor))
        # plt.show()
        i = np.argmax(np.abs(cor))
        m = cor[i]
        sample_delay = len(chan0_tmp) - i - 1
        phases.append(np.angle(m) * 180 / np.pi)
        delays.append(sample_delay)
    return (np.mean(phases), np.mean(delays))


def measure_phase(chan0, chan1):
    assert len(chan0) == len(chan1)
    errorV = np.angle(chan0 * np.conj(chan1)) * 180 / np.pi
    error = np.mean(errorV)
    return error


buff_size = 2 ** 14

# Create radio
primary = "ip:10.44.3.39"
secondary = "ip:10.44.3.38"

lo_freq = 1000000000
dds_freq = 1234567

primary_jesd = adi.jesd(primary)
secondary_jesd = adi.jesd(secondary)

print("--Connecting to devices")
multi = adi.adrv9009_zu11eg_multi(
    primary, [secondary], primary_jesd, [secondary_jesd], fmcomms8=True
)

multi._dma_show_arming = False
multi._jesd_show_status = True
multi.rx_buffer_size = 2 ** 10

multi.primary.rx_enabled_channels = [0, 2, 4, 6]

for secondary in multi.secondaries:
    secondary.rx_enabled_channels = [0, 2, 4, 6]

multi.set_trx_lo_frequency(999999990)
multi.primary.dds_single_tone(dds_freq, 0.8)

log = [[], [], [], [], []]

N = 8
C = 5
R = 32

plot_time = True

rx = np.zeros([C, N])
rx_m = np.zeros([C, R])
rx_v = np.zeros([C, R])

chan_desc = [
    "Across Chip (A)",
    "Across FMC8 (A)",
    "Across Chip (B)",
    "Across FMC8 (B)",
    "Across SoM (AB)",
]

for r in range(R):
    print("Pulling buffers")
    multi._rx_initialized = False

    # [0, 2, 4, 6][0, 2, 4, 6]
    # [0, 1, 2 ,3, 4, 5, 6, 7]
    for i in range(N):
        x = multi.rx()
        rx[0][i] = measure_phase(x[0], x[1])
        rx[1][i] = measure_phase(x[0], x[2])
        rx[2][i] = measure_phase(x[4], x[5])
        rx[3][i] = measure_phase(x[4], x[6])
        rx[4][i] = measure_phase(x[0], x[4])

    for i in range(C):
        rx_m[i][r] = np.mean(rx[i])
        rx_v[i][r] = np.var(rx[i])
        if rx_v[i][r] > 10:
            plot_time = True
        else:
            plot_time = False

        log[i].append(rx_m[i])

    print("###########")
    for i in range(C):
        print("%s:\t %f" % (chan_desc[i], rx_m[i][r]))
    print("###########")

    if plot_time:
        plt.clf()
        plt.plot(x[0][:1000], label="Chan0 SOM A")
        plt.plot(x[1][:1000], label="Chan2 SOM A")
        plt.plot(x[2][:1000], label="Chan4 SOM A FMC8")
        plt.plot(x[4][:1000], label="Chan0 SOM B")
        plt.plot(x[6][:1000], label="Chan4 SOM B FMC8")
        plt.legend()
        plt.draw()
        plt.pause(5)

    plt.clf()
    x = np.array(range(0, r + 1))

    for i in range(C):
        plt.errorbar(x, rx_m[i][x], yerr=rx_v[i][x], label=chan_desc[i])

    plt.xlim([-1, x[-1] + 1])
    plt.xlabel("Measurement Index")
    plt.ylabel("Phase Difference (Degrees)")
    plt.legend()
    plt.draw()
    plt.pause(0.1)

print(log)
fields = []
for i in range(C):
    fields.append(np.sum(log[i]) / len(log[i]))
    fields.append(np.min(log[i]))
    fields.append(np.max(log[i]))
with open(r'log.csv', 'a') as f:
    writer = csv.writer(f)
    writer.writerow(fields)
plt.show(block=False)
plt.pause(2)
plt.close()
