# API-para-Web-Scraper-de-Fermentos-Cervejeiros
Esta aplicação visa facilitar a procura por fermentos cervejeiros disponíveis para compra, permitindo uma busca filtrada por nomes, preços máximos e palavras-chave que descrevam os produtos desejados.
Para isso, esta aplicação reúne informações de diferentes websites que comercializam fermentos cervejeiros, sendo seu intuito a facilitação da pesquisa por meio da centralização das informações em uma única base de dados.

Para executar a aplicação, clone este respositório ou baixe seus arquivos, abra abra o terminal no diretório onde os arquivos foram salvos e instale as dependências (pip install -r requirements.txt). 
Em seguida, execute o comando "uvicorn main:app --reload", espere o carregamento e vá até o endereço IP mostrado pelo terminal. Acrescente "/docs" ao final do endereço. 

Ex: http://127.0.0.1:8000/docs

A base de dados disponibilizada neste repositório foi atualizada pela última vez no dia 06/01/2026, mas você pode atualizá-la por meio das funções disponibilizadas na aplicação.

Funções GET:
Para usar a função "Pesquisar Por Nome", clique em "Try it out" e digite uma palavra ou sequencia de caracteres presentes no nome do fermento procurado. Ex: se quisessemos pesquisar pelo fermento Mangrove Jacks, poderíamos escrever "Mangrove", "Jacks", "Mangrove Jacks", "Mangr", "ove Jacks", etc;

Para usar a função "Pesquisar Por Preço", digite um valor máximo a partir do qual não serão mostrados mais resultados;

Para usar a função "Pesquisar Por Nome e Preço", digite o preço máximo e uma palavra ou sequencia de caracteres presentes no nome do fermento procurado;

Para usar a função "Pesquisar Por Descrição", digite alguma palavra ou sequência de caracteres que você acredita que estejam presentes na descrição do produto desejado.


Você também pode modificar a base de dados por meio das outras funções.

As funções do tipo POST fazem o web scraping nos websites nelas referenciados.

A função do tipo PUT sobrescreve a tabela, substituindo-a por uma tabela vazia.

As funções do tipo DELETE apagam os dados provenientes de algum dos websites nelas referenciados.


