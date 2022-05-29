import time
import pickle
import pipeline.core as core

if __name__ == '__main__':
    f = core.Frame()
    bf = pickle.dumps(f)
    l = pickle.dumps(len(bf))
    with open('a.plf', 'wb') as f:
        f.write(l)
        c = len(l)
        f.write(bf)
    with open('a.plf', 'rb') as f:
        bf1 = f.read(c)
        i = pickle.loads(bf1)
        bf2 = f.read(i)
    f1 = pickle.loads(bf2)
    print(f1)
