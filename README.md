# Standard-Leitfaden für neue Webdeveloper

Dieses Projekt ist eine statische Website mit ergänzenden SEO-Skripten. Der Leitfaden beschreibt die wichtigsten Schritte, damit ein neuer Entwickler das Repository schnell lokal übernehmen und weiterentwickeln kann.

## 1. Repository klonen

Das Projekt wird zuerst von GitHub auf den eigenen Rechner geladen.

```bash
git clone <URL-zum-GitHub-Repository>
```

Danach liegt das komplette Projekt mit Ordnerstruktur und Historie lokal vor.

## 2. Ordner in VS Code öffnen

Den geklonten Projektordner in VS Code über **Datei > Ordner öffnen...** auswählen.

VS Code erkennt die Struktur automatisch und zeigt die Website-Dateien direkt an.

## 3. Abhängigkeiten installieren

In diesem Repository sind keine klassischen Node-Abhängigkeiten im `package.json` hinterlegt. Die SEO-Hilfsskripte arbeiten mit Python und den Paketen aus `requirements.txt`.

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Falls noch keine virtuelle Umgebung vorhanden ist, sollte sie zuerst angelegt werden:

```powershell
python -m venv .venv
```

## 4. Geheime Schlüssel und lokale Konfiguration

Geheime Daten gehören nicht ins Git-Repository. Die konkreten Werte stehen bewusst ganz am Ende dieser Anleitung, damit sie bei der Übergabe getrennt behandelt werden können.

Wenn eine `.env.example` verwendet wird, dient sie nur als Vorlage für die lokalen Geheimnisse.

## 5. Projekt-Setup nach dem Klonen

Ein neuer Entwickler führt lokal vor allem diese Schritte aus:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Danach können die vorhandenen Hilfsskripte genutzt werden, zum Beispiel für Sitemap- und SEO-Abläufe.

```powershell
npm run sitemap
npm run sitemap:seo
```

## 6. Deployment

Das Deployment erfolgt per FTP auf den Webhost.

Vor dem Upload sollten die statischen Website-Dateien, die Sitemaps und die relevanten SEO-Ausgabedateien aktuell sein. Anschließend werden die Dateien per FTP auf den Webserver übertragen.

## 7. Geheimnisse und Zugangsdaten

Diese Angaben nur persönlich übergeben und nicht online veröffentlichen.

Mögliche geheime Werte für dieses Projekt sind:

- `GOOGLE_APPLICATION_CREDENTIALS`
- `SEARCH_CONSOLE_PROPERTY`
- `SITE_ROOT`
- `SITEMAP_PATH`
- `POSTS_PATH`
- `SEO_DB_PATH`
- `HOMEPAGE_PATH`

Wenn weitere API-Schlüssel, Passwörter oder FTP-Zugangsdaten benötigt werden, ebenfalls nur separat und sicher übergeben.

## Kurzüberblick

- Projekt klonen
- Ordner in VS Code öffnen
- Python-Umgebung einrichten und Abhängigkeiten installieren
- Lokale Geheimnisse in einer `.env` oder vergleichbaren Datei pflegen
- Website-Dateien und SEO-Assets per FTP deployen