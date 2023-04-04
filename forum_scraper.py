from time import sleep
import warnings
import httpx
from lxml.html import fromstring

from utils import get_not_answered, load_conf

from secret import *

USER_AGENT = \
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"


class AuthenticationError(Exception):
    pass


class RequestError(Exception):
    pass


class ForumScraper:
    def __init__(self, url, cookie, warning_mgs=False):
        self.payload = {}
        self.url = url
        self.ses = httpx.Client(follow_redirects=True)
        self.ses.headers.update({"user-agent": USER_AGENT})
        self.ses.cookies.update({"xf_user": cookie})
        if not warning_mgs:
            warnings.filterwarnings("ignore")
        self.get_authorization()

    def reply(self, thread_id, response):
        url = f"{self.url.split('/forums')[0]}/threads/{thread_id}/add-reply"
        self.payload["message"] = response  # + "\n[ISPOILER]gpt-3 test[/ISPOILER]"
        self.ses.post(url, data=self.payload)

    def get_authorization(self):
        try:
            res = self.ses.get(self.url)
            if res.status_code > 303:
                raise RequestError(f"Forum request error, code: {res.status_code}")
            # print(res.text[397:550])
            html = fromstring(res.content)
            self.payload['_xfToken'] = html.find('.//input[@name="_xfToken"]').value
        except AttributeError:
            raise AuthenticationError("not logged in!")

    def get_threads(self):
        main_page_data = []
        res = self.ses.get(self.url)
        if res.status_code > 303:
            RequestError(f"Forum request error, code: {res.status_code}")
        html = fromstring(res.content)
        self.payload['_xfToken'] = html.find('.//input[@name="_xfToken"]').value
        threads = html.find_class('structItem structItem--thread')
        for thread in threads:
            title_div = thread.xpath('./div[2]/div[1]')[0]
            main_page_data.append(
                {"author": thread.attrib["data-author"],
                 "id": title_div.values()[1].replace("unread", "")[-10:-1],
                 "title": title_div.text_content().strip()
                 }
            )
        return sorted(main_page_data, key=lambda d: d["id"])

    def get_preview_text(self, id_thread):
        res = self.ses.get(
            f'{self.url.split("/forums")[0]}/threads/{id_thread}/preview?_xfToken={self.payload["_xfToken"]}\
            &_xfResponseType=json '
        )
        if res.status_code > 303:
            warnings.warn(f"[!] get_preview_text, error at forum request, code: {res.status_code}")
            return ""
        return fromstring(res.json()["html"]["content"]).text_content().strip()

    def get_thread_data(self, filter_user):
        first_page_threads = self.get_threads()
        to_answer = get_not_answered(load_conf("last_read.conf"), first_page_threads)
        # to reply if in filter
        # to_answer_filter_user = [a for a in to_answer if a["author"] in filter_user]
        # to reply if NOT in filter
        to_answer_filter_user = [a for a in to_answer if a["author"] not in filter_user]
        for thread in to_answer_filter_user:
            sleep(0.4)  # prevent 429 "too many gay questions" error
            out_data = self.get_preview_text(thread["id"])
            thread["text"] = out_data
        # remove threads without text, e.g: image, videos..
        to_answer_filter_without_text = [th for th in to_answer_filter_user if th["text"]]
        return to_answer_filter_without_text

