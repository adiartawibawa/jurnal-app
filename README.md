# Jurnal App

Backend API untuk aplikasi jurnal, dibangun dengan **FastAPI**, **SQLModel**, dan **PostgreSQL**.

Saat ini yang sudah tersedia adalah **sistem akun pengguna**: register, login, logout, lupa password, dan reset password. Fitur jurnal itu sendiri belum dibuat.

## Daftar isi

1. [Fitur dan endpoint](#fitur-dan-endpoint)
2. [Teknologi](#teknologi)
3. [Prasyarat](#prasyarat)
4. [Struktur folder](#struktur-folder)
5. [Menjalankan di komputer sendiri](#menjalankan-di-komputer-sendiri)
6. [Mencoba API lewat /docs](#mencoba-api-lewat-docs)
7. [Pengaturan .env](#pengaturan-env)
8. [Migration database (Alembic)](#migration-database-alembic)
9. [Menambah fitur baru](#menambah-fitur-baru)
10. [Cara kerja autentikasi](#cara-kerja-autentikasi)
11. [Masalah yang sering muncul](#masalah-yang-sering-muncul)
12. [Catatan keamanan](#catatan-keamanan)

---

## Fitur dan endpoint

Semua alamat diawali `/api/v1`.

| Method | Alamat | Wajib login | Fungsi |
|---|---|---|---|
| GET | `/health` | Tidak | Mengecek aplikasi dan koneksi database |
| POST | `/users` | Tidak | Register akun baru |
| POST | `/login/access-token` | Tidak | Login, mengembalikan token |
| POST | `/logout` | Ya | Logout (token yang dipakai dicabut) |
| POST | `/forgot-password` | Tidak | Minta tautan reset password lewat email |
| POST | `/reset-password` | Tidak | Buat password baru memakai token dari email |
| GET | `/users/me` | Ya | Data user yang sedang login |
| GET | `/users/{user_id}` | Ya | Data satu user berdasarkan id |

## Teknologi

| Kebutuhan | Yang dipakai |
|---|---|
| Framework web | FastAPI |
| ORM (akses database) | SQLModel |
| Database | PostgreSQL (driver `psycopg` v3) |
| Migration | Alembic |
| Konfigurasi | pydantic-settings (membaca file `.env`) |
| Hash password | pwdlib (Argon2) |
| Token login | PyJWT |
| Pengelola paket | uv |

## Prasyarat

Pastikan ini sudah terpasang:

- **Python 3.11 atau lebih baru**: cek dengan `python --version`
- **uv**: pengelola paket Python. Panduan pemasangan: <https://docs.astral.sh/uv/>
- **PostgreSQL**: server database yang sudah berjalan
- **Git**

## Struktur folder

```
jurnal-app/
├── README.md
├── .gitignore
└── backend/                 # semua kode Python ada di sini
    ├── main.py              # titik masuk: membuat aplikasi dan memasang router
    ├── alembic.ini          # pengaturan Alembic
    ├── pyproject.toml       # daftar dependensi
    ├── uv.lock              # versi persis dependensi (jangan diedit manual)
    ├── .env.example         # contoh isi .env (aman di-commit)
    ├── .env                 # isi sebenarnya, RAHASIA (tidak di-commit)
    │
    ├── api/                 # lapisan HTTP
    │   ├── router.py        # menggabungkan semua router
    │   ├── deps.py          # dependency bersama (sesi database, user yang login)
    │   └── routes/          # satu file per kelompok endpoint
    │       ├── health.py
    │       ├── login.py     # login, logout, forgot/reset password
    │       └── users.py     # register, /users/me, /users/{id}
    │
    ├── schemas/             # bentuk data masuk/keluar API (apa yang boleh dikirim/dilihat klien)
    │   ├── auth.py
    │   ├── token.py
    │   └── user.py
    │
    ├── crud/                # fungsi yang membaca/menulis database
    │   ├── token.py
    │   └── user.py
    │
    ├── models/              # definisi tabel database
    │   └── models.py
    │
    ├── config/              # pengaturan dan utilitas inti
    │   ├── config.py        # membaca .env
    │   ├── dbase.py         # koneksi database dan sesi
    │   ├── security.py      # hash password dan token JWT
    │   └── email.py         # pengiriman email
    │
    └── migrations/          # riwayat perubahan struktur database (dikelola Alembic)
        ├── env.py
        └── versions/        # satu file per perubahan
```

### Cara kerja satu request

```
Klien -> api/routes (terima request)
              -> schemas (validasi data)
              -> crud (baca/tulis database lewat models)
         <- schemas (bentuk respons)  <- Klien
```

Aturan sederhananya: **route** tidak menulis query sendiri. Route memanggil **crud**, dan crud yang berbicara dengan database.

## Menjalankan di komputer sendiri

> **Penting:** semua perintah di bawah dijalankan dari folder **`backend/`**, bukan dari folder paling luar. File `.env` dan Alembic dibaca relatif terhadap folder tempat perintah dijalankan.

### 1. Ambil kode

```bash
git clone https://github.com/USERNAME/jurnal-app.git   # ganti USERNAME
cd jurnal-app/backend
```

### 2. Pasang dependensi

```bash
uv sync    # membuat folder .venv dan memasang semua paket dari uv.lock
```

### 3. Buat file `.env`

```bash
cp .env.example .env    # di Windows PowerShell: copy .env.example .env
```

Buka `.env`, lalu isi `SECRET_KEY` dan password PostgreSQL. Untuk membuat `SECRET_KEY`:

```bash
uv run python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Salin hasilnya ke `SECRET_KEY=` di `.env`.

### 4. Buat database kosong

Buat database dengan nama yang sama seperti `POSTGRES_DATABASE` di `.env` (bawaan: `jurnal`). Lewat terminal:

```bash
psql -U postgres -c "CREATE DATABASE jurnal;"
```

Atau lewat DBeaver / pgAdmin: klik kanan pada koneksi, lalu *Create Database*.

### 5. Buat tabel lewat migration

```bash
uv run alembic upgrade head    # menjalankan semua migrasi, membuat semua tabel
```

### 6. Jalankan server

```bash
uv run fastapi dev main.py     # --reload otomatis: server restart saat kode diubah
```

Alternatif jika perintah di atas tidak tersedia:

```bash
uv run uvicorn main:app --reload
```

Server berjalan di <http://127.0.0.1:8000>. Cek `http://127.0.0.1:8000/api/v1/health`. Jika muncul `{"status":"ok","database":"connected"}`, semuanya sudah benar.

## Mencoba API lewat /docs

Buka <http://127.0.0.1:8000/docs>. Halaman ini otomatis dibuat FastAPI dan bisa dipakai untuk mencoba endpoint tanpa aplikasi tambahan.

**Alur mencoba dari awal:**

1. **Register**: buka `POST /api/v1/users` → *Try it out* → isi
   ```json
   {
     "email": "saya@example.com",
     "password": "rahasia123",
     "full_name": "Nama Saya"
   }
   ```
   Password minimal 8 karakter.
2. **Login**: klik tombol **Authorize** (kanan atas). Isi `username` dengan **email** Anda dan `password`, lalu *Authorize*.
3. **Coba endpoint yang butuh login**: `GET /api/v1/users/me` seharusnya menampilkan data Anda.
4. **Logout**: `POST /api/v1/logout`. Setelah itu `GET /users/me` dengan token yang sama menghasilkan `401`.

**Mencoba lupa password:**

1. Panggil `POST /api/v1/forgot-password` dengan email Anda.
2. Selama `SMTP_HOST` di `.env` kosong dan `FASTAPI_ENV=development`, isi email **dicetak di terminal** tempat server berjalan. Cari baris `[EMAIL DEV]`, lalu salin nilai setelah `token=`.
3. Panggil `POST /api/v1/reset-password`:
   ```json
   {
     "token": "tempel-token-di-sini",
     "new_password": "passwordbaru456"
   }
   ```
4. Login ulang dengan password baru.

## Pengaturan .env

Contoh lengkap ada di `backend/.env.example`.

| Variabel | Wajib | Keterangan |
|---|---|---|
| `PROJECT_NAME` | Ya | Nama aplikasi (tampil di `/docs` dan subjek email) |
| `SECRET_KEY` | Ya | Kunci rahasia penanda token. Panjang dan acak, jangan dibagikan |
| `DATABASE_URL` | Ya | Alamat database: `postgresql://user:password@host:5432/namadb` |
| `FASTAPI_ENV` | Tidak | Isi `development` di lokal. Pada mode ini email dicetak ke terminal bila SMTP kosong |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Tidak | Masa berlaku token login (bawaan 8 hari) |
| `RESET_TOKEN_EXPIRE_MINUTES` | Tidak | Masa berlaku token reset password (bawaan 15 menit) |
| `FRONTEND_URL` | Tidak | Alamat frontend untuk tautan di email reset (bawaan `http://localhost:3000`) |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_TLS`, `EMAILS_FROM_EMAIL` | Tidak | Pengaturan pengiriman email sungguhan. Kosongkan `SMTP_HOST` untuk mode development |

Catatan: `DATABASE_URL` boleh memakai `${POSTGRES_USERNAME}` dan sejenisnya. Nilainya diganti otomatis dari baris lain di `.env`.

## Migration database (Alembic)

**Migration** adalah catatan perubahan struktur database, mirip riwayat Git untuk tabel. Dengan migration, semua orang (dan server produksi) bisa membuat struktur database yang sama persis lewat satu perintah.

### Perintah yang sering dipakai

```bash
uv run alembic upgrade head      # terapkan semua migrasi yang belum dijalankan
uv run alembic current           # lihat posisi database saat ini
uv run alembic history           # lihat daftar semua migrasi
uv run alembic downgrade -1      # batalkan 1 migrasi terakhir
uv run alembic check             # cek apakah model dan database sudah sinkron
```

### Alur saat mengubah atau menambah tabel

1. Ubah atau tambah model di `models/models.py`.
2. **Model baru wajib didaftarkan** di `migrations/env.py`, pada baris impor model:
   ```python
   from models.models import NamaModelBaru, RevokedToken, User  # noqa: F401
   ```
3. Buat file migrasi otomatis:
   ```bash
   uv run alembic revision --autogenerate -m "pesan singkat tentang perubahan"
   ```
4. **Buka file baru di `migrations/versions/` dan baca isinya.** Pastikan sesuai yang Anda maksud. Jika isi `upgrade()` hanya `pass`, berarti perubahan tidak terdeteksi (biasanya lupa langkah 2).
5. Terapkan:
   ```bash
   uv run alembic upgrade head
   ```
6. Commit file migrasi ke Git bersama perubahan modelnya.

> **Jangan** mengedit file migrasi lama yang sudah dijalankan atau di-push. Buat migrasi baru.

## Menambah fitur baru

Contoh: menambah fitur "jurnal". Ikuti urutan ini, dari bawah ke atas:

1. **Model** → tambah class tabel di `models/models.py`, daftarkan di `migrations/env.py`, lalu buat dan jalankan migrasi.
2. **Schema** → buat `schemas/journal.py` berisi bentuk data request dan response.
3. **CRUD** → buat `crud/journal.py` berisi fungsi akses database. Beri komentar pada setiap fungsi.
4. **Route** → buat `api/routes/journal.py`. Jika endpoint wajib login, pakai `current_user: CurrentUser` dari `api/deps.py`.
5. **Daftarkan** router di `api/router.py`:
   ```python
   from api.routes import health, journal, login, users

   api_router.include_router(journal.router)
   ```
6. Jalankan server dan coba di `/docs`.

Menambah paket baru: `uv add nama-paket` (otomatis memperbarui `pyproject.toml` dan `uv.lock`; commit keduanya).

## Cara kerja autentikasi

- **Password** tidak pernah disimpan apa adanya. Yang disimpan adalah hash Argon2.
- **Login** menghasilkan token JWT yang dikirim klien di setiap request: `Authorization: Bearer <token>`.
- **Logout**: id unik token (`jti`) dicatat di tabel `revokedtoken`, lalu token itu ditolak. Hanya token yang dipakai yang dicabut; login di perangkat lain tetap hidup.
- **Lupa password**: server mengirim email berisi tautan dengan token khusus (berlaku 15 menit). Respons endpoint selalu sama, baik email terdaftar maupun tidak, agar orang lain tidak bisa menebak email yang punya akun.
- **Reset password** hanya bisa dipakai **sekali**. Setelah password diganti, token reset tersebut dan **semua token login lama** otomatis tidak berlaku.
- Token reset dan token login tidak bisa saling menggantikan.

## Masalah yang sering muncul

| Gejala | Penyebab dan solusi |
|---|---|
| `ValidationError ... Field required` saat server dijalankan | File `.env` tidak ditemukan atau ada isian wajib yang kosong. Pastikan perintah dijalankan dari folder `backend/` dan `.env` ada di sana |
| `ModuleNotFoundError: No module named 'config'` | Perintah dijalankan dari folder yang salah. Pindah ke `backend/` |
| `connection refused` ke `localhost:5432` | Server PostgreSQL belum berjalan |
| `password authentication failed` | User atau password di `DATABASE_URL` salah. Karakter khusus pada password (`@`, `#`, `/`, `:`) harus di-encode, misalnya `@` menjadi `%40` |
| `database "jurnal" does not exist` | Database belum dibuat. Lihat langkah 4 |
| `relation "user" does not exist` / `relation "revokedtoken" does not exist` | Migrasi belum dijalankan. Jalankan `uv run alembic upgrade head` |
| `NameError: name 'sqlmodel' is not defined` saat migrasi | File migrasi tidak memuat `import sqlmodel`. Tambahkan di bawah `import sqlalchemy as sa`, juga pada `migrations/script.py.mako` agar migrasi berikutnya benar |
| Alembic tidak mendeteksi tabel baru | Model belum diimpor di `migrations/env.py` |
| `401 Unauthorized` | Token kedaluwarsa, sudah logout, atau password sudah diganti. Login ulang |
| `422 Unprocessable Entity` | Data yang dikirim tidak sesuai aturan (misalnya password kurang dari 8 karakter). Isi respons menjelaskan bagian mana yang salah |
| `409 Conflict` saat register | Email sudah terdaftar |

## Catatan keamanan

- **Jangan pernah commit file `.env`.** Isinya password database dan `SECRET_KEY`. File ini sudah masuk `.gitignore`.
- Jika `.env` pernah ter-push ke GitHub, anggap isinya bocor: ganti password database dan `SECRET_KEY`, karena menghapus file saja tidak menghapus riwayat Git.
- Gunakan `SECRET_KEY` yang berbeda untuk lokal dan produksi.
- Belum ada pembatasan jumlah permintaan (rate limiting). Sebelum dipakai publik, tambahkan terutama pada `login` dan `forgot-password`.
- Belum ada verifikasi email saat register.
- Belum ada tes otomatis.
