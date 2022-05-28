import cv2
from pipeline.core import *
import pipeline.utils as utils


class ReadCamera(Worker):
    def __init__(self, name: str = 'camera', url: str = 0):
        super().__init__(name)
        self.camera = cv2.VideoCapture(url)

    def process(self, frame: Frame):
        ret, img = self.camera.read()
        frame.data['img'] = img
        return frame


class Flip(Worker):
    def __init__(self, name: str = 'flip'):
        super().__init__(name)

    def process(self, frame: Frame):
        frame.data['img'] = cv2.flip(frame.data['img'], 1)
        return frame


class ChalkEffects(Worker):
    def __init__(self, name: str = 'chalk_effects'):
        super().__init__(name)

    def process(self, frame: Frame):
        img = cv2.cvtColor(frame.data['img'], cv2.COLOR_BGR2GRAY)
        img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 5, 3)
        frame.data['img'] = cv2.bitwise_not(img)
        return frame


class ShowImg(Worker):
    def __init__(self, name: str = 'show_img'):
        super().__init__(name)

    def process(self, frame: Frame):
        cv2.imshow(self.name, frame.data['img'])
        cv2.waitKey(1)
        return frame


if __name__ == '__main__':

    mirror = NodeSet([
        # 使用官方工具包中的 Source 组件作为起始组件
        Node('node0', subsequents=['node1'], worker=utils.Source()),
        Node('node1', subsequents=['node2'], worker=ReadCamera()),
        Node('node2', subsequents=['node3', 'node5'], worker=Flip()),
        Node('node3', subsequents=['node4'], worker=ChalkEffects()),
        Node('node4', worker=ShowImg()),
        # 使用官方工具包中的 Save 组件保存数据流
        Node('node5', worker=utils.Save(save_path='./output/')),
    ])

    while mirror.switch:
        fs = mirror.run(Frame(end='node0'))
