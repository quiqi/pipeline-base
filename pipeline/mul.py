import multiprocessing
import multiprocessing.queues
import time
import typing
from typing import Optional

from sympy.parsing.sympy_parser import _T

import pipeline.core
import pipeline.utils


class MulSource(pipeline.core.Worker):
    def __init__(self):
        super().__init__(name='_MulSource')

    def after_process(self, frame: pipeline.core.Frame):
        """
        用于阻塞进程
        :param frame:
        :return:
        """
        return frame


class MulIgnition:
    def __init__(self, dots: typing.List[pipeline.core.Node], queue_size: int = 10):
        if len(dots) == 0:
            raise Exception('Please include at least one dot in nodes')

        self.pipes = {}
        self.process_list = {}
        self.source = []
        self.queue_size = queue_size

        # 初始化管道
        for dot in dots:
            if dot.name in ['_SOURCE', '_OUTPUT']:  # dot 不可以以 '_SOURCE' 命名
                raise Exception('The dot can not named as "_SOURCE"! Please changing the name.')
            if dot.name not in self.pipes.keys():
                self.pipes[dot.name] = multiprocessing.Queue(queue_size)  # 为当前进程建立管道

                # 如果该进程为源头进程
                if dot.source is not None:  # 如果该dot是源头dot，则
                    if dot.source == dot.name:  # 如果dot名和起始节点同名，则将节点名加入 source 列表中
                        self.source.append(dot.name)
                    else:  # 否则将多级路径加入 source 列表中
                        self.source.append('{}/{}'.format(dot.name, dot.source))
            else:
                raise Exception('Two processes with the same name appear: {}.'
                                'Processes cannot have the same name'.format(dot.name))
        self.pipes['_OUTPUT'] = multiprocessing.Queue(queue_size)
        self.pipes['_INPUT'] = multiprocessing.Queue(queue_size)
        if len(self.source) == 0:
            self.source.append(dots[0].name)
        # 加入源头进程，一切的数据包都来源于源头进程
        source_dot = pipeline.core.Node('_SOURCE', subsequents=self.source, worker=MulSource())
        p = MulIgnition.MulDot(source_dot, self.pipes)
        # p.start()
        self.process_list['_SOURCE'] = p

        # 初始化进程
        for dot in dots:
            p = MulIgnition.MulDot(dot, self.pipes)
            # p.start()
            self.process_list[dot.name] = p  # 为当前进程创造进程对象

    def run(self):
        for process in self.process_list:
            self.process_list[process].start()
        self.api()

    def api(self):
        time.sleep(2)
        while True:
            order = input('>> ').split(' ')
            if len(order) == 1:
                if order[0] == 'show':
                    for p in self.pipes:
                        print('\t{}:{}/{}'.format(p, self.pipes[p].qsize(), self.queue_size))
            elif len(order) >= 2:
                order_rout = '_SOURCE/' + order[0]
                order_head = order[1]
                order_args = order[2:]
                order_frame = pipeline.core.OrderFrame(order_head, order_args, '_INPUT', order_rout)
                self.pipes['_INPUT'].put(order_frame)
            else:
                print('Unrecognized command:{}'.format(' '.join(order)))

    def get(self):
        if self.pipes['_OUTPUT'].empty():
            return None
        return self.pipes['_OUTPUT'].get()

    class MulDot(multiprocessing.Process):
        def __init__(self, dot: pipeline.core.Node, pipes: dict):
            super(MulIgnition.MulDot, self).__init__(name=dot.name)
            self.dot = dot
            self.pipes = pipes

        def run(self):
            if self.dot.name == '_SOURCE':  # 如果是源头节点，则自己生成数据
                while self.dot.switch:
                    if self.pipes['_INPUT'].empty():
                        frames = self.dot.run(pipeline.core.Frame(end='_SOURCE'))
                    # 如果不为空，则读取命令
                    else:
                        frames = self.dot.run(self.pipes['_INPUT'].get())
                    # print('s:{}'.format(frames[0].end))
                    for frame in frames:
                        if frame.end in self.pipes.keys():  # 安全检查，检查frame当前帧的目的地是否有对应的管道
                            self.pipes[frame.end].put(frame)  # 如果有，则将当前帧放入管道中
                        else:
                            pass  # 否则什么也不干，相当于抛弃这个帧
            else:
                while self.dot.switch:  # 如果是非源头节点，则直接从自己的管道中读取数据
                    frame = self.pipes[self.dot.name].get()
                    if frame is not None:
                        frames = self.dot.run(frame)
                        # print('d:{} run, data:{}'.format(self.dot.name, frames[0].data))
                        for frame in frames:  # 按地址发送每一个帧
                            if frame.end in self.pipes.keys():  # 安全检查，检查frame当前帧的目的地是否有对应的管道
                                self.pipes[frame.end].put(frame)  # 如果有，则将当前帧放入管道中
                            else:
                                while self.pipes['_OUTPUT'].full():
                                    self.pipes['_OUTPUT'].get()
                                self.pipes['_OUTPUT'].put(frame)
                                # print(self.pipes['_OUTPUT'].qsize())
                                # print(self.dot.name)
