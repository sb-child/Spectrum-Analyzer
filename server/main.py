# Copyright 2023 sbchild

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0


import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import math
import socket

CHUNK_SIZE = 2048
SAMPLING_RATE = 44100

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(("192.168.0.123", 1234))

p = pyaudio.PyAudio()

for i in range(pyaudio.PyAudio().get_device_count()):
    if pyaudio.PyAudio().get_device_info_by_index(i)["maxInputChannels"] > 0:
        print(pyaudio.PyAudio().get_device_info_by_index(i))

stream = p.open(format=pyaudio.paFloat32, channels=2, rate=SAMPLING_RATE,
                input=True, input_device_index=8, frames_per_buffer=CHUNK_SIZE)

fig, (ax_left, ax_right) = plt.subplots(1, 2)

x = np.linspace(0, 16, 16)

line_left, = ax_left.plot(x, np.random.rand(16), lw=2)
line_right, = ax_right.plot(x, np.random.rand(16), lw=2)

ax_left.set_ylim(0, 8)
ax_left.set_xlim(0, 16)
ax_right.set_ylim(0, 8)
ax_left.set_xlim(0, 16)


ax_left.set_xlabel('Frequency (Hz)')
ax_left.set_ylabel('Magnitude')
ax_right.set_xlabel('Frequency (Hz)')
ax_right.set_ylabel('Magnitude')

fig.show()

left_spectrum_16 = np.zeros(16)
right_spectrum_16 = np.zeros(16)

left_spectrum_16_rt = np.zeros(16)
right_spectrum_16_rt = np.zeros(16)

ba = bytearray(64)

while True:
    data = stream.read(CHUNK_SIZE)

    data = np.frombuffer(data, dtype=np.float32)
    data = data / (2 ^ 32)

    left_channel = data[::2]
    right_channel = data[1::2]
    left_fft = np.fft.fft(left_channel)
    right_fft = np.fft.fft(right_channel)

    left_spectrum = np.abs(left_fft)[:CHUNK_SIZE//2]
    right_spectrum = np.abs(right_fft)[:CHUNK_SIZE//2]

    left_spectrum = (5.5*np.log10(left_spectrum)) + 5.5
    right_spectrum = (5.5*np.log10(right_spectrum)) + 5.5

    left_spectrum_16 *= 0.9
    right_spectrum_16 *= 0.9

    for i in range(16):
        freq_from = int((CHUNK_SIZE//2) *
                        (10 ** (i * 0.14375 + 1.7)) / (SAMPLING_RATE/2))
        freq_to = int((CHUNK_SIZE//2) *
                      (10 ** ((i + 1) * 0.14375 + 1.7)) / (SAMPLING_RATE/2))
        left_split = left_spectrum[freq_from:freq_to].max()
        left_split = 0 if math.isnan(
            left_split) or left_split < 0 else left_split
        left_split = 10 if math.isinf(
            left_split) or left_split > 10 else left_split
        left_split = left_split * 0.7
        left_spectrum_16[i] = left_split if left_split > left_spectrum_16[i] else left_spectrum_16[i]
        left_spectrum_16_rt[i] = left_split
        right_split = right_spectrum[freq_from:freq_to].max()
        right_split = 0 if math.isnan(
            right_split) or right_split < 0 else right_split
        right_split = 10 if math.isinf(
            right_split) or right_split > 10 else right_split
        right_split = right_split * 0.7
        right_spectrum_16[i] = right_split if right_split > right_spectrum_16[i] else right_spectrum_16[i]
        right_spectrum_16_rt[i] = right_split

    line_left.set_ydata(left_spectrum_16)
    line_right.set_ydata(right_spectrum_16)

    left_spectrum_16[left_spectrum_16 > 7] = 7
    right_spectrum_16[right_spectrum_16 > 7] = 7

    for i in range(32):
        if i < 16:
            ba[i] = int(left_spectrum_16[i])
        else:
            ba[i] = int(right_spectrum_16[i - 16])

    for i in range(32, 64):
        if i < 48:
            ba[i] = int(left_spectrum_16_rt[i - 32])
        else:
            ba[i] = int(right_spectrum_16_rt[(i - 32) - 16])

    try:
        sock.send(ba)
    except OSError:
        pass

    fig.canvas.draw()
    fig.canvas.flush_events()
