# Projekt Alpha 4
### Nebeský Michal
Třída C4b

# Potřebné věci pro spuštění
1. Operační system Windows / Linux - distribuce Debian
2. Python 3.9+ / pro linux python3
3. Putty/Telnet

# Navod na spuštění pro Windows
1. Stažený program rozbalte z .zip
2. Přejděte do složky cfg do souboru tcp_config.ini
3. Nastavte všechny potřebné udaje např. podle sekce Konfigurační soubor
4. Přejděte do šložky src
5. Do vrchního vyhledáváče souboru napiště cmd
6. Otevře se konzole
7. Do konzole napište python main.py
8. Program se spustí, nic nevypisuje, pouze problikává podtržítko
9. Jakékoliv možné stavy je možné sledovat v ../logs/app.log
10. Na program se poté dá připojit například pomocí Putty/Telnet podle ip a portu na kterém naslouchá

# Konfigurační soubor
V konfiguračním souboru (..cfg/tcp_config.ini) se nastavuje několik věcí:
1. IP adresa na kterém server naslouchá
2. Port na kterém server naslouchá
3. Rozsah IP Adress ve kterých bude program hledat obdobné programy
4. Rozsah Portu ve kterých bude program hledat obdobné programy

### Příklad nastavení

```text
[Server]
#IP Adresa na ktere server nasloucha
ip = 25.51.221.44
#Port na kterem server nasloucha
port = 8085

[Searching]
#Rozsah IP Adres
ip_range = 25.51.167.13 - 25.51.167.50
#Rozsah portu
port_range = 8084 - 8086
```


### Příklad spuštění
```cmd
Microsoft Windows [Version 10.0.19044.2604]
(c) Microsoft Corporation. All rights reserved.

D:\School\Python\Projekty\Alpha4\src>python main.py
_
```

# Navod na spuštění pro Linux
1. Stažený program rozbalte z .zip
2. Přejděte do složky cfg do souboru tcp_config.ini
3. Nastavte všechny potřebné udaje např. podle sekce Konfigurační soubor
4. Vytvořte si .service soubor pomoci (nano /etc/systemd/system/[nazev].service)
5. Podle sekce .service soubor konfigurace, vyplnte vše potřebné
6. Restartujte daemona (systemctl daemon-reload)
7. Zapněte vašeho nového deamona (systemctl start [nazev])
8. Zkontrolujte zda daemon běží (systemctl status [nazev])
9. Pro automaticke spouštění po startu lze použít přikaz (systemctl enable [nazev])

### .service soubor konfigurace

```text
[Unit]
Description=[nazev]
After=network.target

[Service]
User=<Uzivatelske jmeno>
WorkingDirectory=<cesta_k_programu/src/>
ExecStart=python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```