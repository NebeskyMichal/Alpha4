import configparser
import ipaddress
import logging
import socket


class CmdPing:
    """Třida pro prikaz TRANSLATEPING"{NazevProgramu}"""

    def run(connection, word_to_translate=None):
        """Metoda odesila peerovi reakci na TRANSLATEPING pomoci TRANSLATEPONG"{NazevProgramu}

        :param connection: Připojeni peera
        :param word_to_translate: Slovník, které se má přeložit (zde se nepoužívá)
        """
        connection.send(bytes("TRANSLATEPONG\"Nebesky Prekladac\"" + "\r\n", "utf-8"))


class CmdTransLocal:
    """Třida pro prikaz TRANSLATELOCL"{SlovickoKPrekladu}"""
    def run(connection, word_to_translate=None):
        """Metoda odesila peerovi reakci na TRANSLATELOCL pomoci TRANSLATESUC"{PrelozeneSlovicko},
         když se překlad povede nebo TRANSLATEERR"{Chyba}" kdyz se nepovede překlad

                :param connection: Připojeni peera
                :param word_to_translate: Slovník, které se má přeložit

                :return: Pokud dojde k překladu vraci se prelozene slovicko, když se nepovede vraci se False
                """
        with open('../cfg/words.txt') as f:
            lines = [line.rstrip() for line in f]

        words = {}
        for line in lines:
            eng, cz = line.split("=")
            words[eng] = cz

        if word_to_translate not in words:
            connection.send(bytes("TRANSLATEDERR\"Slovicko nebylo nalezeno v lokalnim slovniku\"" + "\r\n", "utf-8"))
            return False
        connection.send(bytes("TRANSLATEDSUC\"{}\"\r\n".format(words[word_to_translate]), "utf-8"))
        return words[word_to_translate]


class CmdTransScan:
    """Třida pro prikaz TRANSLATESCAN"{SlovickoKPrekladu}"""
    def scan(connection):
        """Metoda slouží k proscanování sítě a snaží se najít programy stejného použití pomocí přikazu
        TRANSLATEPING"{NazevProgramu}, čeká na odpoveď pomocí TRANSLATEPING a totot připojení pak ukládá jako validní

        :param connection: Připojeni peera

        :return: Validní připojení, kteár odpověděli pomocí TRANSLATEPONG
        """
        translators = []
        try:
            config = configparser.ConfigParser()
            config.read('../cfg/tcp_config.ini')
            config.sections()
            ip_range = config['Searching']['ip_range']
            port_range = config['Searching']['port_range']
            ip_start, ip_end = ip_range.split("-")

            port_start, port_end = port_range.split("-")
            port_start = int(port_start.strip())
            port_end = int(port_end.strip())
        except Exception as e:
            logging.error("There was an error reading the config file")

        for ip_int in range(int(ipaddress.IPv4Address(ip_start.strip())),
                            int(ipaddress.IPv4Address(ip_end.strip())) + 1):
            ip_address = str(ipaddress.IPv4Address(ip_int))

            for port in range(port_start, port_end + 1):
                try:
                    new_socket = socket.socket()
                    new_socket.settimeout(5)
                    new_socket.connect((ip_address, port))
                    new_socket.send(bytes("TRANSLATEPING\"{}\"".format("Nebesky C4b translator"), "utf-8"))
                    translated_word = new_socket.recv(1024).decode("utf-8")
                    if translated_word.startswith("TRANSLATEPONG"):
                        translators.append(ip_address+":"+str(port))
                        new_socket.close()
                except Exception as e:
                    pass

        return translators

    def run(connection, word_to_translate=None):
        """Metoda prohledává validní připojení, každému zasílá TRANSLATELOCL{SlovickoKPrekladu} a ocekava dve odpovedi:
            TRANSLATEDSUC{PrelozeneSlovicko}, když se překlad povede nebo TRANSLATEDERR"{Chyba}" kdyz se nepovede

                        :param connection: Připojeni peera
                        :param word_to_translate: Slovo, které se má přeložit

                        :return: Pokud dojde k překladu vraci se prelozene slovicko, když se nepovede vraci se False
                        """
        if len(word_to_translate.strip()) > 0:

            logging.basicConfig(filename='../logs/app.log', level=logging.DEBUG,
                                format='%(asctime)s:%(levelname)s:%(message)s')

            translated_word = ""

            with open('../cfg/words.txt') as f:
                lines = [line.rstrip() for line in f]

            words = {}
            for line in lines:
                eng, cz = line.split("=")
                words[eng] = cz

            if word_to_translate not in words:
                translated_word = False
            else:
                connection.send(bytes("TRANSLATEDSUC\"{}\"\r\n".format(words[word_to_translate]), "utf-8"))
                return True

            if translated_word is False:
                viable_translators = CmdTransScan.scan(connection)
                for translator in viable_translators:
                    ip_address, port = translator.split(":")
                    try:
                        new_socket = socket.socket()
                        new_socket.settimeout(5)
                        new_socket.connect((ip_address, int(port)))
                        new_socket.send(bytes("TRANSLATELOCL\"{}\"".format(word_to_translate), "utf-8"))
                        translated_word = new_socket.recv(1024).decode("utf-8")
                        if translated_word.startswith("TRANSLATEDSUC"):
                            break
                    except Exception as e:
                        pass

                if translated_word is False or translated_word.startswith("TRANSLATEDERR"):
                    connection.send(bytes("TRANSLATEDERR\"Slovicko se nepodarilo prelozit\"\r\n", "utf-8"))
                    return False

            connection.send(bytes(translated_word + "\r\n", "utf-8"))
            return True
