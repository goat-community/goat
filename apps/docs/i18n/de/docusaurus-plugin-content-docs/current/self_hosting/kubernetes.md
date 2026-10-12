---
sidebar_position: 3
sidebar_label: Kubernetes (Helm)
description: "Installieren Sie GOAT mit dem Helm-Chart und legen Sie fest, was es offenlässt: öffentliche URLs, S3-Speicher, Anmeldung, Analyse-Worker und RWX-Speicher."
---

# Kubernetes (Helm)

Für Kubernetes-Cluster gibt es ein Helm-Chart für GOAT, veröffentlicht unter `oci://ghcr.io/plan4better/charts/goat`. Diese Seite fasst zusammen, was das Chart enthält und was Sie bereitstellen müssen. Die [README des Charts](https://github.com/plan4better/goat/tree/main/deploy/helm/goat) ist die vollständige Referenz aller Values.

:::tip Ein Server? Nutzen Sie Docker Compose
Für einen einzelnen Server ist das [Docker-Compose-Paket](./docker_compose/installation.md) der empfohlene Weg. Es enthält den Anmeldeserver, den Objektspeicher und HTTPS, die das Helm-Chart Ihnen überlässt.
:::

Diese Seite beschreibt die Chart-Version **0.6.0**, die standardmäßig GOAT **v3.0.3** installiert.

## Installation {#install}

```bash
helm install goat oci://ghcr.io/plan4better/charts/goat \
  --version 0.6.0 \
  --namespace goat --create-namespace \
  --values your-values.yaml \
  --wait --timeout 25m
```

Eine erste Installation lädt mehrere große Images, daher der lange Timeout. Ein frischer Cluster benötigt nur diesen einen Befehl.

## Was das Chart enthält {#included}

| Komponente | Vorgabe |
|---|---|
| core, web, geoapi, processes, catalog | an |
| Windmill-Server und der Standard-Worker | an |
| Windmill-Worker `tools`, `workflows` und `print` | **aus** |
| PostgreSQL über CloudNativePG (Operator und Cluster) | an, optionales Sub-Chart |
| Redis | an, optional |
| Ein gemeinsames Daten-Volume (`data`, 200 Gi, `ReadWriteOnce`) | an |
| Caddy für eigene Domains | aus |

Das Chart enthält **nicht**:

- **Objektspeicher.** GOAT benötigt einen externen S3-kompatiblen Speicher.
- **Keycloak.** Wenn sich Benutzer anmelden sollen, benötigen Sie ein externes Keycloak.

Statt der mitgelieferten Instanzen können Sie das Chart auch auf ein bestehendes PostgreSQL oder Redis richten; die README des Charts listet das SQL auf, das Ihr PostgreSQL benötigt.

## Was Sie einstellen müssen {#required-values}

### Öffentliche URLs {#public-urls}

Der Browser ruft core, geoapi, processes und catalog direkt auf, deshalb benötigt die Web-App deren öffentliche Adressen. Geben Sie jedem Dienst ein Ingress mit Host (`<service>.ingress.*`), dann werden die URLs daraus abgeleitet, oder setzen Sie sie ausdrücklich in `web.publicUrls.api`, `.geoapi`, `.processes` und `.catalog`.

:::warning
Ohne diese URLs zeigt die Web-App eine leere Seite.
:::

### Objektspeicher {#storage}

Beschreiben Sie Ihren S3-Speicher einmal in `global.s3`: den Bucket für Uploads, Anbieter, Endpunkt, Region, ob der Speicher Pfad-URLs (path style) braucht, und ein Secret mit dem Zugangsschlüssel-Paar (`global.s3.existingSecret`). core, geoapi, processes und die Analyse-Worker (siehe unten) erhalten alle diese Einstellungen.

Hochgeladene Bilder, etwa Vorschaubilder von Projekten und Datensätzen, Profilbilder und Bilder in Dashboards, liegen in einem zweiten Bucket desselben Speichers (`global.s3.assets.bucket`). Browser laden sie direkt aus diesem Bucket; machen Sie ihn deshalb öffentlich lesbar und tragen Sie seine öffentliche URL in `global.s3.assets.publicUrl` ein. Außerhalb von AWS ist die URL Pflicht. GOATs eigene Grafiken liefert die Web-App selbst aus; sie brauchen beides nicht.

### Anmeldung {#auth}

Die Anmeldung ist standardmäßig **aus** (`global.auth.enabled: false`): Alle Dienste handeln dann als ein Standardbenutzer, stellen Sie eine solche Installation also hinter Ihre eigene Zugriffskontrolle. Um die Anmeldung einzuschalten, setzen Sie `global.auth.enabled: true` und `global.auth.existingSecret` auf ein Secret mit den Schlüsseln `server-url`, `realm`, `client-id`, `client-secret` und `nextauth-secret`. Ein Secret versorgt alle fünf Dienste.

### E-Mail und Einladungen {#email}

- **`email`** legt den SMTP-Server fest, über den core Einladungen verschickt, mit dem Passwort aus einem Secret (`email.existingSecret`). Die Links in diesen E-Mails entstehen aus den öffentlichen URLs von Web-App und API.
- **Keycloak** verschickt seine eigenen E-Mails, etwa zum Zurücksetzen des Passworts, mit den SMTP-Einstellungen seines Realms. Tragen Sie dort denselben Server ein.
- **`global.auth.provisionInvitedUsers: true`** lässt eine Einladung das Keycloak-Konto anlegen, und Keycloak schickt einen Link zum Setzen des Passworts. Nutzen Sie es, wenn Ihr Realm keine Selbstregistrierung erlaubt. Der Keycloak-Client von core braucht dann die realm-management-Rollen `view-users` und `manage-users`.
- **`global.caBundle`** nennt eine ConfigMap oder ein Secret mit dem Zertifikat einer eigenen CA, für ein SMTP-Relay, ein Keycloak oder Seiten, die der Druck-Worker öffnet, deren Zertifikat von einer privaten CA stammt. Das Chart bindet es in core, die Web-App und die Worker `print`, `tools` und `workflows` ein.

### Support-Tickets {#support}

Optional und **standardmäßig aus**. Support-Tickets reichen Problemmeldungen Ihrer Benutzer an einen Odoo-Helpdesk weiter. Der Block `odoo` enthält die Verbindung (`odoo.url`, `odoo.db`), `odoo.support` das Helpdesk-Team (`odoo.support.teamId`) und den API-Schlüssel aus einem Secret (`odoo.support.existingSecret`). Die Tickets sind nur eingeschaltet, wenn all das gesetzt ist. Den Schlüssel stellt Plan4Better für sein eigenes Odoo aus; lassen Sie den Block auf Ihrer eigenen Installation leer, es sei denn, Sie haben einen erhalten.

Ohne Tickets öffnet *Problem melden* eine E-Mail an die Adresse in `web.supportEmail`; sie steht auch in der Meldung, wenn der Support vorübergehend nicht erreichbar ist. Standard ist `support@plan4better.de`; tragen Sie für eine White-Label-Installation Ihre eigene Adresse ein.

Nachrichten zu einem Ticket können Anhänge von bis zu 55 MiB in einer Anfrage enthalten. Das Ingress vor core muss für `/api/v2/support` Anfragekörper von mindestens 56 MB annehmen und großzügige Lese-Timeouts erlauben. ingress-nginx begrenzt Anfragekörper standardmäßig auf 1 MB; erhöhen Sie das mit `nginx.ingress.kubernetes.io/proxy-body-size: "56m"` und `proxy-read-timeout` in `core.ingress.annotations`.

### Analyse-Worker {#workers}

Der Standard-Worker von Windmill übernimmt nur kleine Jobs. **Analyse-Werkzeuge, Datensatz-Importe und Workflows benötigen die Worker `tools` und `workflows`, der PDF-Druck benötigt den Worker `print`.** Alle drei sind standardmäßig aus. So nutzen Sie sie:

- Schalten Sie sie mit `windmill.workers.tools.enabled`, `windmill.workers.workflows.enabled` und `windmill.workers.print.enabled` ein.
- Die Worker `tools` und `workflows` sind an Nodes mit dem Label `node.kubernetes.io/server-usage: geodata` und der Toleration `geodata=true:NoSchedule` gebunden. Bereiten Sie solche Nodes vor oder überschreiben Sie `nodeSelector` und `tolerations` für diese Worker. Andernfalls bleiben ihre Pods im Zustand `Pending`, und `helm install --wait` läuft in den Timeout.
- Das Chart gibt diesen Workern, was GOATs Jobs brauchen: die GOAT-Datenbank, den S3-Speicher, den Katalog-Bucket, die Adresse der Web-App für den Druck und, bei eingeschalteter Anmeldung, den Keycloak-Client, mit dem sich der Druck-Worker anmeldet. Windmill reicht nur die Variablen an die Jobs weiter, die in `WHITELIST_ENVS` stehen; das Chart stellt diese Liste zusammen, einschließlich jeder Variable, die Sie in `config` oder `extraEnv` eines Workers ergänzen.
- Schalten Sie `windmill.scriptSync.enabled` ein, um GOATs Analyse-Werkzeuge und Aufgaben nach der Installation in Windmill zu registrieren. Die Einstellung ist standardmäßig aus.

### Speicher für mehrere Nodes {#rwx}

Das gemeinsame Daten-Volume verwendet standardmäßig `ReadWriteOnce`, was auf einem einzelnen Node funktioniert. In einem Cluster mit mehreren Nodes setzen Sie `data.accessMode: ReadWriteMany` mit einer RWX-fähigen Storage-Class (`data.storageClassName`) oder stellen mit `data.existingClaim` Ihren eigenen Claim bereit.

## Weiterführende Informationen {#further-reading}

Die [README des Charts](https://github.com/plan4better/goat/tree/main/deploy/helm/goat) behandelt die Details: die Installation auf einem frischen Cluster, die Einrichtung eines externen PostgreSQL, die Rangfolge der Authentifizierungseinstellungen, das gemeinsame Daten-Volume, die Region, in der neue Projekte öffnen (`DEFAULT_PROJECT_VIEW_STATE`), Schema-Migrationen und die Upgrade-Hinweise zwischen den Chart-Versionen.
