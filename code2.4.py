import pipeline.core as core

# 初始化每一个节点
node1 = core.Node('node1', ['node2'])
node2 = core.Node('node2', ['node3', 'node4'])
node3 = core.Node('node3', ['node1'])# 将数据发回node1形成死循环
# node4 = core.Node('node4', ['node1'])# 将数据发回node1形成死循环
node4 = core.Node('node4')

# 将以上节点放入NodeSet中构建流程图
chart = core.NodeSet([node1, node2, node3, node4])

frame = core.Frame(end='node1')		# 生成帧对象
fs = chart.run(frame)				# 运行一次该流程图
a = 0