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

    mirror = WorkerSet('mirror', [
        ReadCamera(),
        Flip(),
        ChalkEffects(),
        ShowImg()
    ])

    while mirror.switch:
        # 默认从列表的第一个组件开始运行，不需要指定起始节点
        fs = mirror.run(Frame())
