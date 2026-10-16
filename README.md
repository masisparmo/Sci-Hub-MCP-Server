# Sci-Hub MCP & API Server

🔍 **Sci-Hub MCP Server** memungkinkan asisten AI seperti **Google Gemini (Spark)**, **ChatGPT**, dan **Claude Desktop** untuk mencari, mengakses metadata, dan mengunduh jurnal/paper ilmiah secara otomatis melalui Model Context Protocol (MCP) dan REST API.

---

## ✨ Fitur Utama

- 🔎 **Pencarian Berdasarkan DOI**: Menemukan metadata lengkap dan tautan unduh PDF langsung dari Sci-Hub.
- 🔍 **Pencarian Berdasarkan Judul**: Mencari nomor DOI melalui CrossRef, lalu menghubungkannya ke Sci-Hub.
- 🔑 **Pencarian Berdasarkan Kata Kunci**: Menemukan kumpulan paper terkait topik/riset tertentu.
- 📊 **Pengambilan Metadata Akurat**: Penulis, tahun terbit, jurnal/penerbit, dan URL PDF.
- 🌐 **Dukungan Multi-Platform (Universal)**:
  - **Google Gemini Spark (Connected Apps)**: Mendukung protokol *Streamable HTTP*.
  - **ChatGPT Custom MCP Server (Plugins)**: Mendukung protokol *Server-Sent Events (SSE)*.
  - **ChatGPT Custom GPT (Actions)**: Mendukung skema *OpenAPI 3.0*.
  - **Klien MCP Desktop**: Claude Desktop & Cursor via `stdio`.

---

## 🚀 Panduan Pemasangan

### 1. Google Gemini Spark (Aplikasi Terhubung / Connected Apps)

Berdasarkan [Panduan Resmi Google Gemini](https://support.google.com/gemini/answer/17209137), Gemini menggunakan protokol **Streamable HTTP**.

1. Buka [gemini.google.com](https://gemini.google.com) di browser komputer Anda.
2. Klik **Setelan (Settings)** di kiri bawah > pilih **Aplikasi Terhubung (Connected Apps)**.
3. Gulir ke bagian **Aplikasi Kustom (Custom Apps)** > klik **Tambahkan aplikasi kustom (Add a custom app)**.
4. Masukkan URL berikut pada kolom **URL Server MCP**:
   ```text
   https://sci-hub-mcp.onrender.com/mcp
   ```
5. Klik **Berikutnya (Next)** dan ikuti konfirmasi di layar.
6. **Cara Penggunaan di Chat**:
   Ketik `@` lalu pilih aplikasi custom Anda, atau langsung tanyakan:
   > *"Tolong carikan paper dengan DOI 10.1038/nature09492 dan berikan tautan PDF-nya."*

---

### 2. ChatGPT (Custom MCP Server / Plugins)

Jika menggunakan fitur integrasi MCP resmi di ChatGPT (Developer Mode / Plugins):

1. Buka [chatgpt.com](https://chatgpt.com).
2. Buka menu **Plugins** atau **Apps** > klik tombol **`+`** atau **Add custom MCP server**.
3. Isi formulir dengan data berikut:
   * **Name**: `Sci-Hub`
   * **Description**: `Cari paper dan unduh PDF jurnal ilmiah`
   * **Connection**: Pilih tab **Server URL**
   * **Server URL**:
     ```text
     https://sci-hub-mcp.onrender.com/sse
     ```
   * **Authentication**: Pilih **`No authentication`** *(PENTING: Jangan pilih OAuth)*
4. Centang pernyataan persetujuan risiko (*I understand and want to continue*).
5. Klik **Create as a plugin**.

---

### 3. ChatGPT (Custom GPT Actions)

Jika Anda membuat Custom GPT sendiri di [ChatGPT GPT Builder](https://chatgpt.com/gpts/editor):

1. Masuk ke tab **Configure** pada Custom GPT Anda.
2. Gulir ke bawah dan klik **Create new action**.
3. Di bagian **Schema**, klik **Import from URL**.
4. Masukkan URL OpenAPI Schema:
   ```text
   https://sci-hub-mcp.onrender.com/openapi.json
   ```
5. Klik **Import**. ChatGPT akan otomatis mendeteksi semua tools (`search_scihub_by_doi`, `search_scihub_by_title`, dll.).
6. Pada kolom **Privacy Policy**, isi: `https://sci-hub-mcp.onrender.com`.

---

### 4. Klien MCP Lokal (Claude Desktop / Cursor)

Jalankan server dalam mode `stdio` di komputer lokal Anda:

```bash
python sci_hub_server.py --stdio
```

Konfigurasi untuk `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "scihub": {
      "command": "python",
      "args": ["d:/Aplikasi/MCP Sci-Hub/sci_hub_server.py", "--stdio"]
    }
  }
}
```

---

## 🛠 Daftar Endpoint Server

| Endpoint | Protokol / Fungsi | Target Klien |
| :--- | :--- | :--- |
| `POST /mcp` | Streamable HTTP Transport | **Google Gemini Connected Apps** |
| `GET /sse` | Server-Sent Events (SSE) | **ChatGPT Plugins / MCP Client** |
| `GET /openapi.json` | OpenAPI 3.0 Schema | **ChatGPT Custom GPT Actions** |
| `GET /docs` | Swagger Interactive UI | Pengujian manual & Dokumentasi |
| `GET /health` | Health Check | Render.com Keep-Alive |
| `POST /api/search_by_doi` | REST Endpoint | Webhook / Aplikasi Umum |
| `POST /api/search_by_title` | REST Endpoint | Webhook / Aplikasi Umum |
| `POST /api/search_by_keyword` | REST Endpoint | Webhook / Aplikasi Umum |
| `POST /api/get_metadata` | REST Endpoint | Webhook / Aplikasi Umum |

---

## ☁️ Deployment ke Render.com

Jika Anda ingin mendeploy instance server sendiri di Render:
1. Hubungkan repositori GitHub ini ke [dashboard.render.com](https://dashboard.render.com).
2. Buat **Web Service** baru:
   * **Runtime**: `Python 3`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `uvicorn sci_hub_server:app --host 0.0.0.0 --port $PORT`
   * **Instance Type**: `Free`
3. Render akan otomatis mendeteksi environment variable `$PORT` dan menyajikan server secara publik.

---

## 📄 Lisensi & Disclaimer

* **Lisensi**: MIT License.
* **Disclaimer**: Alat ini dibuat semata-mata untuk keperluan edukasi dan riset akademis. Harap patuhi hak cipta dan ketentuan hukum yang berlaku di wilayah Anda.
