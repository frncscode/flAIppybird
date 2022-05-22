from perlin_noise import PerlinNoise
import time

noise = PerlinNoise()


x = 0
while True:
    time.sleep(0.001)
    print(noise(x))
    x += 0.5