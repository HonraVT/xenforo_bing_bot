# xenforo_bing_bot

## Use o chat IA do Bing para responder tópicos no forum IGN boards. <img alt="PyPI version" src="https://www.ignboards.com/styles/ign/ign/smilies/international-classic/lolsuper.gif">



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

Erro ```RequestThrottledError``` significa que a conta atingiu o máximo de solicitações por dia.

## Acknowledgment

Baseado em https://github.com/acheong08/EdgeGPT



  
  
      
      
