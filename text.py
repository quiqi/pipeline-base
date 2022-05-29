import time
import pickle
import pipeline.core as core

if __name__ == '__main__':
    f = core.Frame()
    bf = pickle.dumps(f)
    with open('a.plf', 'w') as f:
        f.write(str(bf))
        f.write('\n')
        f.write(str(bf))
    with open('a.plf', 'r') as f:
        bf1 = f.readline()
        bf2 = f.readline()
    f1 = pickle.loads(eval(bf1))
    print(f1)
