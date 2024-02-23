import time
from adafruit_circuitplayground import cp

cp.pixels[0] = (0, 255, 0) # LED's 0 and 1 shine into your finger
cp.pixels[1] = (0, 255, 0)

NUM_OVERSAMPLE = 10 # How many light readings per sample
NUM_SAMPLES = 20 # How many samples we take to calculate 'average'
samples = [0] * NUM_SAMPLES

while True:
    for i in range(NUM_SAMPLES):
        oversample = 0
        for s in range(NUM_OVERSAMPLE):
            oversample += float(cp.light)
        samples[i] = oversample / NUM_OVERSAMPLE
        mean = sum(samples) / float(len(samples))   
        print((samples[i] - mean,))
        # Pulse LED #9 when sign changes
        if i > 0:
            if (samples[i]-mean) <= 0 and (samples[i-1]-mean) > 0:
                cp.pixels[9] = (20, 0, 0)
        else:
                cp.pixels[9] = (0, 0, 0)
        time.sleep(0.025)