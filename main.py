from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
from datetime import datetime
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.database import get_db, engine
from app.models import Base, ValidationLog
from app.token_service import TokenService
from app.ai_service import AIServiceFactory
from app.payment_service import PaymentService

# Carrega variáveis de ambiente
load_dotenv()

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Pipeline Validation API",
    description="API para validação de pipelines CI/CD usando IA",
    version="1.0.0"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class ValidationRequest(BaseModel):
    token: str
    payload: Dict[str, Any]

class ValidationResponse(BaseModel):
    status: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now()

class PayPalIPNResponse(BaseModel):
    token: str
    expires_at: datetime
    company_name: str

@app.get("/")
async def root():
    return {"message": "Pipeline Validation API"}

@app.post("/validate", response_model=ValidationResponse)
async def validate_pipeline(
    request: ValidationRequest,
    db: Session = Depends(get_db)
):
    # Valida o token
    token = await TokenService.validate_token(db, request.token)
    
    # Cria instância do serviço de IA
    ai_service = AIServiceFactory.create_service()
    
    # Realiza a análise
    analysis_result = await ai_service.analyze(request.payload)
    
    # Salva o log da validação
    validation_log = ValidationLog(
        token_id=token.id,
        payload=request.payload,
        result=analysis_result,
        status=analysis_result["status"]
    )
    db.add(validation_log)
    db.commit()
    
    return ValidationResponse(
        status=analysis_result["status"],
        message="Validação realizada com sucesso",
        details=analysis_result["details"],
        timestamp=datetime.now()
    )

@app.post("/paypal/ipn", response_model=PayPalIPNResponse)
async def paypal_ipn(
    request: Request,
    db: Session = Depends(get_db)
):
    # Obtém os dados do IPN
    form_data = await request.form()
    ipn_data = dict(form_data)
    
    # Processa o pagamento e cria o token
    token = await PaymentService.process_paypal_ipn(db, ipn_data)
    
    return PayPalIPNResponse(
        token=str(token.token),
        expires_at=token.expires_at,
        company_name=token.company.name
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 