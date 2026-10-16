import os
import sys
import asyncio
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from sci_hub_search import (
    search_paper_by_doi,
    search_paper_by_title,
    search_papers_by_keyword,
    download_paper
)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# FastAPI App for Render & ChatGPT / Gemini integrations
app = FastAPI(
    title="Sci-Hub Academic Search API & MCP Server",
    description="API & MCP Server to search, access metadata, and retrieve academic paper links via Sci-Hub & CrossRef.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Enable CORS for cross-origin access (ChatGPT Actions, web agents, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchDoiRequest(BaseModel):
    doi: str = Field(..., description="The Digital Object Identifier (DOI) of the paper, e.g. '10.1038/nature09492'")

class SearchTitleRequest(BaseModel):
    title: str = Field(..., description="The title of the academic paper to search for")

class SearchKeywordRequest(BaseModel):
    keyword: str = Field(..., description="Keywords or topic describing the research area")
    num_results: Optional[int] = Field(default=5, description="Maximum number of papers to return (default 5, max 10)")

class DownloadRequest(BaseModel):
    pdf_url: str = Field(..., description="The direct URL of the PDF to download")
    output_path: str = Field(..., description="The local filename or path to save the PDF")


@app.get("/", summary="Root Status")
def root_status():
    return {
        "status": "online",
        "service": "Sci-Hub Academic Search MCP & REST API Server",
        "documentation": "/docs",
        "openapi_schema": "/openapi.json",
        "endpoints": [
            "/api/search_by_doi",
            "/api/search_by_title",
            "/api/search_by_keyword",
            "/api/get_metadata"
        ]
    }

@app.get("/health", summary="Health check for Render.com")
def health():
    return {"status": "healthy"}

@app.post("/api/search_by_doi", summary="Search Paper by DOI", operation_id="search_scihub_by_doi")
async def api_search_doi(request: SearchDoiRequest) -> Dict[str, Any]:
    """Search for an academic paper on Sci-Hub by DOI and get paper metadata and direct PDF URL."""
    logging.info(f"Searching by DOI: {request.doi}")
    return await asyncio.to_thread(search_paper_by_doi, request.doi)

@app.post("/api/search_by_title", summary="Search Paper by Title", operation_id="search_scihub_by_title")
async def api_search_title(request: SearchTitleRequest) -> Dict[str, Any]:
    """Search for an academic paper by title via CrossRef to resolve DOI, then fetch from Sci-Hub."""
    logging.info(f"Searching by title: {request.title}")
    return await asyncio.to_thread(search_paper_by_title, request.title)

@app.post("/api/search_by_keyword", summary="Search Papers by Keyword", operation_id="search_scihub_by_keyword")
async def api_search_keyword(request: SearchKeywordRequest) -> List[Dict[str, Any]]:
    """Search academic papers by keywords or research topic."""
    logging.info(f"Searching by keyword: {request.keyword}")
    return await asyncio.to_thread(search_papers_by_keyword, request.keyword, request.num_results or 5)

@app.post("/api/get_metadata", summary="Get Paper Metadata", operation_id="get_paper_metadata")
async def api_get_metadata(request: SearchDoiRequest) -> Dict[str, Any]:
    """Retrieve bibliographic metadata for a paper given its DOI."""
    logging.info(f"Fetching metadata for DOI: {request.doi}")
    return await asyncio.to_thread(search_paper_by_doi, request.doi)


# MCP FastMCP setup (compatible with local stdio usage)
def get_mcp_instance():
    try:
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("scihub")

        @mcp.tool()
        async def search_scihub_by_doi(doi: str) -> Dict[str, Any]:
            """Search for a paper on Sci-Hub using its DOI."""
            return await asyncio.to_thread(search_paper_by_doi, doi)

        @mcp.tool()
        async def search_scihub_by_title(title: str) -> Dict[str, Any]:
            """Search for a paper on Sci-Hub using its title."""
            return await asyncio.to_thread(search_paper_by_title, title)

        @mcp.tool()
        async def search_scihub_by_keyword(keyword: str, num_results: int = 5) -> List[Dict[str, Any]]:
            """Search for papers on Sci-Hub using keywords."""
            return await asyncio.to_thread(search_papers_by_keyword, keyword, num_results)

        @mcp.tool()
        async def download_scihub_pdf(pdf_url: str, output_path: str) -> str:
            """Download a paper PDF from Sci-Hub."""
            success = await asyncio.to_thread(download_paper, pdf_url, output_path)
            return f"PDF successfully downloaded to {output_path}" if success else "Failed to download PDF"

        return mcp
    except Exception as e:
        logging.warning(f"FastMCP setup warning: {e}")
        return None

mcp = get_mcp_instance()

if __name__ == "__main__":
    if "--stdio" in sys.argv:
        if mcp:
            logging.info("Starting Sci-Hub MCP Server in stdio mode")
            mcp.run(transport="stdio")
        else:
            print("FastMCP library could not be loaded for stdio mode.")
    else:
        import uvicorn
        port = int(os.environ.get("PORT", 8000))
        logging.info(f"Starting Sci-Hub Web & API Server on port {port}")
        uvicorn.run("sci_hub_server:app", host="0.0.0.0", port=port, reload=False)
