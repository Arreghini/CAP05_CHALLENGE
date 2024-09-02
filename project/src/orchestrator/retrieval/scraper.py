from abc import ABC, abstractmethod
import re
from typing import Any

import aiohttp
from bs4 import BeautifulSoup


# Esta clase de Python define un Scraper con un método abstracto fetch para obtener datos desde una URL y un método parse para extraer 
# texto del contenido HTML.
class Scraper(ABC):
    @abstractmethod
    async def fetch(self, url: str) -> dict[str, Any]:
        pass

    async def parse(self, body):
        """Parses all the text from the html."""

        soup = BeautifulSoup(body, "html.parser")
        raw_text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r"\n{3,}|\s{2,}", "\n", raw_text)
        return text


#La clase ScraperRemote es una subclase de Scraper que obtiene y analiza contenido HTML de un servidor remoto utilizando solicitudes 
# asincrónicas.


class ScraperRemote(Scraper):
    def __init__(self, host: str = "http://lb-scraper/scrape/?url=") -> None:
        self.host = host

    async def fetch(self, url: str) -> dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            query_url = self.host + url
            async with session.post(query_url) as response:
                if response.status == 200:
                    body = await response.json()
                    text = await self.parse(body["html"])
                    if text:
                        return {"url": url, "text": text}
            return {"url": url, "text": None}

# La clase ScraperLocal es una subclase de Scraper que define un método asincrónico fetch para obtener y analizar contenido HTML desde una 
# URL dada utilizando aiohttp.
class ScraperLocal(Scraper):
    async def fetch(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                html = await response.text()
                text = await self.parse(html)

                return {"url": url, "text": text}
