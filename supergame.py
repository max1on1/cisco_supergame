import os
import re
import sys
import pprint
import textfsm
import re
import draw_topology as draw

from nornir.plugins.tasks import networking, text 
from nornir.plugins.functions.text import print_title, print_result 
from nornir import InitNornir
from nornir.core import exceptions
from nornir.core.filter import F
from nornir_scrapli.tasks import send_command
from nornir.plugins.tasks import networking

def show_lldp(task):
    lldp_data = task.run(task=networking.napalm_cli, commands=['sh lldp neighbors'])
    host_facts = task.run(task=networking.napalm_get, getters=['facts'])
    hostname = host_facts.result['facts']['hostname']
    #Парсим аутпут с помощью шаблона textfsm
    template = open("cisco_ios_show_lldp_neighbors.textfsm")
    re_table = textfsm.TextFSM(template) 
    parsed_output = re_table.ParseText(lldp_data.result['sh lldp neighbors'])

    #запоминаем данные
    task.host['f_hostname'] = hostname
    task.host['lldp_data'] = parsed_output

def save_topology_dict(topology_dict):
    dict = topology_dict
    f = open("topology_files/topology.txt","w")
    f.write( str(dict) )
    f.close()


def main():
    # определяем путь до скрипта для упрощения навигации
    # иницилизируем норнир
    with InitNornir(config_file="config.yaml") as nr:
        nr.run(task=show_lldp)
        topology_dict = {}
        #собираем итоговый словарь топологии
        for host in nr.inventory.dict()['hosts']:
            for item in nr.inventory.dict()['hosts'][host]['data']['lldp_data']:
                neighbor_hostname = item[0]
                local_int = item[1]
                neighbor_int = item[3]
                #проверяем на дублирующиеся линки
                if (neighbor_hostname,neighbor_int) not in topology_dict:
                    topology_dict.update({(nr.inventory.dict()['hosts'][host]['data']['f_hostname'],local_int):(neighbor_hostname,neighbor_int)})
        #Сохраняем словарь с топологией в файл
        save_topology_dict(topology_dict)

        pprint.pprint(topology_dict)
        #Рисуем граф с нашей топологией и сохраняем в папку img/
        draw.draw_topology(topology_dict)

if __name__ == '__main__':
    main()


