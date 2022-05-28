import cv2
from pipeline.core import *
import pipeline.utils as utils


class ShowImg(Worker):
    def __init__(self, name: str = 'show_img'):
        super().__init__(name)

    def process(self, frame: Frame):
        cv2.imshow(self.name, frame.data['img'])
        cv2.waitKey(1)
        return frame


if __name__ == '__main__':
    mirror = NodeSet([
        # 使用官方工具包中的 Load 组件读取'./output/'中的数据
        Node('node1', subsequents=['node2'], worker=utils.Load(load_path='./output/', reappear=True)),
        Node('node2', worker=ShowImg()),
    ])

    while mirror.switch:
        mirror.run(Frame(end='node1'))
