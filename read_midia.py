import random
import warnings

import httpx

"""Get some media context"""


def random_headers():
    return f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.5563.{random.randint(0, 9999)} Safari/537.{random.randint(0, 99)}'


def get_youtube_video_title(youtube_id):
    try:
        params = {"format": "json", "url": "https://www.youtube.com/watch?v=" + youtube_id}
        res = httpx.get("https://www.youtube.com/oembed", params=params)
        if res.status_code == 200:
            return res.json()["title"]
    except Exception as e:
        warnings.warn(f"[!] youtube API error: {str(e)}")
    return None


def get_twitter_text(tweet_id):
    url = "https://api.twitter.com/1.1/statuses/show.json?id="
    api_headers = {
        'User-Agent': random_headers(),
        # API key extracted from snscrape https://github.com/JustAnotherArchivist/snscrape
        'Authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
        'Referer': "https://api.twitter.com",
        'Accept-Language': 'en-US,en;q=0.5',
    }
    try:
        res = httpx.get(url + tweet_id, headers=api_headers, follow_redirects=True)
        if res.status_code == 200:
            return res.json()["text"]
    except Exception as e:
        warnings.warn(f"[!] twitter API error: {str(e)}")
    return None


def get_reddit_title(reddit_id):
    api_headers = {'User-Agent': random_headers()}
    try:
        res = httpx.get(f"https://www.reddit.com/comments/{reddit_id}/.json", headers=api_headers)
        if res.status_code == 200:
            return res.json()[0]['data']['children'][0]['data']['title']
    except Exception as e:
        warnings.warn(f"[!] Reddit API error: {str(e)}")
    return None


def midia_context(html):
    for m in html.iterlinks():
        if m[1] == "src":
            if "youtube" in m[2]:
                yt = get_youtube_video_title(m[2].split("embed/")[1])
                if yt:
                    return f"\ntítulo do video no youtube: {yt}"
                break
            if "twitter" in m[2]:
                twt = get_twitter_text(m[2][48:-5])
                if twt:
                    return f"\nesse tweet: {twt}"
                break
            if "reddit" in m[2]:
                red = get_reddit_title(m[2][-7:])
                if red:
                    return f"\nesse comentário no reddit: {red}"
                break
            if "instagram" in m[2]:
                return f"\n{m[2]}"
    return ""
  
