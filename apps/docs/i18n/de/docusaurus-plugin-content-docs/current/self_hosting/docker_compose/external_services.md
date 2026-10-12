---
sidebar_position: 3
sidebar_label: Externe Dienste
description: "Ersetzen Sie Garage und Keycloak aus dem Paket durch eigenen S3-Speicher und eigenes Keycloak, binden Sie SMTP an und schalten Sie optionale Integrationen ein."
---

# Externe Dienste

Im Auslieferungszustand betreibt das Paket alles selbst. Sie können den mitgelieferten Objektspeicher und den mitgelieferten Anmeldeserver durch eigene ersetzen, einen E-Mail-Server anbinden und optionale Integrationen einschalten. All das stellen Sie in `.env` ein; übernehmen Sie jede Änderung mit:

```bash
docker compose up -d
```

Die mitgelieferten Komponenten wählen Sie mit `COMPOSE_PROFILES`:

| Profil | Komponente |
|---|---|
| `garage` | Mitgelieferter S3-Objektspeicher. Entfernen Sie das Profil, um Ihren eigenen S3-Speicher zu verwenden. |
| `keycloak` | Mitgelieferter Anmeldeserver. Entfernen Sie das Profil, um Ihr eigenes Keycloak zu verwenden. |
| `backup` | Nächtliche Backups (siehe [Backups](./operations.md#backups)). |

Die Vorgabe ist `COMPOSE_PROFILES=garage,keycloak`.

## Eigener S3-Speicher {#s3}

GOAT speichert hochgeladene Dateien in einem S3-Bucket und Profilbilder und Bilder in einem zweiten, öffentlich lesbaren Bucket. Jeder S3-kompatible Speicher ist geeignet.

:::tip Vor dem ersten Start entscheiden
Richten Sie Ihren eigenen Speicher ein, bevor Sie GOAT zum ersten Mal starten. Daten, die bereits im mitgelieferten Garage liegen, werden nicht in Ihren Speicher übertragen.
:::

### 1. Buckets vorbereiten {#s3-buckets}

- **Upload-Bucket** (`S3_BUCKET_NAME`, Vorgabe `goat-uploads`). Browser laden Dateien direkt in diesen Bucket hoch, daher müssen seine CORS-Regeln `PUT` mit einem `Content-Type`-Header von der GOAT-URL erlauben. Das mitgelieferte Garage verwendet diese Regel, die Sie anpassen können:

  ```json
  [
    {
      "AllowedOrigins": ["https://goat.example.org"],
      "AllowedMethods": ["GET", "HEAD", "PUT"],
      "AllowedHeaders": ["*"],
      "ExposeHeaders": ["ETag"],
      "MaxAgeSeconds": 3600
    }
  ]
  ```

- **Assets-Bucket** (`ASSETS_BUCKET_NAME`, Vorgabe `goat-assets`) für Profilbilder und Bilder. Er muss ohne Zugangsdaten unter der Adresse lesbar sein, die Sie als `ASSETS_URL` eintragen.

Auf beide Buckets wird mit demselben Zugangsschlüssel zugegriffen.

### 2. `.env` einrichten {#s3-env}

Entfernen Sie `garage` aus `COMPOSE_PROFILES` und setzen Sie:

| Einstellung | Bedeutung |
|---|---|
| `S3_ENDPOINT_URL` | Der S3-Endpunkt, wie der Server ihn erreicht, z. B. `https://s3.example.org` |
| `S3_PUBLIC_ENDPOINT_URL` | Der S3-Endpunkt, wie Browser ihn erreichen; Upload-Links zeigen hierhin |
| `S3_REGION` | Die Region, z. B. `eu-central-1` |
| `S3_BUCKET_NAME` | Der Upload-Bucket |
| `S3_FORCE_PATH_STYLE` | `true` für Adressen im Pfad-Stil (`endpunkt/bucket/key`), `false` für den Virtual-Hosted-Stil (`bucket.endpunkt/key`) |
| `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY` | Ihr Zugangsschlüssel. Ersetzen Sie die Werte, die `setup.sh` für Garage erzeugt hat. |
| `ASSETS_S3_ENDPOINT_URL` | Endpunkt des Assets-Buckets; Vorgabe ist `S3_ENDPOINT_URL` |
| `ASSETS_BUCKET_NAME` | Der Assets-Bucket |
| `ASSETS_URL` | Öffentliche Adresse des Assets-Buckets, z. B. `https://assets.example.org` |

`GARAGE_RPC_SECRET` und `GARAGE_ADMIN_TOKEN` werden ohne das mitgelieferte Garage nicht verwendet.

## Eigenes Keycloak {#keycloak}

GOAT kann statt des mitgelieferten Keycloak ein Keycloak verwenden, das Sie bereits betreiben.

### Anforderungen an den Client {#keycloak-client}

Legen Sie in Ihrem Realm einen Client für GOAT mit diesen Einstellungen an:

| Einstellung | Wert |
|---|---|
| Client-Typ | Vertraulich (Client-Authentifizierung an), mit aktiviertem Standard Flow |
| Valid redirect URIs | `<GOAT-URL>/*`, z. B. `https://goat.example.org/*` |
| Web origins | `<GOAT-URL>` |
| Service-Account | Aktiviert, mit den `realm-management`-Rollen **`view-users`** und **`manage-users`** |

GOAT verwendet den Service-Account, um Benutzerkonten zu lesen, Name und E-Mail-Adresse eines Benutzers in Keycloak mit seinem GOAT-Profil abzugleichen und ein Konto zu löschen, wenn sein Benutzer es in GOAT löscht.

### `.env` einrichten {#keycloak-env}

Entfernen Sie `keycloak` aus `COMPOSE_PROFILES` und setzen Sie:

| Einstellung | Bedeutung |
|---|---|
| `KEYCLOAK_PUBLIC_URL` | Keycloak, wie Browser es erreichen, z. B. `https://login.example.org` |
| `KEYCLOAK_INTERNAL_URL` | Keycloak, wie die GOAT-Container es erreichen; oft dieselbe URL |
| `REALM_NAME` | Ihr Realm |
| `KEYCLOAK_CLIENT_ID` | Die Client-ID |
| `KEYCLOAK_CLIENT_SECRET` | Das Client-Secret. Ersetzen Sie den Wert, den `setup.sh` erzeugt hat. |

Beide URLs enthalten den relativen Pfad Ihres Keycloak, falls es einen verwendet, etwa `/auth`: `https://login.example.org/auth`.

:::info Der erste Administrator und smoke.sh
Mit Ihrem eigenen Keycloak legt GOAT dort keinen Benutzer an. `smoke.sh` meldet sich mit `GOAT_ADMIN_EMAIL` und `GOAT_ADMIN_PASSWORD` über eine direkte Passwort-Anmeldung an. Damit das funktioniert, setzen Sie beide auf einen bestehenden Benutzer Ihres Realms und aktivieren Sie *Direct access grants* am Client.
:::

Verwendet Ihr Keycloak ein Zertifikat einer privaten CA, lesen Sie [Firmen-CA](./https.md#company-ca).

## E-Mail {#email}

GOAT versendet Einladungen und Keycloak E-Mails zum Zurücksetzen des Passworts über **einen SMTP-Server**. E-Mail ist ausgeschaltet, solange `SMTP_HOST` leer ist.

| Einstellung | Bedeutung |
|---|---|
| `SMTP_HOST`, `SMTP_PORT` | Der Mailserver, z. B. `smtp.example.org` und `587` |
| `SMTP_SECURITY` | `starttls` (meist Port 587), `ssl` (meist Port 465) oder `none` (z. B. ein internes Relay auf Port 25) |
| `SMTP_USER`, `SMTP_PASSWORD` | Die Anmeldedaten. Lassen Sie beide leer für ein Relay, das E-Mails ohne Anmeldung annimmt. |
| `SMTP_FROM` | Absenderadresse. Vorgabe ist `SMTP_USER`, daher ist sie für ein Relay ohne Anmeldung Pflicht. |
| `EMAILS_FROM_NAME` | Absendername, Vorgabe `GOAT` |

Zum Beispiel ein Relay in Ihrem Netz:

```bash
SMTP_HOST=mail.internal.example.org
SMTP_PORT=25
SMTP_SECURITY=none
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=goat@example.org
```

Führen Sie nach einer Änderung von `SMTP_SECURITY` einmal `./setup.sh` aus: Es leitet die beiden Schalter `SMTP_STARTTLS` und `SMTP_SSL` ab, die Keycloak benötigt. Übernehmen Sie die Änderung dann mit `docker compose up -d`.

Mit `starttls` oder `ssl` prüfen GOAT und Keycloak das Zertifikat des Relays gegen die öffentlichen Zertifizierungsstellen. Stammt das Zertifikat Ihres Relays von einer Firmen-CA, setzen Sie `GOAT_CA_BUNDLE` wie unter [Firmen-CA](./https.md#company-ca) beschrieben; sonst schlägt der Versand mit einem Zertifikatsfehler fehl.

:::info Ein Ort für die E-Mail-Einstellungen
Das mitgelieferte Keycloak verwendet dieselben SMTP-Einstellungen: Bei jedem `docker compose up -d` überträgt der Schritt `keycloak-sync` sie aus `.env` in den Realm. Ändern Sie sie nur in `.env`; Änderungen in der Keycloak-Admin-Konsole unter *Realm settings → Email* werden beim nächsten Start ersetzt.
:::

### E-Mail-Branding {#email-branding}

Standardmäßig zeigen die E-Mails von GOAT und von Keycloak den Namen `GOAT` und keine Links in der Fußzeile. Mit diesen optionalen Einstellungen fügen Sie in beiden Ihre eigenen hinzu:

| Einstellung | Bedeutung |
|---|---|
| `EMAIL_BRAND_NAME` | Name, der in den E-Mails erscheint |
| `EMAIL_LOGO_URL` | Adresse eines Logo-Bildes, das statt des Namens erscheint |
| `EMAIL_CONTACT_URL` | Kontakt-Link in der Fußzeile. Die App verwendet ihn auch für ihre <code>Kontakt</code>-Links. |
| `EMAIL_PRIVACY_URL` | Link zur Datenschutzerklärung in der Fußzeile. Auch die Anmeldeseite verlinkt darauf. |

Die Bilder in den E-Mails kommen von GOATs öffentlicher URL (`<öffentliche URL>/assets`) oder von `STATIC_ASSETS_URL`, falls gesetzt. Die Mailprogramme der Empfänger laden sie von dort, die Adresse muss für sie also erreichbar sein.

## Support-Tickets {#support}

GOAT kann Problemmeldungen und Fragen seiner Benutzer an einen Odoo-Helpdesk weiterreichen, wo sie als Tickets mit Antworten erscheinen. Das ist optional und **standardmäßig aus**. Ohne diese Einstellungen zeigt *Problem melden* in der App eine E-Mail-Adresse und den Link *Dokumentation*, und die Routen unter `/api/v2/support` existieren nicht. Die Adresse ist standardmäßig `support@plan4better.de`; Ihre eigene legen Sie mit `NEXT_PUBLIC_SUPPORT_EMAIL` fest, siehe [Konfigurationsreferenz](./configuration.md#integrations).

| Einstellung | Bedeutung |
|---|---|
| `ODOO_URL` | Adresse des Odoo, z. B. `https://odoo.example.org`. Gemeinsam für GOATs Odoo-Anbindungen. |
| `ODOO_DB` | Die Odoo-Datenbank. Gemeinsam für GOATs Odoo-Anbindungen. |
| `ODOO_SUPPORT_API_KEY` | API-Schlüssel des Support-Benutzers in diesem Odoo. Er ist ein Geheimnis. |
| `ODOO_SUPPORT_TEAM_ID` | Numerische ID des Helpdesk-Teams, das die Tickets erhält |
| `ODOO_SUPPORT_POST_ACTION` | Optional. Name der Odoo-Serveraktion, die eine Nachricht als Teilnehmer des Tickets veröffentlicht. Vorgabe `GOAT: post message as ticket participant`. |

Support-Tickets sind nur eingeschaltet, wenn die ersten vier Einstellungen alle gesetzt sind; ist eine davon leer, bleiben sie aus. Den API-Schlüssel stellt Plan4Better für sein eigenes Odoo aus. Lassen Sie auf Ihrer eigenen Installation alle vier leer, es sei denn, Sie haben einen erhalten.

Nachrichten zu einem Ticket können Anhänge von bis zu 55 MiB in einer Anfrage enthalten. Das mitgelieferte Caddy setzt keine Grenze für Anfragekörper. Stellen Sie einen eigenen Proxy oder Load Balancer davor, muss er für `/api/v2/support` Anfragekörper von mindestens 56 MB annehmen und großzügige Lese-Timeouts erlauben.

## Ohne Anmeldung {#no-login}

Für lokale Tests und Demos kann GOAT ganz ohne Anmeldung laufen:

```bash
AUTH=False
```

Alle, die GOAT öffnen, handeln dann als ein eingebauter Administrator.

:::warning
Mit `AUTH=False` hat jeder, der die URL erreicht, vollen Zugriff auf alle Daten. Verwenden Sie diese Einstellung nur für lokale oder Demo-Installationen.
:::

## Optionale Integrationen {#integrations}

GOAT funktioniert ohne jede dieser Integrationen. Jede schaltet eine Funktion frei, die einen externen Dienst benötigt.

| Einstellung | Was sie freischaltet | Ohne sie |
|---|---|---|
| `NEXT_PUBLIC_MAPTILER_KEY` | Die Satelliten-/Hybrid-Grundkarte von MapTiler | Diese Grundkarte wird ausgeblendet; die anderen Grundkarten funktionieren |
| `NEXT_PUBLIC_MAPBOX_TOKEN` | Die Ortssuche im Suchfeld der Karte (über Mapbox) | Das Suchfeld findet keine Orte |
| `CATALOG_S3_BUCKET`, `CATALOG_S3_ENDPOINT_URL`, `CATALOG_S3_ACCESS_KEY_ID`, `CATALOG_S3_SECRET_ACCESS_KEY`, `CATALOG_S3_REGION` | Den GOAT-Datenkatalog: ein schreibgeschützter Bucket mit den harmonisierten Datensätzen, der regelmäßig gespiegelt wird | Der Katalog bleibt leer, und seine Synchronisierung ist ausgeschaltet |
| `GEOCODING_URL`, `GEOCODING_AUTHORIZATION` | Den Geocoding-Dienst, den Analyse-Werkzeuge verwenden | Analyseschritte, die Geocoding benötigen, können nicht laufen |
| `OTEL_ENABLED`, `OTEL_EXPORTER_OTLP_ENDPOINT` | Den Export von Traces, Metriken und Logs an Ihren OpenTelemetry-Collector | Es wird nichts exportiert |

Die Links, die in der App erscheinen, und die Quelle der Produktgrafiken finden Sie in der [Konfigurationsreferenz](./configuration.md#integrations). Die Quelle der Routing-Basisdaten ist unter [Routing-Basisdaten](./operations.md#base-data) beschrieben.
