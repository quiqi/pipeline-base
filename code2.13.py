# 网络编程

from cv_example import *
from pipeline.core import *
from pipeline.mul import *
from pipeline.utils import *

if __name__ == '__main__':
    mirror = [
        Node('head', subsequents=['node1']),
        Node('node1', subsequents=['node2'], worker=ReadCamera()),
        Node('node2', subsequents=['node4'], worker=Flip()),  # 修改node2的后继
        Node('node4', subsequents=['node3'], worker=ChalkEffects()),
        Node('node3', subsequents=['node5'], worker=ShowImg()),
        Node('node5', worker=TCPServer())
    ]

    while True:
        NodeSet(mirror).run(Frame(end='head'))
