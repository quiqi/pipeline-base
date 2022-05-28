import pipeline.core as core


if __name__ == '__main__':
    start_node = core.Node('start_node', ['head1'])
    chart1 = core.NodeSet([
        core.Node('head1', ['node1']),
        core.Node('node1', ['node2']),
        core.Node('node2', ['node3', 'head2/node5']),
        core.Node('node3'),
        core.Node('node4')
    ], source='head1')

    chart2 = core.NodeSet([
        core.Node('head2', ['node1']),
        core.Node('node1', ['node2']),
        core.Node('node2', ['node3', 'node4']),
        core.Node('node3'),
        core.Node('node5')
    ])

    chart = core.NodeSet([start_node, chart1, chart2])
    while chart.switch:
        chart.run(core.Frame('head1'))
