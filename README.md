# API-para-Crawler-e-Scraper-de-Fermentos
As informações desta aplicação são baseadas em produtos de três websites que vendem fermentos cervejeiros.

Para executar a aplicação, abra o terminal e vá ao diretório onde está o arquivo "main.py", 
Execute "uvicorn main:app --reload", espere o carregamento e vá até o endereço IP mostrado pelo terminal. Acrescente "/docs" ao final do endereço. 

Ex: http://127.0.0.1:8000/docs

Para usar a função "Pesquisar Por Nome", clique em "Try it out" e digite uma palavra ou sequencia de caracteres presentes no nome do fermento procurado. Ex: se quisessemos pesquisar pelo fermento Mangrove Jacks, poderíamos escrever "Mangrove", "Jacks", "Mangrove Jacks", "Mangr", "ove Jacks", etc;
Para usar a função "Pesquisar Por Preço", digite um valor máximo a partir do qual não serão mostrados mais resultados;
Para usar a função "Pesquisar Por Nome e Preço", digite o preço máximo e uma palavra ou sequencia de caracteres presentes no nome do fermento procurado.

Caso queira atualizar a base de dados, instale as dependências necessárias, certifique-se de ter os arquivos organizados nos diretórios corretos, abra o arquivo "testes_tcc.ipynb", leia os comentários para entender o funcionamento do programa e execute apenas as células necessárias.

