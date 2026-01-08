# importar pacotes
from bs4 import BeautifulSoup
import requests
import time
import json
import datetime
import pandas as pd
import warnings
import sqlite3
import shutil
import uuid
import os

warnings.simplefilter(action='ignore', category=FutureWarning)  # para ignorar os warnings do pandas, que poluem muito as saídas

# Função para criar uma conexão de banco de dados temporária para o usuário
def criar_banco_usuario_temporario():
    # Cria um nome único para o banco de dados temporário
    nome_banco = f"./fermentos_{uuid.uuid4().hex}.db"
    
    # Copia o banco original para o banco temporário
    shutil.copy("./fermentos.db", nome_banco)
    
    # Conecta-se ao banco temporário
    con1 = sqlite3.connect(nome_banco, check_same_thread=False)
    cursor1 = con1.cursor()

    return con1, cursor1, nome_banco

# def deletar_banco_temporario(nome_banco, con1):
#     try:
#         # Fechar a conexão ao banco de dados antes de tentar deletá-lo
#         print("Fechando a conexão...")
#         con1.close()

#         # Verifica se o banco existe e tenta deletá-lo
#         if os.path.exists(nome_banco):
#             os.remove(nome_banco)
#             print(f"Banco temporário '{nome_banco}' deletado.")
#         else:
#             print(f"Banco temporário '{nome_banco}' não encontrado.")
#     except Exception as e:
#         print(f"Erro ao deletar o banco temporário: {e}")

def verificar_tabela_no_banco(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tabelas no banco temporário:", tables)
    if ('tab_fermentos_1',) not in tables:
        print("Tabela 'tab_fermentos_1' não encontrada no banco temporário!")
    else:
        print("Tabela 'tab_fermentos_1' está presente.")

# Função para gerar uma tabela do tipo .csv
def func_gerar_csv(filtro:str, cursor1):  ## o parâmetro filtro deverá ser uma f string (exemplo: gerar_csv(f"WHERE nome_do_produto_c LIKE ('%{nome}%')"))

    def fazer_linha_1_csv(filtro:str, cursor1):
        selecionar_tudo = f"SELECT * FROM tab_fermentos_1 {filtro}"
        cursor1.execute(selecionar_tudo)
        informacoes_sobre_fermentos = cursor1.fetchall()
        for cada_linha_tabela_de_fermentos in informacoes_sobre_fermentos[0:1]:
            cada_dicionario_de_fermentos = {
                "Nome do fermento": [cada_linha_tabela_de_fermentos[0]],
                "Preço (R$)": [cada_linha_tabela_de_fermentos[1]],
                "Descrição": [cada_linha_tabela_de_fermentos[2]],
                "Data do Scraping (YYYY-MM-DD)": [cada_linha_tabela_de_fermentos[3]],
                "Link": [cada_linha_tabela_de_fermentos[4]],
            }
            tabela_detalhes = pd.DataFrame(cada_dicionario_de_fermentos)

        tabela_em_csv = tabela_detalhes.to_csv("ultima_busca.csv", sep=',', index=False)

    def fazer_linhas_restantes_csv(filtro:str, cursor1):
        tabela_detalhes = pd.read_csv("ultima_busca.csv")
        selecionar_tudo = f"SELECT * FROM tab_fermentos_1 {filtro}"
        cursor1.execute(selecionar_tudo)
        informacoes_sobre_fermentos = cursor1.fetchall()
        for cada_linha_tabela_de_fermentos in informacoes_sobre_fermentos[1:]:
            cada_dicionario_de_fermentos = {
                "Nome do fermento": cada_linha_tabela_de_fermentos[0],
                "Preço (R$)": cada_linha_tabela_de_fermentos[1],
                "Descrição": cada_linha_tabela_de_fermentos[2],
                "Data do Scraping (YYYY-MM-DD)": cada_linha_tabela_de_fermentos[3],
                "Link": cada_linha_tabela_de_fermentos[4],
            }
            tabela_detalhes = tabela_detalhes.append(cada_dicionario_de_fermentos, ignore_index=True)

        tabela_em_csv = tabela_detalhes.to_csv("ultima_busca.csv", sep=',', index=False)

    # Passando cursor1 para as funções internas
    fazer_linha_1_csv(filtro, cursor1)  # Passando cursor1 para a função
    fazer_linhas_restantes_csv(filtro, cursor1)  # Passando cursor1 para a função

# Função para criar uma tabela vazia quando a busca não fornecer nenhum resultado
def func_csv_sem_resultados():
    dicionario_sem_fermento = {
        "Nome do fermento": [],
        "Preço (R$)": [],
        "Descrição": [],
        "Data do Scraping (YYYY-MM-DD)": [],
        "Link": [],
    }

    tabela_detalhes = pd.DataFrame(dicionario_sem_fermento)  ## para criar uma tabela a partir desse dicionário vazio
    tabela_em_csv = tabela_detalhes.to_csv("ultima_busca.csv", sep=',', index=False)  ## para gerar um .csv a partir dessa tabela vazia

# Função para pesquisar o número de resultados presentes na base de dados
def func_todos_os_resultados(cursor1):
    selecionar_tudo = f"SELECT * FROM tab_fermentos_1"
    cursor1.execute(selecionar_tudo)
    informacoes_sobre_fermentos = cursor1.fetchall()
    resultados = 0  ## os resultados contados nessa variável
    for cada_linha_tabela_de_fermentos in informacoes_sobre_fermentos:
        resultados += 1

    if (resultados == 0): func_csv_sem_resultados()  ## se a busca não retornar nenhum resultado, gera-se uma tabela vazia
    else: func_gerar_csv("", cursor1)

    numero_de_resultados = "Foram encontrados " + str(resultados) + " resultados de fermentos na base de dados. Os resultados também podem ser vistos no arquivo 'ultima_busca.csv' "
    return numero_de_resultados

# Função para pesquisar fermento por NOME
def func_pesquisar_por_nome(nome: str, cursor1):

    selecionar_palavra_buscada = f"SELECT * FROM tab_fermentos_1 WHERE nome_do_produto_c LIKE ('%{nome}%')"
    cursor1.execute(selecionar_palavra_buscada)
    informacoes_sobre_fermentos = cursor1.fetchall()
    resultados = []  ## os resultados (em forma de dicionarios) serão adicionados a essa lista
    for cada_linha_tabela_de_fermentos in informacoes_sobre_fermentos:
        cada_dicionario_de_fermentos = {
            "Nome do fermento": cada_linha_tabela_de_fermentos[0],
            "Preço (R$)": cada_linha_tabela_de_fermentos[1],
            "Descrição": cada_linha_tabela_de_fermentos[2],
            "Data do Scraping (YYYY-MM-DD)": cada_linha_tabela_de_fermentos[3],
            "Link": cada_linha_tabela_de_fermentos[4],
        }
        resultados.append(cada_dicionario_de_fermentos)

    if (len(resultados) == 0): func_csv_sem_resultados()  ## se a busca não retornar nenhum resultado, gera-se uma tabela vazia
    else: func_gerar_csv(f"WHERE nome_do_produto_c LIKE ('%{nome}%')", cursor1)

    numero_de_resultados = "Foram encontrados " + str(len(resultados)) + " resultados para esta busca: '" + nome + "'. Os resultados também podem ser vistos no arquivo 'ultima_busca.csv' "
    return numero_de_resultados, resultados

# Função para pesquisar fermento por PREÇO
def func_pesquisar_por_preco_maximo(preco_maximo: str, cursor1):  ## não é preciso converter o preço para float aqui, pois o valor deve estar como string para funcionar na busca por f string abaixo

    selecionar_valor_buscado = f"SELECT * FROM tab_fermentos_1 WHERE preco_BRL <= {preco_maximo}"
    cursor1.execute(selecionar_valor_buscado)
    informacoes_sobre_fermentos = cursor1.fetchall()
    resultados = []  ## os resultados (em forma de dicionários) serão adicionados a essa lista
    for cada_linha_tabela_de_fermentos in informacoes_sobre_fermentos:
        cada_dicionario_de_fermentos = {
            "Nome do fermento": cada_linha_tabela_de_fermentos[0],
            "Preço (R$)": cada_linha_tabela_de_fermentos[1],
            "Descrição": cada_linha_tabela_de_fermentos[2],
            "Data do Scraping (YYYY-MM-DD)": cada_linha_tabela_de_fermentos[3],
            "Link": cada_linha_tabela_de_fermentos[4],
        }
        resultados.append(cada_dicionario_de_fermentos)

    if (len(resultados) == 0): func_csv_sem_resultados()  ## se a busca não retornar nenhum resultado, gera-se uma tabela vazia
    else: func_gerar_csv(f"WHERE preco_BRL <= {preco_maximo}", cursor1)

    numero_de_resultados = "Foram encontrados " + str(len(resultados)) + ' resultados de fermentos com preço abaixo de R$' + preco_maximo + ". Os resultados também podem ser vistos no arquivo 'ultima_busca.csv' "
    return numero_de_resultados, resultados

# Função para pesquisar fermento por NOME & PREÇO
def func_pesquisar_por_nome_e_preco(nome: str, preco_maximo: str, cursor1):
    selecionar_palavra_buscada = f"SELECT * FROM tab_fermentos_1 WHERE nome_do_produto_c LIKE ('%{nome}%') AND preco_BRL <= {preco_maximo}"
    cursor1.execute(selecionar_palavra_buscada)
    informacoes_sobre_fermentos = cursor1.fetchall()
    resultados = []  ## os resultados (em forma de dicionários) serão adicionados a essa lista
    for cada_linha_tabela_de_fermentos in informacoes_sobre_fermentos:
        cada_dicionario_de_fermentos = {
            "Nome do fermento": cada_linha_tabela_de_fermentos[0],
            "Preço (R$)": cada_linha_tabela_de_fermentos[1],
            "Descrição": cada_linha_tabela_de_fermentos[2],
            "Data do Scraping (YYYY-MM-DD)": cada_linha_tabela_de_fermentos[3],
            "Link": cada_linha_tabela_de_fermentos[4],
        }
        resultados.append(cada_dicionario_de_fermentos)

    if (len(resultados) == 0): func_csv_sem_resultados()  ## se a busca não retornar nenhum resultado, gera-se uma tabela vazia
    else: func_gerar_csv(f"WHERE nome_do_produto_c LIKE ('%{nome}%') AND preco_BRL <= {preco_maximo}", cursor1)

    numero_de_resultados = "Foram encontrados " + str(len(resultados)) + ' resultados de fermentos até R$ ' + preco_maximo + " para esta busca: '" + nome + "'. Os resultados também podem ser vistos no arquivo 'ultima_busca.csv' "
    return numero_de_resultados, resultados

# Função para pesquisar fermento por DESCRIÇÃO
def func_pesquisar_por_descricao(descricao: str, cursor1):

    selecionar_palavra_buscada = f"SELECT * FROM tab_fermentos_1 WHERE descricao_c LIKE ('%{descricao}%')"
    cursor1.execute(selecionar_palavra_buscada)
    informacoes_sobre_fermentos = cursor1.fetchall()
    resultados = []  ## os resultados (em forma de dicionários) serão adicionados a essa lista
    for cada_linha_tabela_de_fermentos in informacoes_sobre_fermentos:
        cada_dicionario_de_fermentos = {
            "Nome do fermento": cada_linha_tabela_de_fermentos[0],
            "Preço (R$)": cada_linha_tabela_de_fermentos[1],
            "Descrição": cada_linha_tabela_de_fermentos[2],
            "Data do Scraping (YYYY-MM-DD)": cada_linha_tabela_de_fermentos[3],
            "Link": cada_linha_tabela_de_fermentos[4],
        }
        resultados.append(cada_dicionario_de_fermentos)

    if (len(resultados) == 0): func_csv_sem_resultados()  ## se a busca não retornar nenhum resultado, gera-se uma tabela vazia
    else: func_gerar_csv(f"WHERE descricao_c LIKE ('%{descricao}%')", cursor1)

    numero_de_resultados = "Foram encontrados " + str(len(resultados)) + " resultados para esta busca: '" + descricao + "'. Os resultados também podem ser vistos no arquivo 'ultima_busca.csv' "
    return numero_de_resultados, resultados

    
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#



# Função para apagar os resultados da base de dados e recriar a tabela do zero
def func_recriar_tabela(con1, cursor1):
    # agora vamos definir as propriedades das colunas da tabela de fermentos para criar ou recriar a tabela

    # o bloco abaixo serve para deletar uma tabela já criada anteriormente
    deletar1 = 'DROP TABLE IF EXISTS tab_fermentos_1'
    cursor1.execute(deletar1)
    con1.commit()

    # agora vamos criar uma nova tabela
    propriedades_tabela_1 = "CREATE TABLE tab_fermentos_1 (nome_do_produto_c TEXT, preco_BRL INTEGER, \
    descricao_c TEXT, data_do_scraping_YYYY_MM_DD TEXT, link_c TEXT)"
    # obs: '_c' significa 'coluna'

    # para salvar as alterações feitas
    cursor1.execute(propriedades_tabela_1)
    con1.commit()
    print("Tabela recriada")

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
# função de parsing essencial para o funcionamento de outras funções
def func_parsing (link):
    lista_links_para_fermentos_neste_site = [] ## a esta lista serão adicionados os links obtidos para as páginas de cada fermento

    # definido parâmetros e fazendo a requisição
    agent = {"User-Agent":'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'} ## esse 'agent' é pra usar como parâmetro do requests (pra evitar um erro de acesso negado)
    requisicao = requests.get(link, headers=agent) ## usa o 'requests' pra acessar o link da página que mostra todos os fermentos disponíveis pra compra e usa o parâmetro 'agent' para que a raspagem de dados seja possível na página
    #time.sleep(0.3) # espera alguns segundos
    #print(html_source) # se der certo vai printar '200' e pular linha. é útil pra ver onde acaba um resultado e começa outro
    soup = BeautifulSoup(requisicao.content, 'html.parser') ## usa o 'BeautifulSoup' pra ler o conteúdo da requisição feita
    #print(soup)
    return soup


def func_parsing_2(link): #função alternativa pra parsing pra quando a primeira falhar
    lista_links_para_fermentos_neste_site = []  ## a esta lista serão adicionados os links obtidos para as páginas de cada fermento

    # Cabeçalhos mais detalhados para simular um navegador real
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "TE": "Trailers"
    }

    # Fazendo a requisição com os novos cabeçalhos
    try:
        requisicao = requests.get(link, headers=headers)
        requisicao.raise_for_status()  # Isso irá gerar um erro se a resposta for 4xx ou 5xx
        soup = BeautifulSoup(requisicao.content, 'html.parser')  # Usando BeautifulSoup para fazer a parsing do HTML
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar o site: {e}")
        return None  # Retorna None em caso de erro na requisição
    return soup
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------------#

# funções para fazer o web scraping em cada site
def func_centralbrew(con1, cursor1):

    print("+-----------------   --------------------------   -----------------------   -------------------------   ------------------------+")
    print("+-----------------   --------------------------   -----------------------   -------------------------   ------------------------+")
    print("                               Próximo website a ser analisado: centralbrew.com.br \n")
    print("+-----------------   --------------------------   -----------------------   -------------------------   ------------------------+")

    link = 'https://centralbrew.com.br/fermentos?limit=100' ## link com "?limit=100" no final pra mostrar o máximo possível de produtos na página 1 (a página de fermentos nunca passa de 100 mesmo)

    lista_links_centralbrew = [] ## a esta lista serão adicionados os links obtidos para as páginas de cada fermento

    soup = func_parsing(link)

    # agora vamos obter os links dos fermentos à venda
    # através da opção "Inspecionar" do Chrome, foi constatado que os links estavam todos marcados pela tag <h4>, então fez-se:
    lista_de_elementos_que_contem_os_links = soup.find_all('h4') ## usa o 'BeautifulSoup' pra encontrar todas as tags 'h4' e transformar numa lista

    for elemento in lista_de_elementos_que_contem_os_links[1:]: ## define que será feita uma iteração em cada link obtido nessa lista (com exceção do elemento de index == 0, que não é um link de fermento. por isso o [1:])
        #print(elemento) ## para mostrar os dados que estão na lista
        link = elemento.find('a').get('href') ## como os links também estão acompanhados da tag 'a' e estão contidos em 'href', usamos o método 'find' do 'BeautifulSoup' para obtê-los
        print(link) ## mostra cada link obtido
        lista_links_centralbrew.append(link) ## adiciona cada link obtido à lista de links ('lista_links')

    print("\nForam obtidos",len(lista_links_centralbrew),"links no site centralbrew") ## mostra quantos links foram obtidos

    print("\n")
    print("+-------------------------------------------------------------------------------------------------------------------------------+")
    print("Web scraping em andamento...")
    print("+-------------------------------------------------------------------------------------------------------------------------------+")

    inicio = 0
    #fim = inicio + 1

    #lista_links_centralbrew = obter_links_centralbrew()

    #dicionario_fermentos = {} ## cria um dicionário vazio para adicionar as informações do delivery

    for link in lista_links_centralbrew[inicio:]: ## entra em cada link da lista

        try:

            soup = func_parsing(link)

            # para obter o nome do produto:
            nome_do_produto = soup.find('h1').get_text() ## obtêm o texto da tag <h1>, que o nome do produto
            print("Nome do produto:",nome_do_produto) ## mostra na tela

            # para obter o preço:
            achando_preco = (soup.find_all('h2')) ## encontra todos os elementos marcados pela tag <h2>
            #print(achando_preco) ## mostra o que foi armazenado nessa variável
            for elemento in achando_preco: ## define que será abordado cada elemento da recém criada lista 'achando_preco'
                elemento_sem_tags = elemento.get_text() ## pega somente o texto de cada elemento da lista (descartando as tags que vinham junto e poluíam a leitura)
                if 'R$' in elemento_sem_tags: ## procura pela string "R$" em cada elemento (pois o preço é o único que contêm 'R$')
                    preco_string = elemento_sem_tags.split("Por: ")[1] ## como a informação do preço vem com um "Por:" (ex:  Por: R$39,90), usamos o 'split' parar separar nesse "por: " e pegar o segundo elemento ([1]), que é o preço
                    preco = float( preco_string.replace(",",".").replace("R$","") ) ## remove o "R$", substitui as vírgulas por pontos e transforma o preço em float (pois ele vem como string)
                    print("\nPreço (R$):",preco) ## mostra o preço na tela  

            # para obter a descrição do produto
            descricao = (soup.find("div", class_="tab-pane active").get_text("\n")) ## pega o texto da descrição (cuja classe é "tab-pane active") e usa o método 'get_text' pra transformar numa string sem tags. A parte do ("\n") é pra pular linhas entre as informações
            print("\nDescrição:",descricao) ## mostra a descrição do produto na tela

            # para registrar a data do scraping
            data_do_scraping = str(datetime.date.today()) # registra a data  ## opção: usar 'str(datetime.date.today())[:-3]' para fatiar a string da data antes do dia, assim mostrando só mês e ano
            print("\nData do scraping (YYYY-MM-DD):",data_do_scraping)

            print("\nLink:",link) ## mostra o link abordado


            #salvar na tabela do sqlite
            cursor1.execute("INSERT INTO tab_fermentos_1 VALUES (?, ?, ?, ?, ?)", (nome_do_produto, preco, descricao, data_do_scraping, link))

            # try: ## tenta registrar o último link salvo para que seja conhecido o próximo link no qual recomeçar o scraping
            #     with open("ultimo_link_adicionado_centralbrew_adicionado.txt","w") as ultimo_link: ## cria/sobrescreve um txt com apenas o último link
            #         ultimo_link.write(link) ## escreve o último link

            #         ''' !!! '''  # agora tem que achar o índice correspondente a esse link na lista
                    
            # except:
            #     pass ## se não der certo, segue pro próximo


            try:
                print("\n✔ sucesso")
                print("+-------------------------------------------------------------------------------------------------------------------------------+")

            except:
                print("\n✘falha ao salvar as informações do link a seguir:",link,"\n")
                print("+-------------------------------------------------------------------------------------------------------------------------------+")

        
        except:
            print("\n✘falha ao obter informações do link a seguir:",link,"\n")
            
            # registrar link falhado num txt
            with open("links_falhados.txt","a") as links_falhados: ## dá append num txt com os links falhados (cria o txt se não existir)
                    links_falhados.write(link) ## escreve o último link
                    links_falhados.write(",") ## adiciona uma vírgula para separar as falhas

                    ''' !!! '''  # agora tem que achar o índice correspondente a esse link na lista

                    
            print("+-------------------------------------------------------------------------------------------------------------------------------+")


    # ao final
    con1.commit() ## pra salvar a database
    print("Web scraping em centralbrew.com.br finalizado") # para aparecer no terminal
    # return "Foram obtidas as informações dos fermentos disponíveis em centralbrew.com.br" # para aparecer na API
    return f"Foram obtidas as informações de {len(lista_links_centralbrew)} fermentos disponíveis no website centralbrew" ## para aparecer na API
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def func_mariacervejeira(con1, cursor1):
    
    print("\n")
    print("+-----------------   --------------------------   -----------------------   -------------------------   ------------------------+")
    print("+-----------------   --------------------------   -----------------------   -------------------------   ------------------------+")
    print("                               Próximo website a ser analisado: mariacervejeira.com.br \n")
    print("+-----------------   --------------------------   -----------------------   -------------------------   ------------------------+")

    # primeiramente, vamos obter todos os links de fermento do site mariacervejeira.com
    link = 'https://www.mariacervejeira.com.br/fermentos'

    lista_links_maria_cervejeira = [] ## a esta lista serão adicionados os links obtidos para as páginas de cada fermento

    soup = func_parsing (link)

    # agora vamos obter os links dos fermentos à venda
    # através da opção "Inspecionar" do Chrome, foi constatado que os links estavam todos marcados por 'li' e 'product col-sm-3', então fez-se:
    lista_de_elementos_que_contem_os_links = soup.find_all("li", class_='product col-sm-3') ## usa o 'BeautifulSoup' pra encontrar todas os produtos e transformar numa lista (ainda cheia de informações indesejáveis, então vamos lapidar essa lista ainda)
    #print(lista_de_elementos_que_contem_os_links)

    for elemento in lista_de_elementos_que_contem_os_links[:]: ## define que será feita uma iteração em cada elemento dessa lista
        #print(elemento) ## para mostrar os dados que estão na lista
        link = elemento.find('a').get('href') ## como os links também estão acompanhados da tag 'a' e estão contidos em 'href', usamos o método 'find' do 'BeautifulSoup' para obtê-los
        print(link) ## mostra cada link obtido
        lista_links_maria_cervejeira.append(link) ## adiciona cada link obtido à lista de links ('lista_links')

    print("\nForam obtidos",len(lista_links_maria_cervejeira),"links no site mariacervejeira") ## mostra quantos links foram obtidos



    #-----------------------------------------------------------------------------------------------------------------------------------

    # aqui se inicia a parte de web scraping

    print("Web scraping em andamento...")
    print("+-------------------------------------------------------------------------------------------------------------------------------+")

    inicio = 0
    #fim = inicio + 1


    for link in lista_links_maria_cervejeira[inicio:]: ## entra em cada link da lista

        try:

            soup = func_parsing(link)

            # para obter o nome do produto:
            nome_do_produto = soup.find('h1').get_text() ## obtêm o texto da tag <h1>, que o nome do produto
            print("Nome do produto:",nome_do_produto) ## mostra na tela

            preco_com_espaco = (soup.find("span", class_="PrecoPrincipal color-tone-2")).get_text() ##  vai mostrar o preço com um espaço antes, exemplo: " $ 27,00" 
            preco_text = preco_com_espaco.replace(" R$ ", "").replace(",",".") ## remove os espaços e o R$
            preco = float(preco_text) ## transforma em float (pois vinha como string)
            print("\nPreço (R$):",preco) ## mostra o preço na tela

            # para obter a descrição do produto
            lista_descricao = (soup.findAll("div", id="descricao"))
            descricao = "" ## cria uma string vazia, à qual será adicionada a descrição do produto
            for elemento in lista_descricao:
                trecho_da_descricao = elemento.get_text("\n\n") # A parte do ("\n\n") é pra pular linhas entre as informações
                descricao = descricao + trecho_da_descricao + "\n\n"
                print("\nDescrição:\n\n",descricao)

                # para registrar a data do scraping
                data_do_scraping = str(datetime.date.today()) # registra a data  ## opção: usar 'str(datetime.date.today())[:-3]' para fatiar a string da data antes do dia, assim mostrando só mês e ano
                print("\nData do scraping (YYYY-MM-DD):",data_do_scraping)

                print("\nLink:",link) ## mostra o link abordado

                cursor1.execute("INSERT INTO tab_fermentos_1 VALUES (?, ?, ?, ?, ?)", (nome_do_produto, preco, descricao, data_do_scraping, link))

                # try: ## tenta registrar o último link salvo para que seja conhecido o próximo link no qual recomeçar o scraping
                #     with open("ultimo_link_do_maria_cervejeira_adicionado.txt","w") as ultimo_link: ## cria/sobrescreve um txt com apenas o último link
                #         ultimo_link.write(link) ## escreve o último link

                #         ''' !!! '''  # agora tem que achar o índice correspondente a esse link na lista
                        
                # except:
                #     pass ## se não der certo, segue pro próximo

            try:
                print("\n✔ sucesso")
                print("+-------------------------------------------------------------------------------------------------------------------------------+")

            except:
                print("\n✘falha ao salvar as informações do link a seguir:",link,"\n")
                print("+-------------------------------------------------------------------------------------------------------------------------------+")

        
        except:
            print("\n✘falha ao obter informações do link a seguir:",link,"\n")
            
            # registrar link falhado num txt
            with open("links_falhados.txt","a") as links_falhados: ## dá append num txt com os links falhados (cria o txt se não existir)
                    links_falhados.write(link) ## escreve o último link
                    links_falhados.write(",") ## adiciona uma vírgula para separar as falhas

                    ''' !!! '''  # agora tem que achar o índice correspondente a esse link na lista

                    
            print("+-------------------------------------------------------------------------------------------------------------------------------+")

    # ao final
    con1.commit() ## pra salvar a database
    print("Web scraping em mariacervejeira.com.br finalizado") # para aparecer no terminal
    # return "Foram obtidas as informações dos fermentos disponíveis em mariacervejeira.com.br" # para aparecer na API
    return f"Foram obtidas as informações de {len(lista_links_maria_cervejeira)} fermentos disponíveis no website mariacervejeira" ## para aparecer na API
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def func_piquiribrewshop(con1, cursor1):

    print("\n")
    print("+-----------------   --------------------------   -----------------------   -------------------------   ------------------------+")
    print("+-----------------   --------------------------   -----------------------   -------------------------   ------------------------+")
    print("                             Próximo website a ser analisado: piquiribrewshop.com.br \n")
    print("+-----------------   --------------------------   -----------------------   -------------------------   ------------------------+")

    # passo 1: obter número de páginas para automatizar a troca
    ## é preciso analisar todos os fermentos até a última páginas, mas, para isso, precisamos saber o número de páginas

    link = 'https://www.piquiribrewshop.com.br/fermentos?pagina=1'
    soup = func_parsing_2(link)

    informacao_de_quantas_paginas = soup.find_all("div",class_= "pagination") ## será encontrada uma lista com dois itens, sendo que o primeiro item já basta para acharmos o número de páginas de fermento desse site
    # sendo assim, podemos pegar o primeiro item ([0]) da lista para ver o número de páginas, que será o maior número que aparecer
    sem_quebras = informacao_de_quantas_paginas[0].text.replace("\n"," ") ## replace("\n"," ") pra substituir as quebras de linha por espaços
    # agora, caso tenhamos (por exemplo) 7 páginas, teremos uma string assim:        1 2 3 ... 6 7      
    # isso vem dos botões para ir para as páginas 1,2,3,6 e 7, sendo o último número igual à quantidade de páginas de fermento (7, no caso)
    # sendo assim, vamos separar essa string em elementos de uma lista para que seja possível obter o último desses elementos (o número de páginas)
    numeros_de_pagina_em_lista = sem_quebras.split(" ")
    # agora já teremos uma lista, mas cheia de elementos em branco (''), que devem ser eliminados
    lista_sem_vazios = []
    for elemento in numeros_de_pagina_em_lista:
        if elemento != '':
            lista_sem_vazios.append(elemento)
    # finalmente teremos uma lista na qual o último elemento é o número de páginas. ex: ['1', '2', '3', '...', '6', '7']
    # portanto, vamos pegar o último elemento dessa lista

    numero_de_paginas = int(lista_sem_vazios[-1]) ## lembrando de transformar o número de string pra int

    #print("este site tem",numero_de_paginas,"páginas de fermentos")


    #-----------------------------------------------------------------------------------------------------------------------------------------------------#

    # passo 2: obter links de produtos disponíveis

    lista_links_disponiveis_piquiri = [] # cria uma lista vazia, à qual serão adicionados os links obtidos no site

    # agora repetiremos um processo para a obtenção dos links em cada uma das páginas do site
    for i in range (1, (numero_de_paginas+1) ): ## aqui o número precisa estar na forma de int para ser usado no range e +1 é porque o range exclui o último valor, então é preciso adicionar +1 pra que ele também passe pela última página
        print("\nObtendo os links da página", i) ## mostra a página na qual a operação se encontra
        link = 'https://www.piquiribrewshop.com.br/fermentos?pagina=' + str(i) ## lembrando que é preciso transformar o número em int de novo
        print(link,"\n")

        soup = func_parsing_2(link) ## executa a função previamente definida como 'parsing' e salva seu conteúdo em 'soup'
        # print(soup)


        # agora vamos extrair o que tiver dentro de '<div class="bandeiras-produto">'
        # e se tiver isso aqui '<span class="bandeira-indisponivel fundo-secundario">indisponível</span>' é pra ignorar o link

        lista_para_encontrar_disponibilidade = soup.find_all("div", class_="bandeiras-produto")
        #print(lista_para_encontrar_disponibilidade)
        lista_disponiveis = [] ## a essa lista serão adicionados os índices dos produtos disponíveis para compra (e essa linha recria a lista do zero a cada vez que uma página analisada)
        for index, item in enumerate(lista_para_encontrar_disponibilidade): ## enumera os elementos da lista para identificá-los
            if('indisponível' in str(item)): ## se o elemento tiver a palavra 'indisponível' em seu conteudo:
                #print("Index",index,"Indisponível") ## apenas printa que não está disponível e não salva o índice
                pass
            else: ## se o elemento não tiver 'indisponível' em seu conteúdo
                lista_disponiveis.append(index) ## salva o índice desse produto numa lista de produtos disponíveis
                #print("Index",index,"Disponível")

        #print("índices dos links de fermentos disponíveis:",lista_disponiveis) ## apenas os produtos cujos índices estiverem contidos nessa lista terão seus links salvos



        # agora vamos obter os links dos fermentos à venda
        # através da opção "Inspecionar" do Chrome, foi constatado que os links estavam todos marcados por 'li' e 'product col-sm-3', então fez-se:
        lista_de_elementos_que_contem_os_links = soup.find_all("a", class_='produto-sobrepor') ## usa o 'BeautifulSoup' pra encontrar todas os produtos e transformar numa lista (ainda cheia de informações indesejáveis, então vamos lapidar essa lista ainda)
        #print("total:",len(lista_de_elementos_que_contem_os_links))

        for index, elemento in enumerate(lista_de_elementos_que_contem_os_links): ## enumera a lista de links encontrados para analisá-los um por um
            try:
                if index in lista_disponiveis:
                    #print(elemento) ## para mostrar os dados que estão na lista
                    link = elemento.get('href') ## como os links também estão acompanhados da tag 'a' e estão contidos em 'href', usamos o método 'find' do 'BeautifulSoup' para obtê-los
                    #print("index:",index,"-",link) ## mostra cada link obtido e seu respectivo index na página
                    print(link) ## mostra cada link obtido
                    lista_links_disponiveis_piquiri.append(link) ## adiciona cada link obtido à lista de links ('lista_links')
            except:
                print("falha em",link)

        #print("\nForam obtidos", len(lista_links_disponiveis_piquiri),"links de fermentos disponíveis para compra no piquiribrewshop até agora")
        print("+-------------------------------------------------------------------------------------------------------------------------------+")

    ## ao final:
    print("\nForam obtidos", len(lista_links_disponiveis_piquiri),"links de fermentos disponíveis para compra no piquiribrewshop")


    #-----------------------------------------------------------------------------------------------------------------------------------------------------#
    # passo 3: web scraping das páginas de fermentos disponíveis

    # tabela de detalhes dos produtos do piquiribrewshop

    print("\nWeb scraping em andamento...")
    print("+-------------------------------------------------------------------------------------------------------------------------------+")

    inicio = 0
    #fim = inicio + 1


    for link in lista_links_disponiveis_piquiri[inicio:]: ## entra em cada link da lista

        try:

            soup = func_parsing_2(link)

            # para obter o nome do produto:
            nome_do_produto = soup.find('h1').get_text() ## obtêm o texto da tag <h1>, que o nome do produto
            print("Nome do produto:",nome_do_produto) ## mostra na tela

            # para obter o preço do produto
            preco_com_espaco = (soup.find("strong", class_="preco-promocional cor-principal titulo")).get_text() ##  vai mostrar o preço com um espaço antes, exemplo: " $ 27,00" 
            preco_text = preco_com_espaco.replace(" R$ ", "").replace(",",".") ## remove os espaços e o R$
            preco = float(preco_text) ## transforma em float (pois vinha como string)
            print("\nPreço (R$):",preco) ## mostra o preço na tela


            # para obter a descrição do produto
            lista_descricao = (soup.findAll("div", id="descricao"))
            descricao = "" ## cria uma string vazia, à qual será adicionada a descrição do produto
            for elemento in lista_descricao:
                trecho_da_descricao = elemento.get_text("\n") # A parte do ("\n") é pra pular linhas entre as informações
                descricao = descricao + trecho_da_descricao + "\n"
                print("\nDescrição:\n\n",descricao)

                # para registrar a data do scraping
                data_do_scraping = str(datetime.date.today()) # registra a data  ## opção: usar 'str(datetime.date.today())[:-3]' para fatiar a string da data antes do dia, assim mostrando só mês e ano
                print("\nData do scraping (YYYY-MM-DD):",data_do_scraping)

                print("\nLink:",link) ## mostra o link abordado

                cursor1.execute("INSERT INTO tab_fermentos_1 VALUES (?, ?, ?, ?, ?)", (nome_do_produto, preco, descricao, data_do_scraping, link))

                # try: ## tenta registrar o último link salvo para que seja conhecido o próximo link no qual recomeçar o scraping
                #     with open("ultimo_link_do_maria_cervejeira_adicionado.txt","w") as ultimo_link: ## cria/sobrescreve um txt com apenas o último link
                #         ultimo_link.write(link) ## escreve o último link

                #         ''' !!! '''  # agora tem que achar o índice correspondente a esse link na lista
                        
                # except:
                #     pass ## se não der certo, segue pro próximo

            try:
                print("\n✔ sucesso")
                print("+-------------------------------------------------------------------------------------------------------------------------------+")

            except:
                print("\n✘falha ao salvar as informações do link a seguir:",link,"\n")
                print("+-------------------------------------------------------------------------------------------------------------------------------+")

        
        except:
            print("\n✘falha ao obter informações do link a seguir:",link,"\n")
            
            # registrar link falhado num txt
            with open("links_falhados.txt","a") as links_falhados: ## dá append num txt com os links falhados (cria o txt se não existir)
                    links_falhados.write(link) ## escreve o último link
                    links_falhados.write(",") ## adiciona uma vírgula para separar as falhas

                    ''' !!! '''  # agora tem que achar o índice correspondente a esse link na lista

                    
            print("+-------------------------------------------------------------------------------------------------------------------------------+")

    # ao final
    con1.commit() ## pra salvar a database
    print("Web scraping em piquiribrewshop.com.br finalizado") # para aparecer no terminal
    # return "Foram obtidas as informações dos fermentos disponíveis em piquiribrewshop.com.br" # para aparecer na API
    return f"Foram obtidas as informações de {len(lista_links_disponiveis_piquiri)} fermentos disponíveis no website piquiribrewshop" ## para aparecer na API
#-----------------------------------------------------------------------------------------------------------------------------------------------------#





## Funções para deletar resultados
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def func_deletar_centralbrew(con1, cursor1):
    site = "%centralbrew%"
    deletar_fornecedor = "DELETE FROM tab_fermentos_1 WHERE link_c LIKE ?"
    cursor1.execute(deletar_fornecedor, (site,))
    con1.commit()
    print("Resultados de centralbrew deletados") ## pra aparecer no terminal
    return "Foram deletados os resultados provenientes do fornecedor centralbrew" ## pra aparecer na API
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def func_deletar_mariacervejeira(con1, cursor1):
    site = "%mariacervejeira%"
    deletar_fornecedor = "DELETE FROM tab_fermentos_1 WHERE link_c LIKE ?"
    cursor1.execute(deletar_fornecedor, (site,))
    con1.commit()
    print("Resultados de mariacervejeira deletados") ## pra aparecer no terminal
    return "Foram deletados os resultados provenientes do fornecedor mariacervejeira" ## pra aparecer na API
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def func_deletar_piquiribrewshop(con1, cursor1):
    site = "%piquiribrewshop%"
    deletar_fornecedor = "DELETE FROM tab_fermentos_1 WHERE link_c LIKE ?"
    cursor1.execute(deletar_fornecedor, (site,))
    con1.commit()
    print("Resultados de piquiribrewshop deletados") ## pra aparecer no terminal
    return "Foram deletados os resultados provenientes do fornecedor piquiribrewshop" ## pra aparecer na API
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
