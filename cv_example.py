import cv2
from pipeline.utils import *
import pipeline


class ReadCamera(Worker):
    """
    从摄像头读取图片
    """

    def __init__(self, name: str = 'camera', url: str = 0):
        super().__init__(name)
        self.url = url
        self.camera = None

    def process(self, frame: Frame):
        if self.camera is None:
            self.camera = cv2.VideoCapture(self.url)
        # frame就是流经该组件的帧对象
        ret, img = self.camera.read()
        # 将读取到的图片放入 frame.data 的 'img' 的关键字下
        frame.data['img'] = img
        # 返回修改后的帧
        return frame


class Flip(Worker):
    """
    将图片翻转
    """

    def __init__(self, name: str = 'flip'):
        super().__init__(name)

    def process(self, frame: Frame):
        # 从 frame.data 的 'img' 的关键字下获得上游传来的图片，并翻转后放回
        frame.data['img'] = cv2.flip(frame.data['img'], 1)
        # 返回修改后的帧
        return frame


class ShowImg(Worker):
    """
    显示图片
    """

    def __init__(self, name: str = 'show_img'):
        super().__init__(name)

    def process(self, frame: Frame):
        # 显示 frame.data 的 'img' 的关键字下的帧
        cv2.imshow(self.name, frame.data['img'])
        cv2.waitKey(1)
        # 返回帧
        return frame


# code 2.6+ 实现粉笔画效果的Worker子类
class ChalkEffects(Worker):
    """
    粉笔画效果
    """
    def __init__(self, name: str = 'chalk_effects'):
        super().__init__(name)

    def process(self, frame: Frame):
        # 将图片灰度化
        img = cv2.cvtColor(frame.data['img'], cv2.COLOR_BGR2GRAY)
        # 自适应二值化
        img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                    cv2.THRESH_BINARY, 5, 3)
        # 对二值化图像取反最终得到粉笔画效果
        frame.data['img'] = cv2.bitwise_not(img)
        # 返回修改后的帧
        return frame
