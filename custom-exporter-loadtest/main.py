import json
import random
from concurrent.futures import ThreadPoolExecutor
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from time import sleep, perf_counter

from prometheus_client import start_http_server, Gauge, CollectorRegistry


class Exp_Instance:
    def __init__(self, id:int, number_of_metrics:int, init_value:int, port:int):
        self.registry = CollectorRegistry()
        self.gauges_list=[]
        self.port=port
        i = 0
        while i < number_of_metrics:
            gauge = self.create_gauge(id, i) #create gauge with id and number (Gauge_1_1 Gauge_1_2, etc..)
            self.gauges_list.append(gauge) # append it to list of gauges
            gauge.set(init_value+i) # set value init + i
            i += 1
        print(f' created group of {number_of_metrics} gauges.')
        print(f' init value first gauge: {init_value}, init value of last gauge: {init_value+number_of_metrics-1}')
        start_http_server(port, registry=self.registry)
        print(f' started http server with port {port}')

    def create_gauge(self, id:int, number: int):
        name = "Gauge_" + str(id) + "_" + str(number)
        desc = "(Instance " + str(id) + ", number " + str(number) + ")"
        print(f'{name}  {desc}')
        return Gauge(name, desc, registry=self.registry)

    def inc_all_gauges(self):
        for gauge in self.gauges_list:
            gauge.inc()
        return True


class SDHTTPRequestHandler(BaseHTTPRequestHandler):
    global services_json_string
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(services_json_string.encode("utf-8"))


if __name__ == "__main__":
    objects = []
    #  service discovery should be added
    services_dict = {'targets':[]}

    '''create instances and add them to json object'''
    for i in range(10):
        obj = Exp_Instance(i, 1000, i*1, 10000+i)
        objects.append(obj)
        # append instance to sd list
        services_dict['targets'].append("target_"+str(i)+':'+str(10000+i))
    services_json_string = "[" + json.dumps(services_dict) + "]"

    '''start sd http server'''
    server_address = ('', 19996)
    httpd = HTTPServer(server_address, SDHTTPRequestHandler)

    # Create a thread for the server
    server_thread = Thread(target=httpd.serve_forever)

    # Start the server thread
    server_thread.start()


    '''update instances '''
    with ThreadPoolExecutor() as executor:
        while True:
            print("updating all instances...")
            for o in objects:
                executor.submit(o.inc_all_gauges())
            sleep(1)