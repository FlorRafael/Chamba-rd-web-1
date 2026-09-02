from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime

# --- AUTH & USER SCHEMAS ---
class UserRegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str
    role: str = "cliente" # Solo 'cliente' o 'tecnico'/'trabajador'. 'admin' está estrictamente prohibido.
    province: Optional[str] = "Santo Domingo"
    municipality: Optional[str] = "Distrito Nacional"
    description: Optional[str] = ""
    experience_years: Optional[int] = 1

    @field_validator("role")
    @classmethod
    def validate_public_registration_role(cls, v: str) -> str:
        clean = (v or "").strip().lower()
        if clean in ["admin", "administrador", "superadmin", "moderador", "root"]:
            raise ValueError("Acceso no autorizado: El rol de administrador no está permitido en el registro público. Debe configurarse internamente.")
        if clean not in ["cliente", "tecnico", "trabajador"]:
            raise ValueError("Rol no válido para registro público. Debe ser 'cliente' o 'tecnico'.")
        return "trabajador" if clean in ["tecnico", "trabajador"] else "cliente"

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    province: Optional[str] = None
    municipality: Optional[str] = None
    description: Optional[str] = None
    experience_years: Optional[int] = None
    hourly_rate_rd: Optional[float] = None
    availability: Optional[str] = None
    profile_photo_url: Optional[str] = None
    portfolio_urls: Optional[List[str]] = None
    categories: Optional[List[str]] = None

class VerificationSubmitRequest(BaseModel):
    id_card_number: str
    infotep_course_name: Optional[str] = ""
    infotep_doc_url: Optional[str] = ""

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class AdminCreateRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone: Optional[str] = None
    role: str
    province: str
    municipality: str
    description: str
    experience_years: int
    hourly_rate_rd: float
    availability: str
    profile_photo_url: str
    portfolio_urls: List[str]
    categories: List[str]
    is_verified: bool
    verification_status: str
    id_card_number: Optional[str] = ""
    is_id_card_verified: bool
    has_infotep_certificate: bool
    infotep_course_name: Optional[str] = ""
    rating_average: float
    total_ratings: int
    completed_jobs: int
    is_active: bool
    must_change_password: bool = False
    created_by_admin_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- CHAMBA SCHEMAS ---
class ChambaCreateRequest(BaseModel):
    title: str
    description: str
    category_id: Optional[str] = None
    category_name: Optional[str] = "General"
    province: Optional[str] = "Santo Domingo"
    municipality: Optional[str] = "Distrito Nacional"
    budget_rd: float
    scheduled_date: Optional[str] = ""
    photos: Optional[List[str]] = []

class ChambaUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    province: Optional[str] = None
    municipality: Optional[str] = None
    budget_rd: Optional[float] = None
    status: Optional[str] = None
    photos: Optional[List[str]] = None

class ChambaResponse(BaseModel):
    id: str
    title: str
    description: str
    category_id: Optional[str] = None
    category_name: str
    client_id: str
    client_name: Optional[str] = None
    worker_id: Optional[str] = None
    worker_name: Optional[str] = None
    province: str
    municipality: str
    budget_rd: float
    status: str
    photos: List[str]
    scheduled_date: str
    postulaciones_count: Optional[int] = 0
    created_at: datetime

    class Config:
        from_attributes = True

# --- POSTULACION SCHEMAS ---
class PostulacionCreateRequest(BaseModel):
    chamba_id: str
    proposal_message: Optional[str] = ""
    proposed_price_rd: float

class PostulacionResponse(BaseModel):
    id: str
    chamba_id: str
    chamba_title: Optional[str] = None
    worker_id: str
    worker_name: Optional[str] = None
    worker_photo: Optional[str] = None
    worker_rating: Optional[float] = 5.0
    worker_jobs: Optional[int] = 0
    worker_verified: Optional[bool] = False
    proposal_message: str
    proposed_price_rd: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- REVIEWS & RATINGS ---
class ReviewCreateRequest(BaseModel):
    chamba_id: str
    recipient_id: str
    rating: float = Field(ge=1.0, le=5.0)
    comment: Optional[str] = ""

class ReviewResponse(BaseModel):
    id: str
    chamba_id: str
    author_id: str
    author_name: Optional[str] = None
    author_photo: Optional[str] = None
    recipient_id: str
    rating: float
    comment: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- PAYMENTS, BANK ACCOUNTS & COMMISSIONS ---
class BankAccountCreateRequest(BaseModel):
    bank_name: str
    account_holder: str
    account_type: str
    account_number: str
    rnc_or_cedula: Optional[str] = ""
    is_active: Optional[bool] = True
    notes: Optional[str] = ""

class BankAccountUpdateRequest(BaseModel):
    bank_name: Optional[str] = None
    account_holder: Optional[str] = None
    account_type: Optional[str] = None
    account_number: Optional[str] = None
    rnc_or_cedula: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None

class BankAccountResponse(BaseModel):
    id: str
    bank_name: str
    account_holder: str
    account_type: str
    account_number: str
    rnc_or_cedula: Optional[str] = ""
    is_active: bool
    notes: Optional[str] = ""
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BankAccountAuditResponse(BaseModel):
    id: str
    admin_id: str
    action: str
    account_id: Optional[str] = None
    old_data: Optional[dict] = {}
    new_data: Optional[dict] = {}
    created_at: datetime

    class Config:
        from_attributes = True

class CommissionUpdateRequest(BaseModel):
    commission_rate: float = Field(ge=0.0, le=0.5, description="Tasa de comisión entre 0% y 50%")
    reason: Optional[str] = ""

class PaymentCreateRequest(BaseModel):
    chamba_id: str
    total_amount_rd: float

class PaymentReceiptUploadRequest(BaseModel):
    receipt_url: str
    receipt_notes: Optional[str] = ""
    transaction_ref: Optional[str] = ""

class PaymentVerificationActionRequest(BaseModel):
    action: str # "confirmar" or "rechazar"
    rejection_reason: Optional[str] = ""

class TechnicianPayoutMarkPaidRequest(BaseModel):
    payment_method: Optional[str] = "Transferencia Bancaria"
    transfer_reference: str
    payout_receipt_url: Optional[str] = ""
    notes: Optional[str] = ""

# --- DATOS BANCARIOS DEL TÉCNICO PARA RECIBIR PAGOS ---
class WorkerBankAccountCreateRequest(BaseModel):
    bank_name: str
    account_holder: str
    account_type: str
    account_number: str
    confirm_account_number: str

    @field_validator("bank_name", "account_holder", "account_type", "account_number")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        clean = (v or "").strip()
        if not clean:
            raise ValueError("Este campo no puede estar vacío.")
        return clean

    @field_validator("confirm_account_number")
    @classmethod
    def validate_account_matching(cls, v: str, info) -> str:
        acc = info.data.get("account_number", "").strip()
        if v.strip() != acc:
            raise ValueError("Los dos números de cuenta no coinciden. Por favor verifícalos.")
        return v.strip()

class WorkerBankAccountResponse(BaseModel):
    id: str
    worker_id: str
    bank_name: str
    account_holder: str
    account_type: str
    account_number: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TechnicianPayoutResponse(BaseModel):
    id: str
    payment_id: str
    chamba_id: str
    chamba_title: Optional[str] = None
    worker_id: str
    worker_name: Optional[str] = None
    gross_amount_rd: float
    commission_rate: float
    commission_amount_rd: float
    net_payout_rd: float
    status: str
    paid_at: Optional[datetime] = None
    payment_method: Optional[str] = None
    transfer_reference: Optional[str] = None
    processed_by_admin_id: Optional[str] = None
    payout_receipt_url: Optional[str] = None
    notes: Optional[str] = None
    # Datos bancarios del técnico para realizar el pago manual (solo visible para admin autorizado)
    worker_bank_name: Optional[str] = None
    worker_account_holder: Optional[str] = None
    worker_account_type: Optional[str] = None
    worker_account_number: Optional[str] = None
    worker_has_bank_account: bool = False
    created_at: datetime

    class Config:
        from_attributes = True

class PaymentResponse(BaseModel):
    id: str
    chamba_id: str
    chamba_title: Optional[str] = None
    client_id: str
    client_name: Optional[str] = None
    worker_id: str
    worker_name: Optional[str] = None
    total_amount_rd: float
    commission_rate: float
    commission_amount_rd: float
    worker_payout_rd: float
    status: str
    transaction_ref: str
    receipt_url: Optional[str] = ""
    receipt_notes: Optional[str] = ""
    receipt_uploaded_at: Optional[datetime] = None
    verified_by_admin_id: Optional[str] = None
    verified_at: Optional[datetime] = None
    rejection_reason: Optional[str] = ""
    bank_account_used_id: Optional[str] = None
    bank_name_used: Optional[str] = ""
    account_number_used: Optional[str] = ""
    created_at: datetime
    released_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class FinancialSummaryResponse(BaseModel):
    total_recibido_rd: float
    comisiones_ganadas_rd: float
    pagos_tecnicos_efectuados_rd: float
    pagos_tecnicos_pendientes_rd: float
    total_transacciones: int
    comision_porcentaje_actual: float
    cuenta_bancaria_activa: Optional[BankAccountResponse] = None

# --- MESSAGING ---
class MessageCreateRequest(BaseModel):
    chamba_id: str
    receiver_id: str
    content: str

class MessageResponse(BaseModel):
    id: str
    chamba_id: str
    sender_id: str
    sender_name: Optional[str] = None
    receiver_id: str
    content: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- NOTIFICATIONS ---
class NotificationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    type: str
    chamba_id: Optional[str] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- ESTIMATOR SCHEMAS ---
class PriceReferenceResponse(BaseModel):
    id: str
    category: str
    service_name: str
    unit_type: str
    min_price_rd: float
    max_price_rd: float
    estimated_time: str
    includes_materials: bool
    notes: str

    class Config:
        from_attributes = True

class PriceEstimateCalculateRequest(BaseModel):
    service_id: str
    quantity: float = 1.0

class PriceEstimateResult(BaseModel):
    service_name: str
    category: str
    quantity: float
    unit_type: str
    total_min_rd: float
    total_max_rd: float
    disclaimer: str = "Los precios son orientativos. El precio final puede variar según materiales, dificultad, ubicación, urgencia y acuerdo entre cliente y técnico."

# --- REPORTS & DISPUTES ---
class ReportCreateRequest(BaseModel):
    reported_user_id: Optional[str] = None
    chamba_id: Optional[str] = None
    reason: str
    description: str
    evidence_url: Optional[str] = ""

class DisputeCreateRequest(BaseModel):
    chamba_id: str
    reason: str
    description: str
    evidence_url: Optional[str] = ""

# --- ATENCIÓN AL CLIENTE / CONFIGURACIÓN DE SOPORTE ---
class SupportConfigRequest(BaseModel):
    phone: str
    whatsapp: str
    business_hours: str
    email: Optional[str] = "soporte@chambard.com"
    whatsapp_welcome_message: Optional[str] = "Hola CHAMBA RD, necesito asistencia con la plataforma."

class SupportConfigResponse(BaseModel):
    phone: str
    whatsapp: str
    business_hours: str
    email: str
    whatsapp_welcome_message: str
    clean_phone_for_dial: str
    clean_whatsapp_for_link: str
    updated_at: Optional[datetime] = None
    last_updated_by: Optional[str] = None
