import time
import requests      # Libreria per effettuare le richieste HTTP ad Amazon
import json          # Gestisce il salvataggio dei prezzi storici in un file
import os            # Permette di verificare l'esistenza dei file sul MiniPC
import re            # Espressioni regolari per "pulire" le stringhe del prezzo
import asyncio       # Gestisce l'esecuzione asincrona e i tempi di attesa
import csv           # Legge i dati dal tuo file prodotti.csv
from datetime import datetime # Gestisce date e orari per i timestamp
from bs4 import BeautifulSoup # Analizza l'HTML delle pagine Amazon per trovare i prezzi
from telegram import Bot      # Interfaccia ufficiale per inviare messaggi tramite il bot

# --- CONFIGURAZIONE ---
TOKEN = "" #  ID del Bot Telegram
CHAT_ID = "" # ID del canale delle segnalazioni

# Percorsi dei file sul tuo MiniPC
DB_FILE = "prices_history.json"  # Memoria degli ultimi prezzi inviati
CSV_FILE = "prodotti.csv"        # Lista degli ASIN da monitorare

# Header per "simulare" un browser reale ed evitare il blocco di Amazon
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "it-IT,it;q=0.9"
}

# --- FUNZIONI DI SUPPORTO ---

def load_products_from_csv():
    """Legge il file CSV e restituisce un dizionario di prodotti."""
    products = {}
    try:
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    products[row['asin']] = {
                        "name": row['nome'],
                        "target_price": float(row['target_price'])
                    }
        return products
    except Exception as e:
        print(f"Errore critico nella lettura del CSV: {e}")
        return {}

def load_history():
    """Carica i prezzi salvati in precedenza dal file JSON."""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_history(history):
    """Salva lo stato attuale dei prezzi nel file JSON."""
    with open(DB_FILE, 'w') as f:
        json.dump(history, f, indent=4)

# --- CUORE DEL BOT ---

async def check_prices():
    """Funzione principale che esegue il monitoraggio ciclico."""
    bot = Bot(token=TOKEN)
    history = load_history()
    print(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] NomeBot in funzione...")

    while True: 
        products = load_products_from_csv()
        
        if not products:
            print("Attenzione: Nessun prodotto trovato nel file prodotti.csv.")
        else:
            for asin, info in products.items():
                url = f"https://www.amazon.it/dp/{asin}"
                try:
                    # Scarica la pagina del prodotto
                    page = requests.get(url, headers=HEADERS, timeout=15)
                    soup = BeautifulSoup(page.content, "html.parser")
                    
                    # 1. RECUPERO PREZZO
                    price_span = soup.find("span", {"class": "a-price-whole"})
                    
                    # 2. RECUPERO IMMAGINE (Nuova parte aggiunta)
                    # Amazon usa solitamente l'ID 'landingImage' per la foto principale
                    img_tag = soup.find("img", {"id": "landingImage"})
                    image_url = img_tag.get("src") if img_tag else None
                    
                    if price_span:
                        # Pulizia del testo del prezzo
                        raw_text = price_span.get_text().replace('.', '').replace(',', '.')
                        current_price = float(re.sub(r'[^\d.]', '', raw_text))
                        
                        last_data = history.get(asin, {})
                        last_price = last_data.get("price")
                        now_str = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

                        # Se il prezzo è sceso sotto il target e non abbiamo già inviato lo STESSO prezzo
                        if current_price <= info["target_price"]:
                            if current_price != last_price:
                                
                                # Componi il testo del messaggio (caption della foto)
                                msg = (f"🚨 VARIAZIONE PREZZO!\n"
                                       f"📦 {info['name']}\n"
                                       f"💰 Prezzo attuale: {current_price}€\n"
                                       f"⏰ Rilevato il: {now_str}\n"
                                       f"🔗 {url}")
                                
                                # TENTA DI INVIARE LA FOTO CON IL TESTO
                                if image_url:
                                    try:
                                        # Invia la foto recuperata con il testo come didascalia
                                        await bot.send_photo(CHAT_ID, photo=image_url, caption=msg)
                                    except Exception as img_err:
                                        # Se l'invio della foto fallisce, invia almeno il testo semplice
                                        print(f"Errore invio foto per {asin}: {img_err}")
                                        await bot.send_message(CHAT_ID, msg)
                                else:
                                    # Se non abbiamo trovato l'immagine, invia solo il testo
                                    await bot.send_message(CHAT_ID, msg)
                                
                                # Salva nella memoria JSON
                                history[asin] = {
                                    "price": current_price,
                                    "timestamp": now_str
                                }
                                save_history(history)
                                print(f"Notifica inviata per {info['name']}: {current_price}€")
                            else:
                                print(f"[{now_str}] {info['name']}: Prezzo stabile a {current_price}€")
                    
                except Exception as e:
                    print(f"Errore durante il controllo di {asin}: {e}")
                
                # Pausa di 7 secondi per non allertare i sistemi anti-bot
                await asyncio.sleep(7)

        # Riposo tra un ciclo completo e l'altro
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Ciclo completato. Prossimo tra 60 minuti.")
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(check_prices())
    except KeyboardInterrupt:
        print("Bot arrestato dall'utente.")
