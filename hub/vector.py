"""
Server representation of controllable device
"""
import ast
import logging
import telnetlib


class Vector:

    def __init__(self, ip: str, port: str, name: str):
        super().__init__()
        self.ip = ip
        self.port = port
        self.name = name
        self.tn = None
        self.services = {}
        self.tell("", None)

    def discover(self):
        self.open_telnet()
        try:
            services = self.send("discover", None)
        except ConnectionError:
            logging.error("Unable to discover " + self.name)
        """
        Expecting services in the format of a str(dict)
        {'service': ('opt', 'opt'), 'service2': ('opt', 'opt', 'opt')}
        """
        try:
            self.services = ast.literal_eval(services.strip())
        except (ValueError, AttributeError, SyntaxError) as exc:
            logging.error("Malformed string on discovery from " + self.ip + "'" + str(services) + "'")

    def validate(self, service, options):
        valid = True
        if service not in self.services.keys() and service is not "discover":
            valid = False
        service_options = self.services.get(service)
        if service_options is not None and type(service_options) is "tuple":
            if service_options is not None and (options is None or len(options) == 0):
                valid = False
            elif service_options is not None and options[0] not in service_options:
                valid = False
        return valid

    def tell(self, service, options):
        return self.send("service " + service, options)

    def send(self, service, options):
        self.open_telnet()
        if self.tn is not None:
            try:
                if options is not None:
                    self.tn.write((service + " " + ' '.join(map(str, options)) + "\r\n").encode('ascii'))
                else:
                    self.tn.write((service + "\r\n").encode('ascii'))
                ret = str(self.tn.read_until("> ".encode('ascii')).decode('ascii'))
                ret = ret.replace('\r\n$junction >', '')
                ret = ret.replace('$junction >', '')
                ret = ret.strip()
                logging.debug("Junction " + self.ip + ": " + ret)
                return ret
            except (ConnectionAbortedError, ConnectionRefusedError, ConnectionAbortedError, ConnectionError,
                    ConnectionResetError):
                self.tn = None
                self.open_telnet()
                # self.tell(service, options)
            except EOFError:
                logging.error("Junction send EOF")
                self.tn.read_all()
                self.tn.close()
                self.tn = None
                self.open_telnet()
        else:
            raise ConnectionError("Vector '" + self.name + "' unavailable.")

    def open_telnet(self):
        if self.tn is None:
            try:
                self.tn = telnetlib.Telnet(self.ip, self.port)
                self.tn.read_until("> ".encode('ascii'))  # Ignore welcome message
                self.discover()
            except (ConnectionAbortedError, ConnectionRefusedError, ConnectionAbortedError, ConnectionError,
                    ConnectionResetError):
                logging.error("Unable to reach " + self.ip)


class Group:

    def __init__(self, vectors: list, name: str):
        super().__init__()
        self.vectors = vectors
        self.services = []
        self.name = name

    def discover(self):
        self.services = []
        for vector in self.vectors:
            for service, options in vector.services.items():
                string = (service + ": " + str(options))
                if string not in self.services:
                    self.services.append(string)
