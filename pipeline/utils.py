import os.path

from pipeline.core import *
import time
import pickle


class Source(Worker):
    """
    源头类，用于产生带有序号和时间戳的frame
    """
    def __init__(self, name: str = '_SOURCE'):
        super().__init__(name)
        self.number = 0

    def process(self, frame: Frame):
        frame.info['_TIME'] = time.time()
        frame.info['_NUMB'] = self.number
        frame.info['_PLOT'] = {}
        self.number += 1
        return frame


class Save(Worker):
    """
    保存类，将数据流保存
    """
    def __init__(self, name: str = '_SAVE', save_path: str = None):
        super().__init__(name)
        if save_path is None:
            save_path = './output/'
        self.save_path = save_path
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        self.save_info_path = os.path.join(self.save_path, 'save_info.txt')
        if os.path.exists(self.save_info_path):
            os.remove(self.save_info_path)

    def process(self, frame: Frame):
        pkl_name = '{}.pkl'.format(frame.info['_NUMB'])
        path = os.path.join(self.save_path, pkl_name)
        suffix = 1
        while True:
            if os.path.exists(path):
                pkl_name = '{}_{}.pkl'.format(frame.info['_NUMB'], suffix)
                path = os.path.join(self.save_path, pkl_name)
                suffix += 1
            else:
                break

        with open(path, 'wb') as f:
            pickle.dump(frame, f)

        with open(self.save_info_path, 'a') as f:
            f.write(pkl_name + '\n')
        return frame


class Load(Worker):
    """
    加载包
    """
    def __init__(self, name: str = '_LOAD', load_path: str = None, reappear: bool = False):
        super().__init__(name)
        if load_path is None:
            load_path = './output/'
        self.load_path = load_path
        self.data_path = []
        self.close = False
        self.data_path_p = 0
        self.reappear = reappear
        self.base_time = None
        self.start_time = None
        if not os.path.exists(os.path.join(load_path, 'save_info.txt')):
            print('Unable to find file save_info.txt in directory {}, '
                  '{} will automatically shut down after sending end frame.'.format(load_path, self.name))
            self.close = True
        else:
            with open(os.path.join(load_path, 'save_info.txt'), 'r') as f:
                line = f.readline()
                while line:
                    self.data_path.append(line[:-1])
                    line = f.readline()

    def process(self, frame: Frame):
        if self.close:
            frame.ctrl.append('_CLOSE')
            return frame
        else:
            if self.data_path_p <= len(self.data_path) - 1:
                dp = self.data_path[self.data_path_p]
                if not os.path.exists(os.path.join(self.load_path, dp)):
                    print('没有找到名为：{}文件'.format(dp))
                with open(os.path.join(self.load_path, dp), 'rb') as f:
                    frame = pickle.load(f)
                if self.data_path_p == len(self.data_path) - 1:
                    frame.ctrl.append('_CLOSE')
                self.data_path_p += 1
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
