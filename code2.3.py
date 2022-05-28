import pipeline.core as core

chart1 = core.NodeSet([
    core.Node('head1', ['node1']),
    core.Node('node1', ['node2']),
    core.Node('node2', ['node3', 'head2/node5']),
    core.Node('node3'),
    core.Node('node4')
])

chart2 = core.NodeSet([
    core.Node('head2', ['node1']),
    core.Node('node1', ['node2']),
    core.Node('node2', ['node3', 'node4']),
    core.Node('node3'),
    core.Node('node5')
])

chart = core.NodeSet([chart1, chart2])

fs = chart.run(core.Frame(end='head1'))
print(fs[1].visited)