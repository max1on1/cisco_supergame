# -*- coding: utf-8 -*-
# Based on http://matthiaseisen.com/articles/graphviz/

import sys
import difflib
import glob
import os
import pprint
from datetime import datetime  

try:
    import graphviz as gv
except ImportError:
    print("Module graphviz needs to be installed")
    sys.exit()

styles = {
    'graph': {
        'label': 'LLDP Network Map',
        'fontsize': '16',
        'fontcolor': 'white',
        'bgcolor': '#333333',
        'rankdir': 'BT',
    },
    'nodes': {
        'fontname': 'Helvetica',
        'shape': 'circle',
        'fontcolor': 'white',
        'color': '#006699',
        'style': 'filled',
        'fillcolor': '#006699',
        'margin': '0.4',
    },
    'edges': {
        'style': 'dashed',
        'color': 'green',
        'arrowhead': 'open',
        'fontname': 'Courier',
        'fontsize': '14',
        'fontcolor': 'white',
    }
}


def apply_styles(graph, styles):
    graph.graph_attr.update(('graph' in styles and styles['graph']) or {})
    graph.node_attr.update(('nodes' in styles and styles['nodes']) or {})
    graph.edge_attr.update(('edges' in styles and styles['edges']) or {})
    return graph

def get_diffs(filename):

    latest_file = sorted(glob.iglob('img/*.svg'), key=os.path.getctime)[-2]
#иногда бывает что модуль ос возвращает два файла как последние созданные, это надо проверить
    if isinstance(latest_file, list):
        if '.' in latest_file:
            latest_file=latest_file.split('.')
            latest_file=latest_file[0]
            print(latest_file)
        else:
            latest_file=latest_file[0]
            print(latest_file)
    else:
        if '.' in latest_file:
            latest_file=latest_file.split('.')
            latest_file=latest_file[0]
            print(latest_file)

    filename=filename.split('.')
    print(latest_file)
    lines1 = open(latest_file).readlines()
    lines2 = open(filename[0]).readlines()
    pprint.pprint(lines1)
    pprint.pprint(lines2)
#выводим в консоль изменения с предыдущей топологией
    for line in difflib.unified_diff(lines1, lines2):
        print(line)



def draw_topology(topology_dict, output_filename='img/topology'):
    '''
    Генерируем топологию
    '''
    #Проверяем колличество файлов в папке
    a = os.listdir('img')

    now = datetime.now()
    output_filename=output_filename+'_'+now.strftime("%H:%M:%S")
    nodes = set([
        item[0]
        for item in list(topology_dict.keys()) + list(topology_dict.values())
    ])

    g1 = gv.Graph(format='svg')

    for node in nodes:
        g1.node(node)

    for key, value in topology_dict.items():
        head, t_label = key
        tail, h_label = value
        g1.edge(
            head, tail, headlabel=h_label, taillabel=t_label, label=" " * 12)

    g1 = apply_styles(g1, styles)
    
    filename = g1.render(filename=output_filename)
    print("Graph saved in", filename)
    
    #если в папке есть более старые файлы выведем дифф в консоль
    if len(a) <= 2:
        print("Directory is empty, nothing to diff")
    else:    
        difs = get_diffs(filename)
    
