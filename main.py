from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pymysql

app = FastAPI(title="API Energia+")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    return pymysql.connect(
        host="gateway01.us-east-1.prod.aws.tidbcloud.com",
        port=4000,
        user="2Wvat7nBiqfsb1q.root",
        password="rNF82pYmi2AapeAv",
        database="energia_db",
        ssl={"ca": "/etc/ssl/certs/ca-certificates.crt"},
        cursorclass=pymysql.cursors.DictCursor
    )

class LeituraRequest(BaseModel):
    usuario_id: int
    kwh_atual: float

@app.get("/")
def home():
    return {"status": "API Energia+ online!"}

@app.post("/api/previsao")
def prever_e_salvar(leitura: LeituraRequest):
    tarifa_kwh = 0.95
    projecao_mensal = round(leitura.kwh_atual * 1.5, 2)
    valor_fatura = round(projecao_mensal * tarifa_kwh, 2)

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO leituras (usuario_id, kwh_atual, projecao_kwh, valor_estimado)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (leitura.usuario_id, leitura.kwh_atual, projecao_mensal, valor_fatura))
        conn.commit()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro de conexão com o MySQL: {str(e)}")

    return {
        "status": "sucesso",
        "usuario_id": leitura.usuario_id,
        "consumo_inserido_kwh": leitura.kwh_atual,
        "projecao_final_mes_kwh": projecao_mensal,
        "estimativa_fatura_R$": valor_fatura
    }
