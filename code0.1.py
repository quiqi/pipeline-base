# 代码1：用opencv实现《镜子》程序
import cv2  # 导入opencv包

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)  # 获取摄像头，参数0表示本地第一个摄像头

    while True:                 # 不断从摄像头读取数据并显示
        ret, img = cap.read()       # 1. 从摄像头读取一帧图片
        img = cv2.flip(img, 1)      # 2. 将图片翻转
        cv2.imshow('test1', img)    # 3. 将图片显示到 ‘test1’ 窗口
        cv2.waitKey(1)  # 等待一个非常短的时间，让cv2.imshow有时间去绘制图像
