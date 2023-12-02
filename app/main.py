from fastapi import FastAPI
from classes import RequestIngrediente, RequestPostReceita, RequestPutReceita, RequestMedida
from models import Ingrediente, Receita, IngredienteReceita, session
from publisher import Publisher
import logging, copy

logger = logging.getLogger(__name__)
logging.getLogger("pika").propagate = False
FORMAT = "[%(asctime)s %(filename)s->%(funcName)s():%(lineno)s]%(levelname)s: %(message)s"
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.DEBUG)


config = {
    'host': 'rabbitmq-service',
    'port': 5672,
    'exchange': 'receitas'
}

app = FastAPI()

@app.get("/")
async def root():
    logger.debug("(GET) Rota: '/'")

    return {
        "status": "SUCCESS",
        "data": "NO DATA"
    }

@app.get("/ingredientes")
async def get_ingredientes():
    logger.info("(GET) Rota: '/ingredientes'")

    ingredientes_query = session.query(Ingrediente)
    ingredientes = ingredientes_query.all()
    
    if not ingredientes:
        return {
            "status": "SUCCESS",
            "data": "Nenhum ingrediente encontrado."
        }

    return {
        "status": "SUCCESS",
        "data": ingredientes
    }

@app.get("/ingrediente/{id}")
async def get_ingrediente(id):
    logger.info(f"(GET) Rota: '/ingrediente/{id}'")

    ingrediente_query = session.query(Ingrediente).filter(
        Ingrediente.id == id
    )
    ingrediente = ingrediente_query.first()
    if ingrediente == None:
        return {
            "status": "SUCCESS",
            "data": f"Ingrediente não encontrado."
        }

    return {
        "status": "SUCCESS",
        "data": ingrediente
    }

@app.get("/ingredientes/{id_receita}")
async def get_ingredientes_by_receita(id_receita):
    logger.info(f"(GET) Rota: '/ingredientes/{id_receita}'")

    receita_query = session.query(Receita).filter(
        Receita.id == id_receita
    )
    receita = receita_query.first()

    if receita == None:
        return {
            "status": "SUCCESS",
            "data": f"Receita não encontrada."
        }

    
    ingredientes_receitas = receita.ingredientes
    ingredientes = []

    for ingrediente_receita in ingredientes_receitas:
        ingrediente_query = session.query(Ingrediente).filter(
            Ingrediente.id == ingrediente_receita.idIngrediente
        )
        ingrediente = ingrediente_query.first()
        ingrediente_medida = copy.deepcopy(ingrediente)
        ingrediente_medida.medida = ingrediente_receita.medida
        ingredientes.append(ingrediente_medida)
    
    if not ingredientes:
        return  {
            "status": "SUCCESS",
            "data": "Essa receita não possui nenhum ingrediente."
        }

    return {
        "status": "SUCCESS",
        "data": ingredientes
    }

@app.post("/ingredientes")
async def post_ingrediente(request_ingrediente: RequestIngrediente):
    logger.info(f"(POST) Rota: '/ingredientes'\n\t - {request_ingrediente}")

    ingrediente_json = request_ingrediente

    ingrediente = Ingrediente(
        nome = ingrediente_json.nome
    )
    session.add(ingrediente)
    session.commit()

    return {
        "status": "SUCCESS",
        "data": ingrediente_json
    }
    

@app.get("/receitas")
async def get_receitas():
    logger.info("(GET) Rota: '/receitas'")

    receitas_query = session.query(Receita)
    receitas = receitas_query.all() 
    
    if not receitas:
        return {
            "status": "SUCCESS",
            "data": "Nenhuma receita encontrada."
        }

    return {
        "status": "SUCCESS",
        "data": receitas,
    }

@app.get("/receita/{id}")
async def get_receita(id):
    logger.info(f"(GET) Rota: '/receita/{id}'")

    receita_query = session.query(Receita).filter(
        Receita.id == id
    )

    receita = receita_query.first()

    if receita == None:
        return {
            "status": "SUCCESS",
            "data": f"Receita não encontrada."
        }

    return {
        "status": "SUCCESS",
        "data": receita
    }

@app.get("/receitas/{id_ingrediente}")
async def get_receitas_by_ingrediente(id_ingrediente):
    logger.info(f"(GET) Rota: '/receitas/{id_ingrediente}'")

    ingrediente_query = session.query(Ingrediente).filter(
        Ingrediente.id == id_ingrediente
    )
    ingrediente = ingrediente_query.first()
    
    if ingrediente == None:
        return {
            "status": "SUCCESS",
            "data": "Ingrediente não encontrado."
        }

    ingredientes_receitas = ingrediente.receitas

    receitas = []

    for ingrediente_receita in ingredientes_receitas:
        receita_query = session.query(Receita).filter(
            Receita.id == ingrediente_receita.idReceita
        )
        receita = receita_query.first()
        receitas.append(receita)
    
    if not receitas:
        return {
            "status": "SUCCESS",
            "data": "Esse ingrediente não está em nenhuma receita."
        }

    return {
        "status": "SUCCESS",
        "data": receitas
    }

@app.post("/receitas")
async def post_receita(request_receita: RequestPostReceita):
    logger.info(f"(POST) Rota: '/receitas'\n\t - {request_receita}")

    receita_json = request_receita
    
    receita = Receita(
        titulo = receita_json.titulo,
    )
    session.add(receita)
    session.commit()

    return {
        "status": "SUCCESS",
        "data": receita_json
    }

@app.put("/ingrediente/{id}")
async def put_ingrediente(id, request_ingrediente: RequestIngrediente):
    logger.info(f"(PUT) Rota: '/ingrediente/{id}'\n\t - {request_ingrediente}")

    ingrediente_json = request_ingrediente
    ingrediente_query = session.query(Ingrediente).filter(
        Ingrediente.id == id
    )
    ingrediente = ingrediente_query.first()

    if ingrediente == None:
        return {
            "status": "SUCCESS",
            "data": "Ingrediente não encontrado."
        }

    if ingrediente_json.nome == "string":
        ingrediente.nome = ingrediente_json.nome
    session.commit()

    return {
        "status": "SUCCESS",
        "data": ingrediente_json
    }

@app.delete("/ingrediente/{id}")
async def delete_ingrediente(id):
    logger.info(f"(DELETE) Rotas: '/ingrediente/{id}")

    ingrediente_query = session.query(Ingrediente).filter(
        Ingrediente.id == id
    )
    ingrediente = ingrediente_query.first()
    
    if ingrediente == None:
        return {
            "status": "SUCCESS",
            "data": "Ingrediente não encontrado."
        }

    session.delete(ingrediente)
    session.commit()

    return {
        "status": "SUCCESS",
    }

@app.put("/receita/{id}/details")
async def put_receita(id, request_receita: RequestPutReceita):
    logger.info(f"(PUT) Rota: '/receita/{id}/details'\n\t - {request_receita}")

    receita_json = request_receita
    receita_query = session.query(Receita).filter(
        Receita.id == id
    )
    receita = receita_query.first()

    if receita == None:
        return {
            "status": "SUCCESS",
            "data": "Receita não encontrada."
        }

    if receita_json.titulo != "string":
        receita.titulo = receita_json.titulo
    if receita_json.modo_de_preparo != "string":
        receita.modo_de_preparo = receita_json.modo_de_preparo
    if receita_json.tempo_de_preparo != "string":
        receita.tempo_de_preparo = receita_json.tempo_de_preparo
    session.commit()

    return {
        "status": "SUCCESS",
        "data": receita_json
    }


@app.post("/receita/{id_receita}/ingrediente/{id_ingrediente}")
async def post_ingrediente_in_receita(id_receita, id_ingrediente, request_medida: RequestMedida):
    logger.info(f"(POST) Rota: '/receita/{id_receita}/ingrediente/{id_ingrediente}'\n\t - {request_medida}")

    medida_json = request_medida

    receita_query = session.query(Receita).filter(
        Receita.id == id_receita
    )
    receita = receita_query.first()

    if receita == None:
        return {
            "status": "SUCCESS",
            "data": "Receita não encontrada."
        }

    ingrediente_query = session.query(Ingrediente).filter(
        Ingrediente.id == id_ingrediente
    )
    ingrediente = ingrediente_query.first()

    if ingrediente == None:
        return {
            "status": "SUCCESS",
            "data": "Ingrediente não encontrado."
        }

    ingrediente_receita = IngredienteReceita(
        idIngrediente = ingrediente.id,
        idReceita = receita.id,
        medida = medida_json.medida
    )

    session.add(ingrediente_receita)
    session.commit()

    return {
        "status": "SUCCESS",
        "data": medida_json
    }

@app.put("/receita/{id_receita}/ingrediente/{id_ingrediente}")
async def put_ingrediente_in_receita(id_receita, id_ingrediente, request_medida: RequestMedida):
    logger.info(f"(PUT) Rota: '/receita/{id_receita}/ingrediente/{id_ingrediente}'\n\t - {request_medida}")

    medida_json = request_medida
    
    ingrediente_receita_query = session.query(IngredienteReceita).filter(
        IngredienteReceita.idIngrediente == id_ingrediente,
        IngredienteReceita.idReceita == id_receita
    )
    ingrediente_receita = ingrediente_receita_query.first()

    if ingrediente_receita == None:
        return {
            "status": "SUCCESS",
            "data": "Par IngredienteReceita não encontado."
        }

    if medida_json.medida != "string":
        ingrediente_receita.medida = medida_json.medida
    session.commit()

    return {
        "status": "SUCCESS",
        "data": medida_json
    }

@app.delete("/receita/{id_receita}/ingrediente/{id_ingrediente}")
async def delete_ingrediente_from_receita(id_receita, id_ingrediente):
    logger.info(f"(DELETE) Rota: '/receita/{id_receita}/ingrediente/{id_ingrediente}'")

    ingrediente_receita_query = session.query(IngredienteReceita).filter(
        IngredienteReceita.idReceita == id_receita,
        IngredienteReceita.idIngrediente == id_ingrediente
    )
    ingrediente_receita = ingrediente_receita_query.first()
    
    if ingrediente_receita == None:
        return {
            "status": "SUCCESS",
            "data": "Par IngredienteReceita não encontado."
        }
    
    session.delete(ingrediente_receita)    
    session.commit()

    return {
        "status": "SUCCESS",
    }

@app.delete("/receita/{id}")
async def delete_receita(id):
    logger.info(f"(DELETE) Rotas: '/receita/{id}")

    receita_query = session.query(Receita).filter(
        Receita.id == id
    )
    receita = receita_query.first()

    if receita == None:
        return {
            "status": "SUCCESS",
            "data": "Receita não encontrada."
        }

    session.delete(receita)
    session.commit()

    return {
        "status": "SUCCESS",
    }

@app.get("/enviar_receitas", status_code=200)
async def get_all_receitas():
    receitas_to_send = []
    logger.info('Coletando as informações das receitas no banco de dados')
    try:
        receitas_query = session.query(Receita)
        receitas = receitas_query.all()
        for receita in receitas:
            item = {
                "titulo": receita.titulo,
                "modo_de_preparo": receita.modo_de_preparo,
                "tempo_de_preparo": receita.tempo_de_preparo
            }
            receita_serializer = RequestPutReceita(**item)            
            receitas_to_send.append(receita_serializer)
      
        publisher = Publisher(config)  
        logger.info('Enviando mensagem para o RabbitMQ')       
        publisher.publish('receitas', receita_serializer.model_dump_json().encode())
    except Exception as e:
         logger.error(f'Erro na consulta das receitas -- get_all_receitas() -- {e}')
         print(e)
    return {
        "status": "SUCCESS",
        "result": "OK"
    }
