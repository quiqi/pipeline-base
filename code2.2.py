import pipeline.core as core

# 初始化每一个节点
node1 = core.Node('node1', ['node2'])
node2 = core.Node('node2', ['node4', 'node5'])
node3 = core.Node('node3')
node4 = core.Node('node4', ['node3'])
node5 = core.Node('node5')

# 将以上节点放入NodeSet中构建流程图
chart = core.NodeSet([node1, node2, node3, node4, node5])

frame = core.Frame(end='node1')		# 生成帧对象
fs = chart.run(frame)				# 运行一次该流程图
for f in fs:
    print(f.visited)