import json
import random
from concurrent.futures import ThreadPoolExecutor
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from functools import partial
from time import sleep, perf_counter
from typing import List
from prometheus_client import start_http_server, Gauge, CollectorRegistry


class ExporterInstance:
    gauges_list: list[Gauge]

    def __init__(self, id: int, number_of_metrics: int, init_value: int, port: int):
        self.registry = CollectorRegistry()
        self.gauges_list = []
        self.port = port
        i = 0
        while i < number_of_metrics:
            gauge = self.create_gauge(id, i)  # create gauge with id and number
            self.gauges_list.append(gauge)  # append gauge to list of gauges
            gauge.set(init_value + i)  # set value init + i
            i += 1
        print(f' created group of {number_of_metrics} gauges.')
        print(f' init value first gauge: {init_value}, init value of last gauge: {init_value + number_of_metrics - 1}')
        start_http_server(port, registry=self.registry)
        print(f' started http server with port {port}')

    def create_gauge(self, id: int, number: int):
        name = "Gauge_" + str(id) + "_" + str(number)
        desc = "(Instance " + str(id) + ", number " + str(number) + ")"
        print(f'{name}  {desc}')
        return Gauge(name, desc, registry=self.registry)

    def inc_all_gauges(self):
        for gauge in self.gauges_list:
            gauge.inc()


class ExporterManager:
    def __init__(self):
        self.list_of_exporters = []
        self.services_dict = {'targets': [], 'labels': [{'name': 'load_test', 'location': 'potsdam'}]}
        self.services_json_string = ""

    def create_exporters(self, num_exporters, init_value=1):
        for i in range(num_exporters):
            obj = ExporterInstance(i, 10, init_value, 10000 + i)
            self.list_of_exporters.append(obj)
            self.services_dict['targets'].append("target_" + str(i) + ':' + str(10000 + i))
        self.services_json_string = "[" + json.dumps(self.services_dict) + "]"

    def update_instances(self):
        def inc_all_gauges_caller():
            obj.inc_all_gauges()

        with ThreadPoolExecutor() as executor:
            while True:
                for obj in self.list_of_exporters:
                    executor.submit(inc_all_gauges_caller)
                    print("update")
                sleep(1)



class SDHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, services_json_string, *args, **kwargs):
        self.services_json_string = services_json_string
        super().__init__(*args, **kwargs)

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(self.services_json_string.encode("utf-8"))


def start_server():
    server_address = ('', 19996)
    httpd = HTTPServer(server_address, SDHTTPRequestHandler)
    server_thread = Thread(target=httpd.serve_forever)
    server_thread.start()


if __name__ == "__main__":
    manager = ExporterManager()
    manager.create_exporters(10)
    #manager.update_instances()
    update_thread = Thread(target=manager.update_instances())
    update_thread.start()

    handler = partial(SDHTTPRequestHandler, manager.services_json_string)
    server = HTTPServer(('', 19996), handler)

    server_thread = Thread(target=server.serve_forever())
    server_thread.start()