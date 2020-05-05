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
    lldp_detail = task.run(task=networking.napalm_cli, commands=['sh lldp neighbors detail'])
    hostname = host_facts.result['facts']['hostname']
    #Парсим аутпут с помощью шаблона textfsm
    template = open("cisco_ios_show_lldp_neighbors.textfsm")
    re_table = textfsm.TextFSM(template) 
    parsed_output = re_table.ParseText(lldp_data.result['sh lldp neighbors'])


    template = open("cisco_ios_show_lldp_neighbors_detail.textfsm")
    re_table = textfsm.TextFSM(template)
    lldp_det_parsed = re_table.ParseText(lldp_detail.result['sh lldp neighbors detail'])
#    for item in lldp_det_parsed:


    #запоминаем данные
    task.host['lldp_det'] = lldp_det_parsed
    task.host['f_hostname'] = hostname
    task.host['lldp_data'] = parsed_output

def main():
    # определяем путь до скрипта для упрощения навигации
    # иницилизируем норнир
    with InitNornir(config_file="config.yaml") as nr:
  #      nr = InitNornir(config_file="config.yaml")
        nr.run(task=show_lldp)
      
        topology_dict = {}
        exit_flag = False
        # проверяем не обноружилось ли новых хостов, если обнаружились то добавляем их в инвентори
        # и запускаем таск снова
        while exit_flag == False:
            for host in nr.inventory.dict()['hosts']:
                if nr.inventory.dict()['hosts'][host]['data']['lldp_det']:
                    for item in nr.inventory.dict()['hosts'][host]['data']['lldp_det']:
                        if item[4] not in nr.inventory.dict()['hosts']:
                            nr.inventory.add_host(item[4])
                            nr.inventory.hosts[item[4]].hostname = item[7]
                            #nr.inventory.hosts[item[4]].groups = ['cisco']
                            pprint.pprint(nr.inventory.dict())
                            print(item[4])
                            nr.run(task=show_lldp)
                        else:
                            exit_flag = True

        #собираем итоговый словарь топологии
        for host in nr.inventory.dict()['hosts']:
            for item in nr.inventory.dict()['hosts'][host]['data']['lldp_data']:
                neighbor_hostname = item[0]
                local_int = item[1]
                neighbor_int = item[3]
                #проверяем на дублирующиеся линки
                if (neighbor_hostname,neighbor_int) not in topology_dict:
                    topology_dict.update({(nr.inventory.dict()['hosts'][host]['data']['f_hostname'],local_int):(neighbor_hostname,neighbor_int)})

        pprint.pprint(topology_dict)
        #Рисуем граф с нашей топологией и сохраняем в папку img/
        draw.draw_topology(topology_dict)

if __name__ == '__main__':
    main()


