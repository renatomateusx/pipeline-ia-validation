from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .models import Company, Token, Payment
from fastapi import HTTPException
import uuid

class PaymentService:
    @staticmethod
    async def process_paypal_ipn(db: Session, ipn_data: dict) -> Token:
        """
        Processa uma notificação IPN do PayPal e cria/atualiza os registros necessários
        """
        # Verifica se o pagamento já foi processado
        existing_payment = db.query(Payment).filter(
            Payment.payment_id == ipn_data.get("txn_id")
        ).first()

        if existing_payment:
            raise HTTPException(
                status_code=400,
                detail="Pagamento já processado"
            )

        # Verifica se a empresa já existe
        company = db.query(Company).filter(
            Company.email == ipn_data.get("payer_email")
        ).first()

        if not company:
            # Cria nova empresa
            company = Company(
                name=ipn_data.get("first_name", "") + " " + ipn_data.get("last_name", ""),
                email=ipn_data.get("payer_email")
            )
            db.add(company)
            db.commit()
            db.refresh(company)

        # Registra o pagamento
        payment = Payment(
            company_id=company.id,
            payment_id=ipn_data.get("txn_id"),
            amount=ipn_data.get("mc_gross"),
            currency=ipn_data.get("mc_currency"),
            status=ipn_data.get("payment_status"),
            payment_date=datetime.now()
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)

        # Se o pagamento foi aprovado, cria um novo token
        if ipn_data.get("payment_status") == "Completed":
            # Desativa tokens antigos da empresa
            db.query(Token).filter(
                Token.company_id == company.id,
                Token.is_active == True
            ).update({"is_active": False})

            # Cria novo token
            token = Token(
                company_id=company.id,
                payment_status="paid",
                expires_at=datetime.now() + timedelta(days=30)
            )
            db.add(token)
            db.commit()
            db.refresh(token)

            return token

        raise HTTPException(
            status_code=400,
            detail="Status de pagamento inválido"
        )

    @staticmethod
    async def get_company_tokens(db: Session, company_id: int) -> list[Token]:
        """
        Retorna todos os tokens ativos de uma empresa
        """
        return db.query(Token).filter(
            Token.company_id == company_id,
            Token.is_active == True
        ).all() 