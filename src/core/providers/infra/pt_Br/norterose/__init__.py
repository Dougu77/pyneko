from fake_useragent import UserAgent
from core.providers.domain.entities import Pages
from core.download.application.use_cases import DownloadUseCase
from core.providers.infra.template.wordpress_madara import WordPressMadara
from core.__seedwork.infra.http import Http
from core.providers.domain.entities import Pages
from urllib.parse import urljoin

class NorteRoseProvider(WordPressMadara):
    name = 'Norte rose'
    lang = 'pt-Br'
    domain = ['norterose.com.br']

    def __init__(self):
        self.url = 'https://norterose.com.br'

        self.path = ''
        
        self.query_mangas = 'div.post-title h3 a, div.post-title h5 a'
        self.query_chapters = 'li.wp-manga-chapter.has-thumb > a'
        self.query_chapters_title_bloat = None
        self.query_pages = 'div.page-break.no-gaps'
        self.query_title_for_uri = 'head meta[property="og:title"]'
        self.query_placeholder = '[id^="manga-chapters-holder"][data-id]'
        ua = UserAgent()
        user = ua.chrome
        self.user = ua.chrome
        self.headers = {'host': 'norterose.com.br', 'Cookie': 'visited=true; wpmanga-reading-history=W3siaWQiOjQxMiwiYyI6IjI1MTYiLCJwIjoxLCJpIjoiIiwidCI6MTcxOTk2MzA1OX1d', 'user_agent': user, 'referer': f'{self.url}/manga/'}
    
    def download(self, pages: Pages, fn: any, headers=None, cookies=None):
        if headers is not None:
            headers = headers | self.headers
        else:
            headers = self.headers
        return DownloadUseCase().execute(pages=pages, fn=fn, headers=headers, cookies=cookies)
    
    def _get_chapters_ajax(self, manga_id):
        uri = urljoin(self.url, f'{manga_id}ajax/chapters/')
        response = Http.post(uri, headers={'Cookie': 'visited=true; wpmanga-reading-history=W3siaWQiOjg4MiwiYyI6IjIzMzU5IiwicCI6MSwiaSI6IiIsInQiOjE3MTk5NjEwODN9XQ%3D%3D'})
        data = self._fetch_dom(response, self.query_chapters)
        if data:
            return data
        else:
            raise Exception('No chapters found (new ajax endpoint)!')