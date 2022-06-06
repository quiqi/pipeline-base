from pipeline.utils import *
from cv_example import *


if __name__ == '__main__':
    mirror = [
        Node('head', subsequents=['node1']),
        Node('node1', subsequents=['node2'], worker=TCPClient()),
        Node('node2', worker=ShowImg())
    ]

    while True:
        NodeSet(mirror).run(Frame(end='head'))




