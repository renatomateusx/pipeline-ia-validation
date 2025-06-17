from datetime import datetime
from sqlalchemy.orm import Session
from .models import Token
from fastapi import HTTPException

class TokenService:
    @staticmethod
    async def validate_token(db: Session, token: str) -> Token:
        # Busca o token no banco
        db_token = db.query(Token).filter(Token.token == token).first()
        
        if not db_token:
            raise HTTPException(
                status_code=401,
                detail="Token inválido"
            )
        
        # Verifica se o token está ativo
        if not db_token.is_active:
            raise HTTPException(
                status_code=401,
                detail="Token inativo"
            )
        
        # Verifica se o pagamento está válido
        if db_token.payment_status != "paid":
            raise HTTPException(
                status_code=401,
                detail="Pagamento pendente ou inválido"
            )
        
        # Verifica se o token não expirou
        if db_token.expires_at < datetime.now():
            raise HTTPException(
                status_code=401,
                detail="Token expirado"
            )
        
        return db_token

    @staticmethod
    async def create_token(
        db: Session,
        token: str,
        company_name: str,
        expires_at: datetime
    ) -> Token:
        db_token = Token(
            token=token,
            company_name=company_name,
            payment_status="pending",
            expires_at=expires_at
        )
        db.add(db_token)
        db.commit()
        db.refresh(db_token)
        return db_token

    @staticmethod
    async def update_payment_status(
        db: Session,
        token: str,
        status: str
    ) -> Token:
        db_token = db.query(Token).filter(Token.token == token).first()
        if not db_token:
            raise HTTPException(
                status_code=404,
                detail="Token não encontrado"
            )
        
        db_token.payment_status = status
        db.commit()
        db.refresh(db_token)
        return db_token 