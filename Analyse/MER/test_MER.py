import numpy as np
from random import randint
import matplotlib.pyplot as plt

### Signal test
trace = [randint(-500,500) for i in range(1000)]
trace.extend([randint(-2048,2048)*np.sin(i) for i in range(500)])
trace.extend([randint(-500,500) for i in range(1000)])

def MER(signal, ne=40):
    b = np.full(ne, np.mean(signal[1 : 2]))
    a = np.full(ne, np.mean(signal[-2 : -1]))
    msignal = np.concatenate((b, signal, a))
    carre = np.square(msignal)
    res = []

    for i in range(1+ne, len(signal)+ne-1):
        num = sum(carre[i : i+ne])
        deno = sum(carre[i-ne : i])
        ratio = num/deno
        mer_i = (np.abs(msignal[i])*ratio)**3
        res.append(mer_i)
    
    return res

def detection_MER(mer, seuil):
    t=0
    while mer[t] < seuil:
        t+=1
    return t

### Test
Mer = MER(trace)
print(detection_MER(Mer, np.max(Mer)/2))

### Affichage
plt.figure()
plt.subplot(2,1,1)
plt.plot(trace, color='r')
plt.subplot(2,1,2)
plt.plot(Mer, color='b')
plt.show()