import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Boolean, Float, Integer, ForeignKey, 
    DateTime, JSON, Enum
)
from sqlalchemy.orm import relationship
from backend.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(30), nullable=True)
    role = Column(String(20), default="cliente", nullable=False) # cliente, trabajador, admin
    
    # Worker/Profile Information
    province = Column(String(100), default="Santo Domingo")
    municipality = Column(String(100), default="Distrito Nacional")
    description = Column(Text, default="")
    experience_years = Column(Integer, default=1)
    hourly_rate_rd = Column(Float, default=0.0)
    availability = Column(String(50), default="Disponible")
    profile_photo_url = Column(Text, default="")
    portfolio_urls = Column(JSON, default=list) # List of image URLs
    categories = Column(JSON, default=list) # List of category IDs or names
    
    # Verification System (INFOTEP & Cédula Dominicana)
    is_verified = Column(Boolean, default=False)
    verification_status = Column(String(20), default="sin_solicitar") # sin_solicitar, pendiente, aprobado, rechazado
    id_card_number = Column(String(30), default="") # Cédula JCE (ej: 402-XXXXXXX-X)
    is_id_card_verified = Column(Boolean, default=False)
    has_infotep_certificate = Column(Boolean, default=False)
    infotep_course_name = Column(String(150), default="")
    infotep_doc_url = Column(Text, default="")
    
    # Stats & Status
    rating_average = Column(Float, default=5.0)
    total_ratings = Column(Integer, default=0)
    completed_jobs = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_suspended = Column(Boolean, default=False)
    must_change_password = Column(Boolean, default=False)
    created_by_admin_id = Column(String(36), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    published_chambas = relationship("Chamba", back_populates="client", foreign_keys="Chamba.client_id")
    assigned_chambas = relationship("Chamba", back_populates="worker", foreign_keys="Chamba.worker_id")
    postulaciones = relationship("Postulacion", back_populates="worker")
    sent_messages = relationship("Message", back_populates="sender", foreign_keys="Message.sender_id")
    received_messages = relationship("Message", back_populates="receiver", foreign_keys="Message.receiver_id")
    notifications = relationship("Notification", back_populates="user")
    reviews_given = relationship("Review", back_populates="author", foreign_keys="Review.author_id")
    reviews_received = relationship("Review", back_populates="recipient", foreign_keys="Review.recipient_id")
    bank_account = relationship("WorkerBankAccount", back_populates="worker", uselist=False, cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "categories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(80), unique=True, nullable=False)
    icon_name = Column(String(50), default="build")
    description = Column(Text, default="")
    min_price_rd = Column(Float, default=500.0)
    max_price_rd = Column(Float, default=5000.0)
    is_active = Column(Boolean, default=True)


class Chamba(Base):
    __tablename__ = "chambas"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(150), nullable=False, index=True)
    description = Column(Text, nullable=False)
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=True)
    category_name = Column(String(80), default="General")
    
    client_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    worker_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    province = Column(String(100), default="Santo Domingo")
    municipality = Column(String(100), default="Distrito Nacional")
    budget_rd = Column(Float, default=0.0)
    
    status = Column(String(30), default="publicada", index=True)
    # Estados: publicada, recibiendo_postulaciones, trabajador_seleccionado, contratada, en_progreso, trabajo_terminado, completada, cancelada, en_disputa
    
    photos = Column(JSON, default=list) # URLs of photos
    scheduled_date = Column(String(50), default="")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    client = relationship("User", foreign_keys=[client_id], back_populates="published_chambas")
    worker = relationship("User", foreign_keys=[worker_id], back_populates="assigned_chambas")
    postulaciones = relationship("Postulacion", back_populates="chamba", cascade="all, delete-orphan")
    contract = relationship("Contract", back_populates="chamba", uselist=False)
    payment = relationship("Payment", back_populates="chamba", uselist=False)
    messages = relationship("Message", back_populates="chamba", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="chamba")


class Postulacion(Base):
    __tablename__ = "postulaciones"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    chamba_id = Column(String(36), ForeignKey("chambas.id"), nullable=False, index=True)
    worker_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    proposal_message = Column(Text, default="")
    proposed_price_rd = Column(Float, default=0.0)
    status = Column(String(20), default="pendiente") # pendiente, aceptada, rechazada, retirada
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    chamba = relationship("Chamba", back_populates="postulaciones")
    worker = relationship("User", back_populates="postulaciones")


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    chamba_id = Column(String(36), ForeignKey("chambas.id"), unique=True, nullable=False)
    client_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    worker_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    agreed_price_rd = Column(Float, nullable=False)
    status = Column(String(30), default="activo") # activo, finalizado_por_tecnico, confirmado_cliente, disputado, cancelado
    
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    chamba = relationship("Chamba", back_populates="contract")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    chamba_id = Column(String(36), ForeignKey("chambas.id"), unique=True, nullable=False)
    client_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    worker_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    total_amount_rd = Column(Float, nullable=False)
    commission_rate = Column(Float, default=0.10) # 10%
    commission_amount_rd = Column(Float, default=0.0)
    worker_payout_rd = Column(Float, default=0.0)
    
    status = Column(String(30), default="pendiente") 
    # Estados de pago: pendiente, comprobante_subido, en_revision, confirmado, rechazado, retenido, liberado, reembolsado, en_disputa
    transaction_ref = Column(String(100), default="")
    
    # Comprobante de transferencia bancaria
    receipt_url = Column(Text, default="")
    receipt_notes = Column(Text, default="")
    receipt_uploaded_at = Column(DateTime, nullable=True)
    
    # Revisión y auditoría del Administrador
    verified_by_admin_id = Column(String(36), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, default="")
    
    # Datos bancarios congelados al momento de la transferencia
    bank_account_used_id = Column(String(36), nullable=True)
    bank_name_used = Column(String(100), default="")
    account_number_used = Column(String(50), default="")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    released_at = Column(DateTime, nullable=True)

    chamba = relationship("Chamba", back_populates="payment")
    payout = relationship("TechnicianPayout", back_populates="payment", uselist=False)


class BankAccountConfig(Base):
    __tablename__ = "bank_account_configs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    bank_name = Column(String(100), nullable=False) # e.g. Banreservas, Banco Popular, BHD
    account_holder = Column(String(150), nullable=False) # e.g. CHAMBA RD S.R.L.
    account_type = Column(String(50), nullable=False) # Cuenta de Ahorros, Cuenta Corriente
    account_number = Column(String(50), nullable=False)
    rnc_or_cedula = Column(String(50), default="")
    is_active = Column(Boolean, default=True)
    notes = Column(Text, default="")
    created_by_admin_id = Column(String(36), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BankAccountAudit(Base):
    __tablename__ = "bank_account_audits"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    admin_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False) # CREATE, UPDATE, ACTIVATE, DEACTIVATE
    account_id = Column(String(36), nullable=True)
    old_data = Column(JSON, default=dict)
    new_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)


class TechnicianPayout(Base):
    __tablename__ = "technician_payouts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    payment_id = Column(String(36), ForeignKey("payments.id"), nullable=False)
    chamba_id = Column(String(36), ForeignKey("chambas.id"), nullable=False)
    worker_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    gross_amount_rd = Column(Float, nullable=False)
    commission_rate = Column(Float, default=0.10)
    commission_amount_rd = Column(Float, default=0.0)
    net_payout_rd = Column(Float, nullable=False)
    
    status = Column(String(30), default="pendiente") # pendiente, pagado, rechazado
    paid_at = Column(DateTime, nullable=True)
    payment_method = Column(String(50), default="Transferencia Bancaria")
    transfer_reference = Column(String(100), default="")
    processed_by_admin_id = Column(String(36), nullable=True)
    payout_receipt_url = Column(Text, default="")
    notes = Column(Text, default="")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    payment = relationship("Payment", back_populates="payout")
    chamba = relationship("Chamba")
    worker = relationship("User", foreign_keys=[worker_id])


class WorkerBankAccount(Base):
    __tablename__ = "worker_bank_accounts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    worker_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    bank_name = Column(String(100), nullable=False)
    account_holder = Column(String(150), nullable=False)
    account_type = Column(String(50), nullable=False) # e.g. "Cuenta de Ahorros", "Cuenta Corriente"
    account_number = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    worker = relationship("User", back_populates="bank_account")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    chamba_id = Column(String(36), ForeignKey("chambas.id"), nullable=False, index=True)
    sender_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    receiver_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    chamba = relationship("Chamba", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(30), default="info") # postulacion, seleccion, pago, chat, review, verificacion, disputa
    chamba_id = Column(String(36), default="")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    chamba_id = Column(String(36), ForeignKey("chambas.id"), nullable=False)
    author_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    recipient_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    rating = Column(Float, nullable=False) # 1.0 - 5.0
    comment = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    chamba = relationship("Chamba", back_populates="reviews")
    author = relationship("User", foreign_keys=[author_id], back_populates="reviews_given")
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="reviews_received")


class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    reporter_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    reported_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    chamba_id = Column(String(36), default="")
    
    reason = Column(String(80), nullable=False)
    description = Column(Text, default="")
    evidence_url = Column(Text, default="")
    status = Column(String(20), default="pendiente") # pendiente, en_revision, resuelto, desestimado
    admin_resolution = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


class Dispute(Base):
    __tablename__ = "disputes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    chamba_id = Column(String(36), ForeignKey("chambas.id"), nullable=False)
    creator_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    reason = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    evidence_url = Column(Text, default="")
    status = Column(String(20), default="abierta") # abierta, en_revision, resuelta, cancelada
    resolution = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    target_type = Column(String(20), nullable=False) # worker, chamba
    target_id = Column(String(36), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class PriceReference(Base):
    __tablename__ = "price_references"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    category = Column(String(80), nullable=False, index=True)
    service_name = Column(String(120), nullable=False)
    unit_type = Column(String(50), default="unidad") # punto, m2, unidad, jornada_dia, salida
    min_price_rd = Column(Float, nullable=False)
    max_price_rd = Column(Float, nullable=False)
    estimated_time = Column(String(60), default="1-3 horas")
    includes_materials = Column(Boolean, default=False)
    notes = Column(Text, default="")


class PlatformConfig(Base):
    __tablename__ = "platform_configs"

    key = Column(String(80), primary_key=True)
    value = Column(String(255), nullable=False)
    description = Column(Text, default="")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
