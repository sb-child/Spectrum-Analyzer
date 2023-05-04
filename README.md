# ESP8266 Spectrum Analyzer

It just works.

## [<查看中文版 view Chinese version>](./README.zh-cn.md)

## Demo

<video controls>
  <source src="./demo/video_2023-05-03_15-26-10.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[click to watch](./demo/video_2023-05-03_15-26-10.mp4)

## Documentation

### how to use

1. install `platform-io`.
2. install `python` and `pyaudio`, `numpy`, `matplotlib` libraries.
3. modify the code to fit your wifi settings.
4. compile and upload firmware to `esp8266-12f`.
5. solder four MAX7219 8*8 led matrix modules:

```
ESP8266
    |
    V
[matrix 1]-DOUT > DIN-[matrix 2]-DOUT > DIN-[matrix 3]-DOUT > DIN-[matrix 4]
          -CS   >  CS-          -CS   >  CS-          -CS   >  CS-
          -CLK  > CLK-          -CLK  > CLK-          -CLK  > CLK-
          -VCC  > VCC-          -VCC  > VCC-          -VCC  > VCC-
          -GND  > GND-          -GND  > GND-          -GND  > GND-
<-----------L CHANNEL---------->            <-----------R CHANNEL---------->
HIGH FREQ               LOW FREQ            LOW FREQ               HIGH FREQ
```

6. connect the first module `VCC - 5V`, `GND - GND`, `DIN - D7`, `CS - D6`, `CLK - D5`.

> NOTE: Check whether VCC-GND is short-circuited before powering on.

7. Powering on, and run `server/main.py`.
8. if `server/main.py` crashed, please change `input_device_index` at line 29, or submit an issue.
9. run `pavucontrol`, on `record` tab, change the record device for `ALSA plug-in [python xx]: ALSA Capture`.
10. enjoy!

### audio server `server/main.py`

This code creates a real-time audio visualizer. It imports the necessary libraries, sets the chunk size and sampling rate, connects to a socket, and then finds the device index for the audio input. It then creates a plot with two axes, one for the left channel and one for the right channel. It then reads in the audio data from the stream, splits it into left and right channels, and performs a Fourier transform on each channel. It then takes the absolute value of the Fourier transform and applies a logarithmic scale to it. It then takes the maximum value from each frequency range and stores it in an array. It then sets the y-data for the plot to the array values, and sends the array values over the socket. Finally, it draws the plot and flushes the events.

1. imports the required libraries: `pyaudio`, `numpy`, `matplotlib`, `math`, and `socket`.
2. sets the  `CHUNK_SIZE`  and  `SAMPLING_RATE`  constants for reading audio data from the microphone.
3. creates a socket and connects to a specific IP address and port, which is used to send the audio data to another device.
4. creates an instance of the `pyaudio.PyAudio()` class and loops through all available audio input devices to find a suitable device for recording audio.
5. creates a plot with two axes, one for the left channel and one for the right channel, using the `matplotlib.pyplot.subplots()` method.
6. generates a sequence of 16 equally spaced numbers between 0 and 16 using the `numpy.linspace()` method, which is used as the x-axis data for the plot.
7. initializes two lines for the plot, one for the left channel and one for the right channel, each containing random y-axis data of length 16.
8. sets the limits and labels for the x- and y-axes of each subplot.
9. displays the plot using the `matplotlib.pyplot.show()` method.
10. initializes four arrays of length 16, which store the maximum values of the audio data in specific frequency ranges.
11. initializes a `bytearray` of length 64, which is used to send the audio data over the socket.
12. enters a loop that repeatedly reads a chunk of audio data from the microphone using the `stream.read(CHUNK_SIZE)` method.
13. converts the audio data to a numpy array of 32-bit floating point data.
14. divides the audio data into two channels, one for the left channel and one for the right channel.
15. performs a Fast Fourier Transform (FFT) on each channel to convert the audio data from the time domain to the frequency domain.
16. takes the absolute value of the FFT results and applies a logarithmic scale to them using the `numpy.log10()` method.
17. finds the maximum value in each of 16 frequency ranges for both the left and right channels, and stores them in separate arrays.
18. updates the y-axis data for the plot with the maximum values stored in the arrays.
19. caps the maximum value of each array at 7 using a thresholding mechanism.
20. stores the maximum values in the arrays, as well as the unfiltered maximum values, in the `bytearray`.
21. sends the `bytearray` over the socket.
22. redraws the plot and flushes any events using the `matplotlib.pyplot.draw()` and `matplotlib.pyplot.flush_events()` methods.

This process is repeated continuously in a loop, resulting in a real-time audio visualizer that displays the amplitude of specific frequency ranges in the audio data being recorded. The visualizer also sends this data to another device over a socket connection.

### display `src/main.cpp`

This code sets up a connection to a WiFi network, and then listens for UDP packets on port 1234. When it receives a packet, it draws a graph of the data on a display.  

1. The code includes the necessary libraries for connecting to a WiFi network, using SPI and I2C, and for displaying data on a display.  
2. It defines the SSID and password of the WiFi network to connect to.  
3. It sets up the static IP, gateway, subnet, and DNS for the connection.  
4. It initializes the display.  
5. In the `setup()` function, it starts the serial connection, initializes the display, connects to the WiFi network, and begins listening for UDP packets on port 1234.  
6. In the `loop()` function, it checks if there is a UDP packet available.  
7. If there is, it reads the packet into a buffer, checks that the packet size is 64 bytes, and then draws a graph of the data on the display.
