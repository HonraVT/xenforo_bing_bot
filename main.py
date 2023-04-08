import asyncio
import traceback
from time import sleep

from edge_gpt import Chatbot, ConversationStyle, RequestThrottledError
from forum_scraper import ForumScraper
from secret import URL, FORUM_COOKIE, BING_COOKIES, MAIN_PROMPT
from utils import save_conf, add_period, add_modifiers, load_conf, cookie_swap


cookie_index = int(load_conf("cookie_swap.conf"))

fs = ForumScraper(URL, FORUM_COOKIE, warning_mgs=True)
bing = Chatbot(BING_COOKIES[cookie_index], warning_mgs=True)


async def main(user_filter, main_prompt):
    threads = fs.get_thread_data(user_filter)
    print("a responder:", len(threads))

    for thread in threads:
        nick, thread_id, title, text = thread.values()
        full_prompt = MAIN_PROMPT + f"\r\nTITULO: {add_period(title)}\nMENSAGEM: {add_period(text)}\nRESPOSTA:"
        try:
            ai_response = await bing.ask(prompt=full_prompt, conversation_style=ConversationStyle.creative)
        except RequestThrottledError:
            if len(BING_COOKIES) == 1:
                print("[!] Request Is Throttled, Your Account Hit Max Requests Per Day, Exiting Program...")
                quit()
            print("[!] Request Is Throttled, Trying Change Cookies.")
            await bing.reset(cookie_swap(BING_COOKIES, cookie_index))
            raise
        await bing.reset()
        print("thread:::", "\n\ttitulo: ", title, "\n\tmensagem: ", text)
        print("\n\n")
        ai_response = add_modifiers(ai_response)
        if ai_response:
            print("ai_response raw:::", ai_response)
            sleep(20)
            fs.reply(thread_id, ai_response)
            save_conf("last_read.conf", thread_id)
            sleep(80)
    sleep(100)
    await main(user_filter, main_prompt)


if __name__ == '__main__':
    # optionally filter user by nick.
    USER_FILTER = []
    try:
        print("run...")
        asyncio.run(main(USER_FILTER, MAIN_PROMPT))
    except Exception as err:
        print("final error", err)
        print("final error full", traceback.format_exc())
        sleep(50)
        asyncio.run(main(USER_FILTER, MAIN_PROMPT))
