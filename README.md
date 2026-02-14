# italyhardwaretrackerbot
Creato da Nando, Admin della community di r/ItalyHardware, questo semplice bot monitora automaticamente una lista di componenti su Amazon e ti avvisa non appena i prezzi scendono. È uno strumento semplice e veloce pensato per aiutarti a risparmiare sui tuoi acquisti tech. Miglioriamolo insieme.

# Come si installa?
Ti serve innanzitutto Python.
In ambiente Linux, installalo da terminale, se non presente, ad esempio col comando:

```
sudo apt-get install python3
```

E poi crea una cartella col nome che vuoi dare al bot. Copiaci all'interno i file scaricabili nella release di questo repository.

Posizionati quindi nella cartella appena creata e crea un ambiente virtuale col comando:

```
python3 -m venv venv && source venv/bin/activate
```

E installa le librerie indicate nel file requirements.txt col comando:
```
pip install -r requirements.txt
```

Per far sì che il bot non si fermi quando chiudi il terminale, usa systemd per creare un servizio dedicato, creando un file in /etc/systemd/system/nomebot.service col codice seguente:

```
[Unit]
Description=inserisci la tua descrizione
After=network.target

[Service]
#Sostituisci 'tuo-utente' con il tuo nome utente linux
User=tuo-utente
WorkingDirectory=/home/tuo-utente/nomebot
#Usa il percorso completo dell'eseguibile python nell'ambiente virtuale
ExecStart=/home/tuo-utente/nome/venv/bin/python /home/tuo-utente/nomebot/nomebot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Dove utente e nomebot sono i nomi che avete associato al bot, che è da sostituire in tutte le sue istanze per non lasciarlo anonimo come in questo esempio.
È possibile poi lanciarlo col comando:

```
sudo systemctl start nomebot.service
```

Per controllarne lo statto, invece, usa il comando:

```
sudo systemctl status nomebot.service
```

Ricorda di inserire in TOKEN il token associato da Telegram al tuo bot, mentre in CHAT_ID l'id della chat associata al tuo bot in Telegram, o del canale, o gruppo, in cui è invitato il bot.

Ho aggiunto anche due script per far partire o stoppare il bot, oltre uno per controllarne il log, che devono essere impostato come eseguibili dal terminale col comando:

```
chmod +x start_bot.sh stop_bot.sh logs.sh
```

Il file prodotti.csv, invece, contiene l'elenco dei prodotti da poter tracciare. Potete popolarlo con quelli che volete. Vi basterà inserire l'ASIN del prodotto Amazon nella prima colonna, la descrizione del prodotto nella seconda, e il prezzo target nella terza. Quando il bot noterà un prezzo inferiore per un prodotto, se intercettato nel lasso di tempo in cui è in funzione allora segnalerà l'offerta come indicato. Un file json, intanto, controllerà lo stato delle segnalazioni già effettuate ed eviterà di duplicarle.

# Come creare il bot su Telegram

Semplicemente parla con @BotFather, crea il bot e segnati il valore di API TOKEN, che ti servirà nel valore TOKEN del codice del bot.

# Dove conviene farlo girare

Il mio consiglio è una VPS in cloud o un MiniPC in locale che abbia un TDP molto basso. Data la poca potenza di calcolo necessaria, è possibile hostarlo anche su un Raspberry Pi o un vecchio NUC. Si accettano ulteriori raccomandazioni.
