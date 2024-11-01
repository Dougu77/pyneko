import tldextract
import cloudscraper
from time import sleep
from os import makedirs
from tinydb import TinyDB, where
from platformdirs import user_data_path
from core.config.request_data import RequestData
from core.__seedwork.infra.http.contract.http import Http, Response
from core.cloudflare.application.use_cases import IsCloudflareBlockingUseCase, BypassCloudflareUseCase, BypassCloudflareNoCapchaUseCase, BypassCloudflareNoCapchaFeachUseCase, IsCloudflareBlockingTimeOutUseCase, IsCloudflareEnableCookies

data_path = user_data_path('pyneko')
db_path = data_path / 'request.json'
makedirs(data_path, exist_ok=True)
db = TinyDB(db_path)

class HttpService(Http):
    
    @staticmethod
    def get(url: str, params=None, headers=None, cookies=None, **kwargs) -> Response:
        status = 0
        count = 0
        extract = tldextract.extract(url)
        domain = f"{extract.domain}.{extract.suffix}"

        scraper = cloudscraper.create_scraper(    
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }    
        )
     
        while(status not in range(200, 299) and count <= 10):
            count += 1

            request_data = db.search(where('domain') == domain)

            if len(request_data) > 0:
                re = RequestData.from_dict(request_data[0])
                if headers is not None:
                    headers = {**headers, **re.headers}
                else:
                    headers = re.headers
                if cookies is not None:
                    cookies = {**cookies, **re.cookies}
                else:
                    cookies = re.cookies

            response = scraper.get(url, params=params, headers=headers, cookies=cookies, timeout=None, **kwargs)
            status = response.status_code

            if response.status_code == 403:
                print(f"<stroke style='color:#add8e6;'>[REQUEST]:</stroke> <span style='color:#add8e6;'>GET</span> <span style='color:red;'>{status}</span> <a href='#'>{url}</a>")
                if IsCloudflareBlockingUseCase().execute(response.text):
                        request_data = db.search(where('domain') == domain)
                        if(len(request_data) > 0):
                            db.remove(where('domain') == domain)
                        data = BypassCloudflareUseCase().execute(f'https://{domain}')
                        db.insert(RequestData(domain=domain, headers=data.user_agent, cookies=data.cloudflare_cookie_value).as_dict())
                elif IsCloudflareEnableCookies().execute(response.text):
                    content = BypassCloudflareNoCapchaFeachUseCase().execute(f'https://{domain}', url)
                    if content:
                        return Response(200, 'a', content, url)
                else:
                        content = BypassCloudflareNoCapchaUseCase().execute(url)
                        if(not IsCloudflareBlockingTimeOutUseCase().execute(content)):
                            return Response(200, content, content, url)
                        else:
                            sleep(30)
            elif status not in range(200, 299) and not 403 and not 429:
                print(f"<stroke style='color:#add8e6;'>[REQUEST]:</stroke> <span style='color:#add8e6;'>GET</span> <span style='color:red;'>{status}</span> <a href='#'>{url}</a>")
                sleep(1)
            elif status == 429:
                print(f"<stroke style='color:#add8e6;'>[REQUEST]:</stroke> <span style='color:#add8e6;'>GET</span> <span style='color:#FFFF00;'>{status}</span> <a href='#'>{url}</a>")
                sleep(60)                
            elif status == 301 and 'Location' in response.headers or status == 302 and 'Location' in response.headers:
                print(f"<stroke style='color:#add8e6;'>[REQUEST]:</stroke> <span style='color:#add8e6;'>GET</span> <span style='color:#add8e6;'>{status}</span> <a href='#'>{url}</a>")
                location = response.headers['Location']
                if(location.startswith('https://')):
                    new_url = location
                else:
                    new_url = f'https://{domain}{response.headers['Location']}'
                response = scraper.get(new_url, params=params, headers=headers, cookies=cookies, timeout=None, **kwargs)
                status = response.status_code
            if status in range(200, 299) or status == 404:
                print(f"<stroke style='color:#add8e6;'>[REQUEST]:</stroke> <span style='color:#add8e6;'>GET</span> <span style='color:green;'>{status}</span> <a href='#'>{url}</a>")
                return Response(response.status_code, response.text, response.content, url)

        raise Exception(f"Failed to fetch the URL STATUS: {status}")

    
    @staticmethod
    def post(url, data=None, json=None, headers=None, cookies=None, **kwargs) -> Response:
        status = 0
        count = 0
        extract = tldextract.extract(url)
        domain = f"{extract.domain}.{extract.suffix}"

        scraper = cloudscraper.create_scraper(    
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }    
        )

        while(status not in range(200, 299) and count <= 10):
            count += 1

            request_data = db.search(where('domain') == domain)

            if(len(request_data) > 0):
                re = RequestData.from_dict(request_data[0])
                if headers != None: headers = headers | re.headers
                else: headers = re.headers
                if cookies != None: cookies = cookies | re.cookies
                else: cookies = re.cookies

            response = scraper.post(url, data=data, json=json, headers=headers, cookies=cookies, timeout=None, **kwargs)
            status = response.status_code

            if response.status_code == 403:
                print(f"<stroke style='color:#add8e6;'>[REQUEST] POST:</stroke> <span style='color:#add8e6;'>POST</span> <span style='color:#FFFF00;'>{status}</span> <a href='#'>{url}</a>")
                if IsCloudflareBlockingUseCase().execute(response.text):
                    data = BypassCloudflareUseCase().execute(f'https://{domain}')
                    response = scraper.post(url, data=data, json=json, headers=headers, cookies=cookies, **kwargs)
                    if IsCloudflareBlockingUseCase().execute(response.text):
                        data = BypassCloudflareUseCase().execute(url)
                    db.insert(RequestData(domain=domain, headers=data.user_agent, cookies=data.cloudflare_cookie_value).as_dict())
            elif status not in range(200, 299) and not 403 and not 429:
                print(f"<stroke style='color:#add8e6;'>[REQUEST] POST:</stroke> <span style='color:#add8e6;'>POST</span> <span style='color:red;'>{status}</span> <a href='#'>{url}</a>")
                sleep(1)
            elif status == 429:
                print(f"<stroke style='color:#add8e6;'>[REQUEST] POST:</stroke> <span style='color:#add8e6;'>POST</span> <span style='color:#FFFF00;'>{status}</span> <a href='#'>{url}</a>")
                sleep(60)
            else:
                print(f"<stroke style='color:#add8e6;'>[REQUEST] POST:</stroke> <span style='color:#add8e6;'>POST</span> <span style='color:green;'>{status}</span> <a href='#'>{url}</a>")
                return Response(response.status_code, response.text, response.content, url)

        raise Exception("Failed to fetch the URL")