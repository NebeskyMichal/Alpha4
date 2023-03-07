import socket
import logging
import configparser
import threading as th
from commands import commands


class TCPServer:
    """TCP Server/Prekladac, nasloucha na ip a portu z konfiguracniho souboru, obstarava prikazy od jinych peeru"""
    def __init__(self):
        """Konstruktor si nastavuje ip a port z konfiguracniho souboru, nastavuje a zapina naslouchani"""
        logging.basicConfig(filename='../logs/app.log', level=logging.DEBUG,
                            format='%(asctime)s:%(levelname)s:%(message)s')

        config = configparser.ConfigParser()
        config.read('../cfg/tcp_config.ini')
        config.sections()

        self.server_inet_address = (config['Server']['ip'], int(config['Server']['port']))
        self.server_socket = socket.socket()
        self.server_socket.bind(self.server_inet_address)
        self.server_socket.listen()
        self.commands = {"TRANSLATEPING": commands.CmdPing,
                         "TRANSLATELOCL": commands.CmdTransLocal,
                         "TRANSLATESCAN": commands.CmdTransScan,
                         }
        self.isRunning = True
        self.translator_connections = []
        self.start_server()

    def start_server(self):
        """Metoda, ktera vyrizuje pozadavky na pripojeni na server
        a posila je do dalsi metody communicate_with_client(). Metoda ocekava pripojeni dokud se server nevypne"""
        logging.info("Server start on " + str(self.server_inet_address[0]) + ":" + str(self.server_inet_address[1]))
        while self.isRunning:
            try:
                connection, client_inet_address = self.server_socket.accept()
                connection.settimeout(15)
                p = th.Thread(target=self.communicate_with_client, args=(connection, client_inet_address))
                p.start()
            except Exception as e:
                logging.info("Server Closed")

    def communicate_with_client(self, connection, client_inet_address):
        """Metoda pro komunikaci s jednotlivymi peery. Dochází zde k provaděni hlavnich prikazu ze zadání
        V připadě chyb s peerem ukončí připojeni. Reaguje i na nesprávné přikazy.

        :param connection: Pripojeni jednotliveho peeru
        :param client_inet_address: Inet adresa, jednotliveho peeru

        """
        self.translator_connections.append(connection)
        logging.info("Client connection accepted from "
                     + str(client_inet_address[0]) + ":" + str(client_inet_address[1]))
        while True:
            try:
                data = connection.recv(1024).decode("utf-8")
                if len(data.strip()) > 0:
                    if data.startswith("TRANSLATE"):
                        data = data.split("\"")
                        command = data[0]
                        self.commands[command].run(connection, data[1])
                    else:
                        connection.send(bytes("TRANSLATEDERR\"Neznamy prikaz\"\r\n", "utf-8"))
            except Exception as e:
                logging.info("Client connection was closed")
                break

        connection.close()
        self.translator_connections.remove(connection)

