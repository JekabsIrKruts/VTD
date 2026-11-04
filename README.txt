# Vardes Tower Defense

Vardes Tower Defense (VTD) ir torņu aizsardzības spēle. Spēlētājs izvieto un
uzlabo vardes, lai apturētu mušas, pirms tās sasniedz ceļa beigas.

## Spēles iespējas

- 10 viļņi ar dažādiem mušu tipiem; pēdējā vilnī ir Mušu māte.
- Vardes var novietot ārpus ceļa un uzlabot trīs pakāpēs: T1, T2 un T3.
- Jaunu varžu iegādei un uzlabojumiem izmanto spārnus (ω). Par katru ar vardēm
  uzvarētu mušu spēlētājs saņem spārnus.
- Pirms viļņiem ir varžu jautājumi. Izlaists varžu jautājums nākamajā reizē
  tiek aizstāts ar grūtāku mušu jautājumu.
- Pēc piektā viļņa Varžu māte piedāvā apmainīt dzīvības pret spārniem. Ja
  spēlētājam ir pilna veselība, var atdot visas dzīvības, izņemot vienu, un
  iegūt svētību, kas nākamajām mušām samazina HP par 10%.
- Spēlētājam ir 1000 HP. Muša, kas sasniedz ceļa beigas, samazina spēlētāja HP
  par šim mušu tipam iestatīto daudzumu. Punkti samazinās viļņa laikā un tiek
  pieskaitīti kopējam rezultātam pēc viļņa pabeigšanas.
- Spēles beigās rezultātu var saglabāt līderu tabulā, ievadot lietotājvārdu.

## Vadība

Spēli vada ar kreiso peles pogu. Velc izvēlēto vardi uz zaļo laukumu, lai to
novietotu; klikšķini uz novietotas vardes, lai atvērtu tās uzlabojumus. Ar peli
var arī atbildēt uz jautājumiem, atvērt nākamā viļņa plānu un izmantot pauzi.

## Uzstādīšana (Windows PowerShell)

Atver PowerShell projekta mapē `VTD` un izveido virtuālo vidi:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Spēles palaišana

```powershell
.\.venv\Scripts\python.exe -m client.main
```

## API servera palaišana un mājaslapa

Palaižot spēli, tā automātiski ieslēdz API serveri, ja tas vēl nedarbojas.
Palaistais serveris tiek apturēts, kad spēle tiek aizvērta. Ja vēlies atvērt
mājaslapu arī bez spēles, vari serveri palaist atsevišķi:

```powershell
.\.venv\Scripts\python.exe -m uvicorn api.main:app --reload
```

Kamēr serveris darbojas, mājaslapas ir pieejamas pārlūkā:

- Līderu tabula: <http://127.0.0.1:8000/>
- Admin panelis: <http://127.0.0.1:8000/admin>
- API interaktīvā dokumentācija: <http://127.0.0.1:8000/docs>

Spēle nosūta saglabājamo rezultātu uz `http://127.0.0.1:8000/scores`.
Ja spēle nevar sasniegt API, pārbaudi, vai servera logs joprojām darbojas.

### Admin paroles iestatīšana

Uvicorn palaišanai parole nav vajadzīga. Lai ielogotos admin panelī, vienreiz
nokopē paroles paraugu un nomaini tajā parauga vērtību:

```powershell
Copy-Item api\.env.example api\.env
notepad api\.env
```

Paroli ievadi `api/.env` failā pie `VTD_ADMIN_PASSWORD`. Šis lokālais fails ir
iekļauts `.gitignore` un netiek pievienots Git repozitorijam. Pēc paroles
iestatīšanas restartē API serveri un ievadi to admin paneļa paroles laukā.

## API endpointi

| Metode | Ceļš | Apraksts | Veiksmīga atbilde | Citas atbildes |
|---|---|---|---:|---|
| `GET` | `/` | Atver līderu tabulas lapu pārlūkā | 200 | — |
| `GET` | `/admin` | Atver admin paneli pārlūkā | 200 | — |
| `POST` | `/scores` | Saglabā rezultātu; JSON: `{"username":"Varde","score":1234}` | 201 | 422 — nederīgs lietotājvārds vai rezultāts |
| `GET` | `/scores/top` | Atgriež līdz 10 labākajiem rezultātiem JSON formātā | 200 | — |
| `POST` | `/admin/login` | Pārbauda paroli un izveido admin sesiju | 200 | 401 — nepareiza parole; 503 — parole nav iestatīta |
| `POST` | `/admin/logout` | Beidz admin sesiju | 200 | — |
| `GET` | `/admin/scores` | Atgriež visus rezultātus; vajadzīga admin sesija | 200 | 401 — nav ielogots |
| `DELETE` | `/admin/scores/{score_id}` | Dzēš rezultātu pēc ID; vajadzīga admin sesija | 200 | 401 — nav ielogots; 404 — rezultāts nav atrasts |
| `DELETE` | `/admin/scores` | Dzēš visus rezultātus; vajadzīga admin sesija | 200 | 401 — nav ielogots |

## Projekta struktūra

- `game/rules.py` glabā spēles datus un noteikumus, tostarp varžu un mušu jautājumus; tas neimportē Pygame.
- `client/main.py` apstrādā ievadi un zīmē spēles ekrānus ar Pygame.
- `assets/textures/` glabā spēles varžu, mušu un šāviņu attēlus.
- `api/main.py` nodrošina rezultātu API, līderu tabulu un admin paneli.
- `api/db.py` saglabā rezultātus SQLite datubāzē `api/scores.db`.
