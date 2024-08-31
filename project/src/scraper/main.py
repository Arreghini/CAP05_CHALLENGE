import time
"""
Esta aplicación de FastAPI en Python incluye funciones para hacer scraping de una página web utilizando un navegador sin interfaz gráfica 
(headless browser) y manejar los tiempos de espera (timeouts) de manera adecuada.

url: El código proporcionado es una aplicación de FastAPI que utiliza Playwright para hacer scraping de una página web y devolver el contenido
HTML. Cuando se realiza una solicitud POST al endpoint /scrape con un parámetro URL, se lanzará un navegador Firefox sin interfaz gráfica, 
navegará a la URL especificada y devolverá el HTML.

:return: El código define una aplicación asíncrona de FastAPI que incluye funciones para obtener y hacer scraping del contenido HTML de una URL
dada utilizando Playwright y aiohttp. Cuando se realiza una solicitud POST al endpoint "/scrape" con un parámetro URL, la aplicación intentará 
hacer scraping del contenido HTML de la URL proporcionada usando un navegador Firefox sin interfaz gráfica lanzado por Playwright.
"""
from fastapi import FastAPI, HTTPException
from playwright.async_api import async_playwright
from playwright._impl._api_types import TimeoutError
from contextlib import asynccontextmanager
import logging
import aiohttp

logger = logging.getLogger(__name__)
app = FastAPI()


async def fetch_check_js(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=3)) as response:
            html = await response.text()

            # if not "text/javascript" in html:
            return html
    return None


@asynccontextmanager
async def launch_browser():
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        try:
            yield browser
        finally:
            await browser.close()


async def scrape_with_browser(url: str):
    async with launch_browser() as browser:
        page = await browser.new_page()
        await page.goto(url, timeout=2000)
        html = await page.content()
    return html


@app.post("/scrape")
async def scrape_url(url: str):
    try:
        html = await scrape_with_browser(url)
    except TimeoutError:
        raise HTTPException(status_code=408, detail="Not fast enough")
    return {"html": html}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
