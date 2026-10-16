# Sci-Hub MCP & API Server

🔍 **Sci-Hub MCP & API Server** enables AI assistants such as **Google Gemini (Spark)**, **ChatGPT**, and **Claude Desktop** to search, retrieve bibliographic metadata, and download scientific papers and journal articles via the Model Context Protocol (MCP) and REST API.

---

## ✨ Core Features

- 🔎 **Search by DOI**: Find comprehensive metadata and direct PDF download links from Sci-Hub.
- 🔍 **Search by Title**: Resolve Digital Object Identifiers (DOI) via CrossRef, then retrieve paper details from Sci-Hub.
- 🔑 **Search by Keyword**: Discover research papers and articles related to specific topics.
- 📊 **Accurate Metadata Retrieval**: Author(s), publication year, journal/publisher, and direct PDF URL.
- 🌐 **Universal Multi-Platform Support**:
  - **Google Gemini Spark (Connected Apps)**: Native support for the **Streamable HTTP** transport protocol.
  - **ChatGPT Custom MCP Server (Plugins)**: Support for the **Server-Sent Events (SSE)** transport protocol.
  - **ChatGPT Custom GPT (Actions)**: Full **OpenAPI 3.0** schema compliance.
  - **Local Desktop MCP Clients**: Claude Desktop & Cursor via `stdio`.

---

## 🚀 Setup & Integration Guides

### 1. Google Gemini Spark (Connected Apps)

According to the [Official Google Gemini Documentation](https://support.google.com/gemini/answer/17209137), Gemini uses the **Streamable HTTP** transport protocol.

1. Open [gemini.google.com](https://gemini.google.com) on your computer.
2. In the bottom-left corner, click **Settings** > select **Connected Apps**.
3. Under **Custom apps**, click **Add a custom app** (or use the custom app link input).
4. Enter the following URL into the **MCP Server URL** field:
   ```text
   https://sci-hub-mcp.onrender.com/mcp
   ```
5. Click **Next** and complete the on-screen confirmation.
6. **How to use in chat**:
   Type `@` and select your custom app, or simply ask Gemini directly:
   > *"Can you find the paper with DOI 10.1038/nature09492 and provide the PDF link?"*

---

### 2. ChatGPT (Custom MCP Server / Plugins)

If you are using ChatGPT's custom MCP server integration (Developer Mode / Plugins):

1. Open [chatgpt.com](https://chatgpt.com).
2. Go to **Plugins** or **Apps** > click **`+`** or **Add custom MCP server**.
3. Fill in the form with the following details:
   * **Name**: `Sci-Hub`
   * **Description**: `Search academic papers and download research PDFs`
   * **Connection**: Select the **Server URL** tab
   * **Server URL**:
     ```text
     https://sci-hub-mcp.onrender.com/sse
     ```
   * **Authentication**: Select **`No authentication`** *(IMPORTANT: Do not select OAuth)*
4. Check the risk agreement checkbox (*I understand and want to continue*).
5. Click **Create as a plugin**.

---

### 3. ChatGPT (Custom GPT Actions)

If you are creating a Custom GPT using the [ChatGPT GPT Builder](https://chatgpt.com/gpts/editor):

1. Navigate to the **Configure** tab of your Custom GPT.
2. Scroll to the bottom and click **Create new action**.
3. In the **Schema** section, click **Import from URL**.
4. Enter the OpenAPI Schema URL:
   ```text
   https://sci-hub-mcp.onrender.com/openapi.json
   ```
5. Click **Import**. ChatGPT will automatically discover and configure all available tools (`search_scihub_by_doi`, `search_scihub_by_title`, `search_scihub_by_keyword`, `get_paper_metadata`).
6. Set the **Privacy Policy** field to: `https://sci-hub-mcp.onrender.com`.

---

### 4. Local Desktop MCP Clients (Claude Desktop / Cursor)

Run the server in local `stdio` mode:

```bash
python sci_hub_server.py --stdio
```

Example configuration for `claude_desktop_config.json`:

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

## 🛠 Server Endpoints Reference

| Endpoint | Protocol / Transport | Target Client |
| :--- | :--- | :--- |
| `POST /mcp` | Streamable HTTP Transport | **Google Gemini Connected Apps** |
| `GET /sse` | Server-Sent Events (SSE) | **ChatGPT Plugins / MCP Clients** |
| `GET /openapi.json` | OpenAPI 3.0 Schema | **ChatGPT Custom GPT Actions** |
| `GET /docs` | Swagger Interactive UI | Manual Testing & API Documentation |
| `GET /health` | Health Check | Render.com Keep-Alive |
| `POST /api/search_by_doi` | REST Endpoint | Custom Webhooks & API integrations |
| `POST /api/search_by_title` | REST Endpoint | Custom Webhooks & API integrations |
| `POST /api/search_by_keyword` | REST Endpoint | Custom Webhooks & API integrations |
| `POST /api/get_metadata` | REST Endpoint | Custom Webhooks & API integrations |

---

## ☁️ Deployment on Render.com

To deploy your own instance of this server on Render:

1. Connect this repository to your [dashboard.render.com](https://dashboard.render.com).
2. Create a new **Web Service**:
   * **Runtime**: `Python 3`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `uvicorn sci_hub_server:app --host 0.0.0.0 --port $PORT`
   * **Instance Type**: `Free`
3. Render automatically binds to the `$PORT` environment variable and exposes your server publicly with HTTPS.

---

## 📄 License & Disclaimer

- **License**: MIT License.
- **Disclaimer**: This tool is designed strictly for educational and academic research purposes. Please respect copyright laws and terms of service applicable in your jurisdiction.
