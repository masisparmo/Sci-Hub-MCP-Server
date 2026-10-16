# Sci-Hub MCP & API Server

🔍 Enable AI assistants (ChatGPT, Gemini, Claude Desktop, Cursor) to search, access, and analyze academic papers through Sci-Hub and CrossRef using a simple MCP interface & OpenAPI endpoints.

The Sci-Hub MCP & API Server provides a bridge between AI assistants and academic literature. It allows AI models to search for scientific articles by DOI, title, or keywords, access their metadata, and retrieve direct PDF links.

---

## ✨ Core Features

- 🔎 **Paper Search by DOI**: Find papers and direct PDF download links using Digital Object Identifier (DOI).
- 🔍 **Paper Search by Title**: Locate papers using their full or partial title via CrossRef metadata resolution.
- 🔑 **Paper Search by Keyword**: Discover papers and research articles related to specific topics.
- 📊 **Metadata Access**: Retrieve detailed metadata (authors, journal, publication year, publisher).
- 🌐 **Cloud Ready**: Configured for instant deployment on **Render.com** (with automatic `$PORT` binding & `/health` endpoint).
- 🤖 **ChatGPT & Gemini Ready**: Exposes `/openapi.json` and interactive Swagger docs at `/docs` for easy setup with ChatGPT Custom GPT Actions and Gemini Function Calling.
- 💻 **MCP Compatible**: Maintains backward compatibility with local MCP clients (`--stdio`).

---

## 🚀 Deployment on Render.com

Deploying to Render takes only 2 minutes:

1. **Fork or Push** this repository to your GitHub account (`masisparmo/Sci-Hub-MCP-Server`).
2. Log into [dashboard.render.com](https://dashboard.render.com).
3. Click **New +** -> **Web Service**.
4. Connect your GitHub repository `masisparmo/Sci-Hub-MCP-Server`.
5. Configure the service settings:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn sci_hub_server:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
6. Click **Create Web Service**.
7. Once deployed, Render will provide a public URL like:
   `https://scihub-mcp-server.onrender.com`

Verify the deployment by visiting `https://<YOUR-RENDER-URL>/docs` in your browser.

---

## 🤖 Integration Guides

### 1. ChatGPT (Custom GPT Actions)

1. Open [ChatGPT](https://chatgpt.com) and go to **Explore GPTs** -> **Create**.
2. Go to the **Configure** tab.
3. Under **Actions**, click **Create new action**.
4. Click **Import from URL** and enter:
   ```
   https://<YOUR-RENDER-URL>/openapi.json
   ```
5. ChatGPT will automatically parse all available tools:
   - `search_scihub_by_doi`
   - `search_scihub_by_title`
   - `search_scihub_by_keyword`
   - `get_paper_metadata`
6. Under **Privacy Policy**, you can provide your base Render URL (`https://<YOUR-RENDER-URL>`).
7. Test the Action in the Preview panel by typing:
   > *"Can you find the paper with DOI 10.1038/nature09492 and give me the summary and PDF link?"*

---

### 2. Google Gemini (Spark / AI Studio / Function Calling)

1. Open [Google AI Studio](https://aistudio.google.com).
2. Create a new prompt or assistant using Gemini 1.5 Pro / Flash.
3. Under **Tools**, enable **Function Calling**.
4. Import the tool schema directly from `https://<YOUR-RENDER-URL>/openapi.json`.
5. You can now prompt Gemini to retrieve academic papers via the server endpoints.

---

### 3. Local Desktop MCP Clients (Claude Desktop, Cursor)

For local desktop usage via stdio, run:

```bash
python sci_hub_server.py --stdio
```

Configuration for `claude_desktop_config.json`:

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

## 📁 Endpoints

- `GET /`: Server status and summary
- `GET /health`: Health check endpoint for Render
- `GET /docs`: Interactive Swagger documentation
- `GET /openapi.json`: OpenAPI 3.0 specification
- `POST /api/search_by_doi`: Search by DOI
- `POST /api/search_by_title`: Search by Title
- `POST /api/search_by_keyword`: Search by Keyword
- `POST /api/get_metadata`: Get Metadata by DOI

---

## 📄 License

This project is licensed under the MIT License.

## ⚠️ Disclaimer

This tool is for educational and research purposes only. Please respect copyright laws and publisher terms.
