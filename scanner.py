import requests
import re
import datetime
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def show_help():
    table = Table(title="GUIDA COMANDI IDK-TOOL")
    table.add_column("Comando", style="cyan")
    table.add_column("Descrizione", style="magenta")
    table.add_row("idk-hunt <user>", "Cerca ovunque (Siti + Discord/Telegram)")
    table.add_row("exit", "Chiude il tool")
    console.print(table)

def extract_data(html_content):
    emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html_content)))
    phones = list(set(re.findall(r'\+\d{1,3}[\s-]?\d{6,14}', html_content)))
    return emails, phones

def check_sito(url_base, username):
    full_url = url_base + username
    try:
        r = requests.get(full_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            title = soup.title.string.strip() if soup.title else "Nessun titolo"
            emails, phones = extract_data(r.text)
            return {"url": full_url, "title": title, "emails": emails, "phones": phones}
    except: pass
    return None

def esegui_caccia_totale(username):
    console.print(f"\n[bold blue]=== ANALISI PROFONDA: {username} ===[/bold blue]")
    try:
        with open("siti.txt", "r") as f:
            lista_siti = [line.strip() for line in f if line.strip()]
        
        report_name = f"REPORT_{username}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            results = list(executor.map(lambda url: check_sito(url, username), lista_siti))
        
        # Scrittura con encoding utf-8 per evitare crash con emoji
        with open(report_name, "w", encoding='utf-8') as f:
            f.write(f"OSINT REPORT: {username}\nData: {datetime.datetime.now()}\n\n")
            
            for res in results:
                if res:
                    console.print(f"[green][+] TROVATO:[/green] {res['url']} | [italic]{res['title']}[/italic]")
                    f.write(f"URL: {res['url']} | TITOLO: {res['title']}\n")
                    if res['emails']: f.write(f"  EMAIL: {res['emails']}\n")
                    if res['phones']: f.write(f"  PHONE: {res['phones']}\n")
            
            # Discord & Telegram
            discord_dork = f"https://www.google.com/search?q=site:discord.com+%22{username}%22"
            telegram_link = f"https://t.me/{username}"
            
            f.write(f"\n--- RICERCA ESTERNA ---\n")
            f.write(f"DISCORD DORK: {discord_dork}\n")
            f.write(f"TELEGRAM LINK: {telegram_link}\n")
            
            console.print(f"\n[bold cyan][!] Link Discord/Telegram pronti nel report.[/bold cyan]")
            console.print(f"[bold yellow]>> REPORT SALVATO: {report_name}[/bold yellow]")
            
    except Exception as e:
        console.print(f"[red]Errore critico: {e}[/red]")

def main():
    console.print(Panel("[bold cyan]IDK-TOOL MASTER EDITION[/bold cyan]"))
    show_help()
    while True:
        cmd = console.input("\n[bold blue]IDK > [/bold blue]").strip()
        if cmd == "exit": break
        elif cmd.startswith("idk-hunt"):
            parts = cmd.split()
            target = parts[1] if len(parts) > 1 else console.input("Inserisci target: ")
            esegui_caccia_totale(target)
        else:
            console.print("[red]Comando non valido. Usa 'idk-hunt <user>'[/red]")

if __name__ == "__main__":
    main()