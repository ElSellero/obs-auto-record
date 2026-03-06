# Netflix Aufnahme-Planer

Nimm Netflix-Sendungen automatisch mit OBS auf - geplant oder sofort.
Einfache Web-Oberflaeche, kein technisches Wissen noetig.

## Was macht dieses Programm?

Du gibst eine Netflix-URL ein, stellst die Uhrzeit und Dauer ein, und das Programm:
1. Oeffnet Netflix in Firefox zur eingestellten Zeit
2. Startet OBS und beginnt die Bildschirmaufnahme
3. Stoppt die Aufnahme nach der eingestellten Dauer
4. Verhindert, dass der Mac einschlaeft

## Voraussetzungen

- Mac mit Apple M1/M2 Chip (macOS)
- Internetverbindung

## Einrichtung (einmalig, fuer den Einrichter)

### 1. Benoetigte Programme installieren

Terminal oeffnen (Spotlight: "Terminal") und ausfuehren:

```bash
cd ~/Downloads/obs-auto-record   # oder wo der Ordner liegt
bash setup.sh
```

Das Script installiert automatisch fehlende Programme (Homebrew, Python, etc.)
und fragt, ob OBS und Firefox installiert werden sollen.

### 2. OBS Studio konfigurieren

1. **OBS oeffnen**
2. **Scene erstellen:** Unten links bei "Scenes" auf + klicken
3. **Display Capture hinzufuegen:**
   - Bei "Sources" auf + klicken
   - "Display Capture" (oder "Bildschirmaufnahme") waehlen
   - OK klicken
4. **WebSocket aktivieren:**
   - Menu: Tools > WebSocket Server Settings
   - Haken bei "Enable WebSocket Server"
   - Passwort merken oder ein eigenes setzen
   - OK klicken
5. **Aufnahmeformat einstellen:**
   - Menu: Settings (oder OBS > Preferences)
   - Reiter "Output"
   - Recording Format: **mp4**
   - OK klicken
6. **Bildschirmaufnahme erlauben:**
   - macOS fragt beim ersten Mal nach der Berechtigung
   - Systemeinstellungen > Datenschutz > Bildschirmaufnahme > OBS erlauben

### 3. Firefox vorbereiten

1. Firefox oeffnen
2. netflix.com aufrufen und einloggen
3. Das richtige Profil auswaehlen
4. Firefox kann danach geschlossen werden

## Benutzung

### Programm starten

Im Finder auf **`start.command`** doppelklicken.

(Beim ersten Mal: Rechtsklick > Oeffnen, da macOS unbekannte Scripts blockiert)

Ein Terminal-Fenster oeffnet sich und der Browser zeigt die Aufnahme-Oberflaeche.

### Aufnahme einrichten

1. **Netflix URL:** Den Link zur Sendung einfuegen
   - Aus der Firefox-Adressleiste kopieren (z.B. `https://www.netflix.com/title/82157128`)
   - Oder nur den Pfad: `/title/82157128`
2. **Modus:** "Sofort starten" oder eine Uhrzeit einstellen
3. **Dauer:** Wie lange aufgenommen werden soll (in Minuten)
4. **OBS Passwort:** Das Passwort aus den OBS WebSocket-Einstellungen
5. **Button klicken** und fertig!

### Wichtig waehrend der Aufnahme

- **MacBook offen lassen** (Deckel nicht zuklappen!)
- Das Terminal-Fenster nicht schliessen
- Der Mac darf nicht in den Ruhezustand gehen (wird automatisch verhindert)

## Wo sind die Aufnahmen?

OBS speichert die Aufnahmen standardmaessig im Home-Ordner unter **Videos**
oder im Ordner, der in OBS unter Settings > Output > Recording Path eingestellt ist.

Typischer Pfad: `~/Movies` oder `~/Videos`

## Fehlerbehebung

| Problem | Loesung |
|---------|---------|
| "start.command" laesst sich nicht oeffnen | Rechtsklick > "Oeffnen" waehlen |
| OBS-Verbindung fehlgeschlagen | OBS manuell starten, WebSocket-Server pruefen |
| Schwarzes Bild in der Aufnahme | Bildschirmaufnahme-Berechtigung fuer OBS pruefen |
| Netflix zeigt schwarzes Bild | Firefox benutzen (nicht Chrome/Safari) |
| Mac geht in Ruhezustand | Deckel offen lassen, Netzteil anschliessen |
| Aufnahme startet nicht | OBS WebSocket Passwort pruefen |
