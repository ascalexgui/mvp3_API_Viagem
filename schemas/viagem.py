from pydantic import BaseModel
from pydantic import BaseModel
from typing import Optional, List
from models.viagem import Viagem

import requests
import json
import pprint


class ViagemSchema(BaseModel):
    """ Define como uma nova viagem a ser inserido deve ser representado
    """
    cidade: str = "Rio de Janeiro"
    descricao: str = "Cidade maravilhosa"
    qtd_dias: int = "15"
    ano: int = "2024"
    mes: str = "Janeiro"
   

class ViagemViewSchema(BaseModel):
    """ Define como uma nova viagem a ser inserida deve ser representada
    """
    cidade: str = "Rio de Janeiro"
    descricao: str = "Cidade maravilhosa"
    qtd_dias: int = "15"
    ano: int = "2024"
    mes: str = "Janeiro"

class ViagemBuscaPorCidadeSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca. Que será
        feita apenas com base no nome da cidade.
    """
    cidade: str = "Rio de Janeiro"


class ViagemBuscaPorIDSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca. Que será
        feita apenas com base no ID da viagem
    """
    id: int = 1

class ViagemAtualizaSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca para atualização dos dados da viagem. Que será
        feita apenas com base no ID da viagem
    """ 
    id: int = 0 
    descricao: str = ""
   
class ListagemViagensSchema(BaseModel):
    """ Define como uma listagem de viagem será retornada.
    """
    viagens:List[ViagemViewSchema]

class ViagemRoteiroViewSchema(BaseModel):
    """Define como deve ser a estrutura que representa a busca. 
       A busca do roteiro será realizada pelo ID da viagem.
       Através do ID da viagem buscamos os dados da cidade + qtd_dias
    """
    id: int = 1


class ViagemViewSchema(BaseModel):
    """ Define como uma viagem será retornado: viagem
    """
    id: int = 1
    cidade: str = "Rio de Janeiro"
    descricao: str = "Cidade maravilhosa"
    qtd_dias: int = "15"
    ano: int = "2024"
    mes: str = "Janeiro"


class ViagemDelSchema(BaseModel):
    """ Define como deve ser a estrutura do dado retornado após uma requisição
        de remoção.
    """
    mesage: str
    id: int


def apresenta_viagem(viagem: Viagem):
    """ Retorna uma representação da viagem seguindo o schema definido em
        ViagemViewSchema.
    """
    return {
        "id": viagem.id,
        "cidade": viagem.cidade,
        "descricao": viagem.descricao,
        "qtd_dias": viagem.qtd_dias,
        "ano": viagem.ano,
        "mes": viagem.mes,
    }

def apresenta_viagens(viagens: List[Viagem]):
    """ Retorna uma representação da viagem seguindo o schema definido em
        ListagemViagensSchema.
    """
    result = []
    for viagem in viagens:
        result.append({
            "id": viagem.id,
            "cidade": viagem.cidade,
            "descricao": viagem.descricao,
            "qtd_dias": viagem.qtd_dias,
            "ano": viagem.ano,
            "mes": viagem.mes,
        })

    return {"viagens": result}

def apresenta_roteiro(mensagem:any ):
    """ Retorna uma representação do roteiro seguindo o schema definido em
        RoteiroSchema.
    """
    return {
        "roteiro": mensagem
    }

def valida_cidade_IBGE (strCidade):

    link = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios?orderBy=nome"

    requisicao = requests.get(link)

    print(requisicao)

    retornocidade = requisicao.json()

    ## Vamos procurar no dicionário "retornoCidade" se a cidade informada no cadastro é valida no Brasil

    achou = False

    for x in retornocidade:
        for k in x.items():
            
            if x['nome'] == strCidade:
                achou = True
                break

    return achou




