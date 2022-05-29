import os.path

from pipeline.core import *
import time
import pickle
import warnings


class Source(Worker):
    """
    源头类，用于产生带有序号和时间戳的frame
    """
    def __init__(self, name: str = '_SOURCE'):
        super().__init__(name)
        self.number = 0
        warnings.warn('This component will be deprecated!')

    def process(self, frame: Frame):
        frame.info['_TIME'] = time.time()
        frame.info['_NUMB'] = self.number
        self.number += 1
        return frame


class Save(Worker):
    """
    保存类，将数据流保存
    """
    def __init__(self, name: str = '_SAVE', save_path: str = None, time_lag: int = 60):
        super().__init__(name)
        if save_path is None:
            save_path = './output/'     # 默认保存在 ./output/ 文件夹中

        self.save_path = save_path      # 保存路径
        self.time_lag = time_lag * 60   # 分段间隔，默认为一小时

        self.save_info_path = os.path.join(self.save_path, 'save_info.txt')     # 索引文件地址
        self.plf_name = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime()) + '.plf'     # plf文件名字
        self.last_time = time.time()    # 当下时间

        # 如果保存地址不存在，需要递归生成
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        # 将当前文件名 self.plf_name 保存到save_info.txt中：
        with open(self.save_info_path, 'a') as f:
            f.write(self.plf_name + '\n')

    def process(self, frame: Frame):
        if time.time() - self.last_time > self.time_lag:    # 如果大于时间间隔
            self.last_time = time.time()    # 更新时间戳
            self.plf_name = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime()) + '.plf'    # plf文件名字
            # 将当前文件名 self.plf_name 保存到save_info.txt中：
            with open(self.save_info_path, 'a') as f:
                f.write(self.plf_name + '\n')

        bf = pickle.dumps(frame)
        with open(os.path.join(self.save_path, self.plf_name), 'a', encoding='utf-8') as f:
            f.write(str(bf) + '\n')
        return frame


class Load(Worker):
    """
    加载包
    """
    def __init__(self, name: str = '_LOAD', load_path: str = None, reappear: bool = False, start_from: str = None):
        super().__init__(name)

        # 默认从 ./output/中读取数据
        if load_path is None:
            load_path = './output/'
        self.load_path = load_path
        self.data_path = []
        self.close = False      # 关闭按钮
        self.data_path_p = 0    # 路径指针
        self.reappear = reappear    # 是否为复现模式
        self.base_time = None       # 基本时间
        self.start_time = None      # 起始时间

        # 当save_info文件找不到时
        if not os.path.exists(os.path.join(load_path, 'save_info.txt')):
            print('Unable to find file save_info.txt in directory {}, '
                  '{} will automatically shut down after sending end frame.'.format(load_path, self.name))
            self.close = True   # 关闭组件
        # 当可以找到 save_info时
        else:
            # 读取save_info
            with open(os.path.join(load_path, 'save_info.txt'), 'r') as f:
                line = f.readline()
                while line:
                    self.data_path.append(line[:-1])
                    line = f.readline()
            # 如果save_info.txt 中没有数据，则设置close为false
            if len(self.data_path) == 0:
                self.close = True
                print('can not find any file in save_info.txt, '
                      '{} will automatically shut down after sending end frame.'.format(self.name))
            else:
                # 如果规定了起点，则将数据流定位到起点
                if start_from is not None:
                    if start_from in self.data_path:
                        self.data_path_p = self.data_path.index(start_from)
                    else:
                        print('can not find the {}, by default, data is read from the earliest'.format(start_from))

                # 创建文件指针
                self.fp = self.get_fp()
                if self.fp is None:  # 如果文件指针为空
                    self.close = True
                    print('can not find any plf.'
                          '{} will automatically shut down after sending end frame.'.format(self.name))

    def process(self, frame: Frame):
        if self.close:  # 如果初始化失败，则关闭
            frame.ctrl.append('_CLOSE')
            return frame

        # 否则开始读取数据
        else:
            # 用read_frame读取一个帧
            t_frame = self.read_frame()
            if t_frame is None:     # 如果读取到空，表示读取完毕
                frame.ctrl.append('_CLOSE')     # 发送结束帧
                return frame
            # 若不为空帧，则给frame赋值
            frame = t_frame

            # 如果为复现模式，则进行时间控制
            if self.reappear:
                if self.base_time is None:
                    self.base_time = frame.info['_TIME']
                    self.start_time = time.time()
                else:
                    t1 = frame.info['_TIME'] - self.base_time   # 期望时间
                    t2 = time.time() - self.start_time          # 真实时间
                    if t1 > t2:     # 如果期望时间大于真实时间
                        time.sleep(t1-t2)
            return frame

    def read_frame(self):
        frame = None
        while frame is None:
            # 读取一行二进制
            line = self.fp.readline()
            if line:  # 如果读取成功
                try:  # 尝试反序列化 line 为一个帧
                    t_frame = pickle.loads(eval(line))
                    # 确定帧类型后将 t_frame 赋值给 frame
                    if isinstance(t_frame, Frame):
                        frame = t_frame
                        return frame
                except Exception as e:  # 差错处理
                    print(e)
                    print('The current frame fails to read and the next frame is automatically read')
            else:   # 如果读取失败
                self.fp = self.get_fp()
                if self.fp is None:
                    return None     # 返回None表示读取失败且没有找到新的文件

    def get_fp(self):
        fp = None  # 文件指针
        while self.data_path_p < len(self.data_path):
            t_path = os.path.join(self.load_path, self.data_path[self.data_path_p])
            if os.path.exists(t_path):
                fp = open(t_path, 'r')
                self.data_path_p += 1
                return fp   # 读取成功返回 fp
            else:
                print('can not find the plf:{}, the next plf will be read automatically'.format(t_path))
                self.data_path_p += 1  # 更新文件指针
        return fp


class PrintData(Worker):
    def __init__(self, name: str = 'print', contents: list = None):
        super().__init__(name)
        self.contents = contents

    def process(self, frame: Frame):
        if self.contents is None:
            print(frame.data)
        else:
            for content in self.contents:
                if content in frame.data.keys():
                    print('data[{}]:{}'.format(content, frame.data[content]))
                else:
                    print('can\'t find the key {} in data'.format(content))
        return frame
