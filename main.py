import asyncio
import traceback
from time import sleep

from edge_gpt import Chatbot, ConversationStyle
from forum_scraper import ForumScraper
from secret import URL, FORUM_COOKIE, BING_COOKIE, MAIN_PROMPT
from utils import save_conf, add_period, remove_reference_simbols

"""
Bot que usa chat do Bing para responder tópicos no forum IGN boards.
   By Honrarias 04/04/2023
   
   ## Requirements

- python 3.8+
- Seguintes cookies de navegador adicionados ao arquivo ```secret.py```:
  - Cookie ```_U``` do bing.com. Uma conta da Microsoft com acesso antecipado a https://bing.com/chat é obrigatório.
  - Cookie ```xf_user``` de usuario do furum.
  
  Para obte-los:
  
  Acesse o bing.com e o forum pelo Chrome ou Firefox (pelo edge não funciona), faça o login e use o "inspecionar" do navegador
  
  ou
  
  instale a extensão **cookie-editor** https://cookie-editor.cgagnier.ca/ para Chrome ou Firefox:
  - faça o login em bing.com ou o forum.
  - Abra a extensão
  - clique no cookie citado acima e copie o ```Value```

## Configure o sub forum:

Em ```secret.py``` adicione o endereço do sub fórum desejado.

## Mensagens de erro:
Erro ```NotAllowedToAccess``` significa que o cookie do bing expirou ou é inválido.
Erro ```AuthenticationError``` significa que o cookie do forum expirou ou é inválido.
"""

fs = ForumScraper(URL, FORUM_COOKIE, warning_mgs=True)
bing = Chatbot(cookies=[{"name": "_U", "value": BING_COOKIE}], warning_mgs=True)


async def main(user_filter, main_prompt):
    threads = fs.get_thread_data(user_filter)
    print("a responder:", len(threads))

    for thread in threads:
        nick, thread_id, title, text = thread.values()
        full_prompt = main_prompt + f"TITULO: {add_period(title)}\n\tMENSAGEM: {add_period(text)}"
        ai_response = await bing.ask(prompt=full_prompt, conversation_style=ConversationStyle.creative)
        await bing.reset()
        print("thread:::", "\n\ttitulo: ", title, "\n\tmensagem: ", text)
        print("\n\n")
        if ai_response:
            ai_response = remove_reference_simbols(ai_response)
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
