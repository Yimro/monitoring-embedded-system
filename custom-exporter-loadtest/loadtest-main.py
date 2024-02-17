#!/usr/bin/env python3
'''
Command line arguments:
1st: number of exporters
2nd: number of metrics for each exporter
3rd: number of labels
'''
import sys
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from functools import partial
from time import sleep
from prometheus_client import start_http_server, Gauge, CollectorRegistry

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
# logging.basicConfig(filename='log/lt-exporter.log', format='%(asctime)s %(message)s', level=logging.INFO)
# logging.basicConfig(handlers=[logging.FileHandler('lt-exporter.log'), logging.StreamHandler(sys.stdout)], format='%(asctime)s %(message)s', level=logging.INFO)

class ExporterInstance:
    def __init__(self, id: int, number_of_metrics: int, init_value: int, port: int):
        self.registry = CollectorRegistry()
        self.port = port
        self.id = id
        self.init_value = init_value
        self.gauges_list = [self.create_gauge(id, i) for i in range(number_of_metrics)]

        #logging.info(f'Created exporter id nr {self.id} with {number_of_metrics} gauges.')
        #logging.info(f'Init gauge 0: {init_value}, init gauge {number_of_metrics-1}: {init_value + number_of_metrics - 1}')

        try:
            start_http_server(port, registry=self.registry)
            logging.info(f'Exporter {self.id} is listening on port {port}')
        except Exception as e:
            logging.error(f'Failed to start HTTP Server: {e}')

    def create_gauge(self, id: int, number: int):
        name = "Gauge_" + str(number)
        desc = "(Instance " + str(id) + ", number " + str(number) + ")"
        return Gauge(name, desc, registry=self.registry)

    def inc_all_gauges(self, val:int=1):
        for gauge in self.gauges_list:
            gauge.inc(val)

    def dec_all_gauges(self, val:int=1):
        for gauge in self.gauges_list:
            gauge.dec(val)

    def reset_all_gauges(self):
        for i, gauge in enumerate(self.gauges_list):
            gauge.set(self.init_value + i)

class ExporterManager:
    def __init__(self):
        self.label_dict = {}
        self.list_of_exporters = []
        self.services_dict = {'targets':[], 'labels':{}}
        self.services_json_string = ""

    def create_exporters(self, num_exporters, num_metrics, num_labels=10, init_value=0, init_port=10000):
        logging.info(f'Creating {num_exporters} exporters with {num_metrics} metrics and {num_labels} labels.')
        for i in range(num_exporters):
            obj = ExporterInstance(i, num_metrics, init_value+(10*i), init_port + i)
            self.list_of_exporters.append(obj)
            self.services_dict['targets'].append('10.0.0.103:' + str(init_port + i))
            self.services_dict['labels'].update(self.create_label_dict(num_labels))
        self.services_json_string = "[" + json.dumps(self.services_dict) + "]"

    def create_label_dict(self, n:int):
        for i in range(n):
            self.label_dict['key_'+str(i)]=str('value_'+str(i))
        return self.label_dict

    def update_instances(self):
        while True:
            for i in range(600):
                for exporter in self.list_of_exporters:
                    exporter.inc_all_gauges(0.1)
                sleep(1)
            for exporter in self.list_of_exporters:
                exporter.reset_all_gauges()

class SDHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, services_json_string, *args, **kwargs):
        self.services_json_string = services_json_string
        super().__init__(*args, **kwargs)

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(self.services_json_string.encode("utf-8"))


if __name__ == "__main__":
    exporter_manager = ExporterManager()
    try:
        # logging.info(f'main: creating {sys.argv[1]} exporter(s) with each {sys.argv[2]} metrics. Job has {sys.argv[3]} '
                     # f'labels')
        exporter_manager.create_exporters(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
        update_thread = Thread(target=exporter_manager.update_instances)
        update_thread.start()

        service_discovery_handler = partial(SDHTTPRequestHandler, exporter_manager.services_json_string)
        service_discovery_server = HTTPServer(('', 19996), service_discovery_handler)
        logging.info(f'HTTP Service Discovery is listening on port 19996')

        service_discovery_server_thread = Thread(target=service_discovery_server.serve_forever)
        service_discovery_server_thread.start()
    except IndexError as e:
        print("Usage: ./main.py <number of exporters> <number of metrics for each exporter> ")
