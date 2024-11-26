from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class AsuraComicProvider(Base):
    name = 'Asura Scans'
    lang = 'en'
    domain = ['asuracomic.net']

    def __init__(self) -> None:
        self.url = 'https://asuracomic.net/series/'
    
    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('span.text-xl.font-bold')
        return Manga(link, title.get_text().strip())

    def getChapters(self, id: str) -> List[Chapter]:
        response = Http.get(id)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('span.text-xl.font-bold')
        chapters_div = soup.select_one('div.pl-4.pr-2.pb-4.overflow-y-auto.scrollbar-thumb-themecolor.scrollbar-track-transparent.scrollbar-thin.mr-3')
        chapters = chapters_div.select('h3 > a')
        list = []
        for ch in chapters:
            list.append(Chapter(f'{self.url}{ch.get('href')}', ch.get_text().strip(), title.get_text().strip()))
        list.reverse()
        return list

    def getPages(self, ch: Chapter) -> Pages:
        list = []
        response = Http.get(ch.id)
        soup = BeautifulSoup(response.content, 'html.parser')
        images = soup.select('img.object-cover.mx-auto')
        for pgs in images:
            list.append(pgs.get('src'))
        return Pages(ch.id, ch.number, ch.name, list)
