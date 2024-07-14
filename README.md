# Verifikacija govornika (speaker-verification-desktop-app)

Ovaj projekt predstavlja desktop aplikaciju za simuliranje rada prepoznavanja govornika na temelju audio zapisa. Cilj aplikacije je utvrditi koliko dobro dobiveni modeli rade u stvarnoj primjeni. Aplikacija se sastoji od dva dijela: "Prepoznavanje govornika" i "Upravljanje korisnicima". Prepoznavanje govornika - vrši simulaciju usporedbe snimljenog audio zapisa sa zapisima korisnika u bazi kako bi se odredio identitet. Upravljanje korisnicima - odnosi se na dodavanje, prikaz i uklanjanje korisnika iz baze podataka.

## Korištene tehnologije i biblioteke

Aplikacija je izrađena korištenjem programskog jezika Python3. Uz Python korištena je MySQL baza podataka za pohranu informacija o korisnicima, koja je pokrenuta koristeći MariaDB poslužitelj. Za ostvarenje navedenog korištene su razne vanjske biblioteke koje su navedene u nastavku uz njihove instalacijske naredbe:

MySQLdb

```bash
pip install mysqlclient
```

PyQt5

```bash
pip install PyQt5
```

librosa

```bash
pip install librosa
```

numpy

```bash
pip install numpy
```

sounddevice

```bash
pip install sounddevice
```

matplotlib

```bash
pip install matplotlib
```

scikit-image

```bash
pip install scikit-image
```

tensorflow

```bash
pip install tensorflow
```

## Pokretanje

Budući da projekt koristi bazu podataka, potrebno je istu pokrenuti i stvoriti tablicu ukoliko ona već ne postoji. Ukoliko je baza uspostavljena, potrebno je pokrenuti glavnu Python skriptu _main_menu.py_.

### 1. Podešavanje baze podataka:

Prvo je potrebno instalirati MariaDB poslužitelj.

```bash
sudo apt-get install mariadb-server
```

Nakon toga potrebno je pokrenuti poslužitelj:

```bash
sudo service mysql start
```

Nadalje, potrebno je prijaviti se:

```bash
sudo mysql -u root -p "newpassword"
```

Ukoliko je prijava uspješna, potrebno je stvoriti bazu _speaker_verification_, ako ista ne postoji.

```bash
CREATE DATABASE speaker_verification;
```

Zatim odaberemo navedenu bazu.

```bash
USE speaker_verification;
```

Kreiramo tablicu _govornici_ u koju će se spremati korisnici:

```bash
CREATE TABLE govornici (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ime VARCHAR(100) NOT NULL,
    prezime VARCHAR(100) NOT NULL,
    spektrogram_url VARCHAR(255) NOT NULL
);
```

### 2. Pokretanje aplikacije:

Ukoliko je baza podataka pokrenuta, desktop aplikacija se pokreće pokretanjem glavne skripte _main_menu.py_.

Aplikaciju je moguće pokrenuti izvršavanjem naredbe:

```bash
python3 ./main_menu.py
```
