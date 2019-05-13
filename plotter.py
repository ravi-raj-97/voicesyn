import matplotlib.pyplot as plt
import wave
import numpy as np

spf = wave.open('daveid.wav','r')
signal = spf.readframes(-1)
signal = np.fromstring(signal, 'Int16')

spf1 = wave.open('dave/dave3.wav','r')
signal1 = spf1.readframes(-1)
signal1 = np.fromstring(signal1, 'Int16')


plt.figure(1)
plt.title('two Signal Waves...')
plt.plot(signal,'r')
plt.plot(signal1,'b')
plt.legend()
plt.show()
