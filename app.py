from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect
from urllib.parse import unquote

from sqlalchemy.exc import IntegrityError

from models import Session, Viagem
from logger import logger
from schemas import *
from flask_cors import CORS

import json
import requests

info = Info(title="Minha API para planejamento de viagens", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
viagem_tag = Tag(name="Viagem", description="Adição, visualização, atualização e remoção de viagens planejadas à base")


@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')


@app.post('/nova_viagem', tags=[viagem_tag],
          responses={"200": ViagemViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_produto(form: ViagemSchema):
    """Adiciona uma nova Viagem à base de dados

    Retorna uma representação das viagens e roteiro associado.
    """
    print(form)
    viagem = Viagem(
        cidade=form.cidade,
        descricao=form.descricao,
        qtd_dias=form.qtd_dias,
        ano=form.ano,
        mes=form.mes
    )

    # validando o nome da cidade informada pelo usuário
    # só vamos permitir cadastro de cidades nacionais
    # a validação será realizada através do serviço disponibilizado pelo IBGE.

    # https://servicodados.ibge.gov.br/api/v1/localidades/municipios?orderBy=nome

    if valida_cidade_IBGE(viagem.cidade):

        logger.info(f"Adicionando viagem para a cidade: '{viagem.cidade}'")
        try:
            # criando conexão com a base
            session = Session()
            # adicionando viagem
            session.add(viagem)
            # efetivando o comando de adição de novo item na tabela
            session.commit()
            logger.info("Adicionado viagem: %s"% viagem)
            return apresenta_viagem(viagem), 200

        except IntegrityError as e:
            # como a duplicidade do nome da cidade + ano + Mês é a provável razão do IntegrityError
            error_msg = "Viagem para mesma cidade no mesmo ano+mês na base :/"
            logger.warning(f"Erro ao adicionar viagem '{viagem.cidade}', {error_msg}")
            return {"mesage": error_msg}, 409

        except Exception as e:
            # caso um erro fora do previsto
            error_msg = "Não foi possível salvar nova viagem :/"
            logger.warning(f"Erro ao adicionar viagem '{viagem.cidade}', {error_msg}")
            return {"mesage": error_msg}, 400
    else:
        error_msg = "Cidade não encontrada no cadastro do IBGE :/"
        logger.warning(f"Não foi possível adicionar viagem com uma cidade inválida '{viagem.cidade}', {error_msg}")
        return {"mesage": error_msg}, 409
        

@app.get('/listaviagens', tags=[viagem_tag],
         responses={"200": ListagemViagensSchema, "404": ErrorSchema})
def get_lista_viagens():
    """Lista todas as Viagens cadastradas

    Retorna uma representação da listagem de viagens.
    """
    logger.info(f"Coletando viagem ")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    viagens = session.query(Viagem).all()

    if not viagens:
        # se não há viagem cadastradas
        return {"viagens": []}, 200
    else:
        logger.info(f"%d viagens encontradas" % len(viagens))
        # retorna a representação da viagem
        return apresenta_viagens(viagens), 200


@app.get('/busca_viagem_por_id', tags=[viagem_tag],
         responses={"200": ViagemViewSchema, "404": ErrorSchema})
def get_viagem(query: ViagemBuscaPorIDSchema):
    """Faz a busca por uma Viagem a partir do id da viagem

    Retorna uma representação das viagens e roteiro associado.
    """
    viagem_id = query.id
    logger.info(f"Coletando dados sobre viagem #{viagem_id}")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    viagem = session.query(Viagem).filter(Viagem.id == viagem_id).first()

    if not viagem:
        # se a viagem não foi encontrada
        error_msg = "Viagem não encontrado na base :/"
        logger.warning(f"Erro ao buscar viagem '{viagem_id}', {error_msg}")
        return {"mesage": error_msg}, 404
    else:
        logger.info("Viagem econtrada: %s" % viagem)
        # retorna a representação da viagem
        return apresenta_viagem(viagem), 200


@app.delete('/deleta_viagem_por_id', tags=[viagem_tag],
            responses={"200": ViagemDelSchema, "404": ErrorSchema})
def del_viagem_id(query: ViagemBuscaPorIDSchema):
    """Deleta uma Viagem a partir do id informado

    Retorna uma mensagem de confirmação da remoção.
    """
    viagem_id = query.id
    logger.info(f"Deletando dados sobre viagem #{viagem_id}")
    # criando conexão com a base
    session = Session()
    # fazendo a remoção
    count = session.query(Viagem).filter(Viagem.id == viagem_id).delete()
    session.commit()

    if count:
        # retorna a representação da mensagem de confirmação
        logger.info(f"Deletado viagem #{viagem_id}")
        return {"mesage": "Viagem removida", "id": viagem_id}
    else:
        # se a viagem não foi encontrada
        error_msg = "Viagem não encontrado na base :/"
        logger.warning(f"Erro ao deletar viagem #'{viagem_id}', {error_msg}")
        return {"mesage": error_msg}, 404
    

@app.delete('/deleta_viagem_cidade', tags=[viagem_tag],
            responses={"200": ViagemDelSchema, "404": ErrorSchema})
def del_viagem_cidade(query: ViagemBuscaPorCidadeSchema):
    """Deleta uma Viagem a partir do nome da cidade

    Retorna uma mensagem de confirmação da remoção.
    """
    viagem_cidade = unquote(unquote(query.cidade))
    logger.info(f"Deletando dados sobre viagem #{viagem_cidade}")
    # criando conexão com a base
    session = Session()
    # fazendo a remoção
    count = session.query(Viagem).filter(Viagem.cidade == viagem_cidade).delete()
    session.commit()

    if count:
        # retorna a representação da mensagem de confirmação
        logger.info(f"Deletado viagem #{viagem_cidade}")
        return {"mesage": "Viagem removida", "id": viagem_cidade}
    else:
        # se a viagem não foi encontrada
        error_msg = "Viagem não encontrado na base :/"
        logger.warning(f"Erro ao deletar viagem #'{viagem_cidade}', {error_msg}")
        return {"mesage": error_msg}, 404

@app.get('/busca_viagem_cidade', tags=[viagem_tag],
         responses={"200": ListagemViagensSchema, "404": ErrorSchema})
def busca_viagem(query: ViagemBuscaPorCidadeSchema):
    """Faz a busca por viagem através do nome da cidade.

    Retorna uma representação das viagens e roteiros associados.
    """
    termo = unquote(query.cidade)
    logger.info(f"Fazendo a busca por cidade que contém: {termo}")
    # criando conexão com a base
    session = Session()
    # fazendo a remoção
    viagens = session.query(Viagem).filter(Viagem.cidade.ilike(f"%{termo}%")).all()
    
    if not viagens:
        # se não há viagens cadastrados
        return {"viagens": []}, 200
    else:
        logger.info(f"%d viagens econtradas" % len(viagens))
        # retorna a representação de viagem
        return apresenta_viagens(viagens), 200

# Rota para atualizar os dados da viagem.
@app.put('/atualiza_viagem', tags=[viagem_tag],
         responses={"200": ViagemAtualizaSchema, "404": ErrorSchema})
def atualiza_viagem(form: ViagemAtualizaSchema):
    """Atualiza os dados de uma Viagem a partir do id informado

    Retorna uma mensagem de confirmação da atualização
    """
    viagem_id = form.id
    logger.info(f"Atualizando os dados da viagem #{viagem_id}")
     # criando conexão com a base
    session = Session()
    # fazendo a busca
    count = session.query(Viagem).filter(Viagem.id == viagem_id).update({Viagem.descricao:form.descricao}) 

    if not count:
        # se a viagem não foi encontrada
        error_msg = "Viagem não encontrada na base :/"
        logger.warning(f"Erro ao buscar viagem '{viagem_id}', {error_msg}")
        return {"mesage": error_msg}, 404
    else:
        # retorna a representação da mensagem de confirmação
        session.commit()
        logger.info(f"Atualizando viagem #{viagem_id}")
        return {"mesage": "Viagem atualizada", "id": viagem_id}


# Rota para buscar o roteiro da viagem no CHATGPT
@app.get('/busca_roteiro_viagem_id', tags=[viagem_tag],
         responses={"200": ViagemRoteiroViewSchema, "404": ErrorSchema})
def get_roteiroviagemid (query: ViagemBuscaPorIDSchema):
    """Faz a busca por uma Viagem a partir do id da viagem e solicita o roteiro ao serviço externo do CHATGPT

    Retorna uma representação do roteiro da viagem
    """
    viagem_id = query.id
    logger.info(f"Coletando dados sobre viagem #{viagem_id}")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    viagem = session.query(Viagem).filter(Viagem.id == viagem_id).first()

    if not viagem:
        # se a viagem não foi encontrada
        error_msg = "Viagem não encontrado na base :/"
        logger.warning(f"Erro ao buscar viagem '{viagem_id}', {error_msg}")
        return {"mesage": error_msg}, 404
    else:
        logger.info("Viagem encontrada: %s" % viagem.cidade)
        # busca o roteiro
        url = f"http://127.0.0.1:5000/busca_roteiro?cidade={viagem.cidade}&qtd_dias={viagem.qtd_dias}"
        
        requisicao = requests.get(url)

        print(requisicao)

        retornoRoteiro = requisicao.json()

        return(retornoRoteiro)
