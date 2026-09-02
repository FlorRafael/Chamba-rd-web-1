import os
from backend.database import SessionLocal, engine, Base
from backend.models import User, Category, PriceReference, PlatformConfig
from backend.auth import get_password_hash
from backend.config import settings

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # 1. Platform Commission Configuration
        if not db.query(PlatformConfig).filter(PlatformConfig.key == "platform_commission_rate").first():
            db.add(PlatformConfig(
                key="platform_commission_rate",
                value="0.10",
                description="Comisión porcentual retenida por CHAMBA RD por cada trabajo completado"
            ))
            
        # 2. Categories
        categories_data = [
            ("Plomería", "plumbing", "Instalación de tuberías, grifería, inodoros, bombas de agua y tinacos", 800, 4500),
            ("Electricidad", "electrical_services", "Puntos de luz, tomacorrientes, paneles de breakers, inversores y cableado", 600, 6000),
            ("Pintura", "format_paint", "Pintura residencial y comercial de interiores, exteriores y techos", 700, 10000),
            ("Aire Acondicionado", "ac_unit", "Mantenimiento preventivo, recarga de gas e instalación de splits inverter", 1500, 6500),
            ("Albañilería", "foundation", "Pegado de bloques, empañete, colocación de pisos y porcelanato", 1200, 15000),
            ("Cerrajería", "key", "Apertura de puertas, cambio de llavines y cerraduras de seguridad", 800, 3000),
            ("Refrigeración", "kitchen", "Reparación de neveras, freezers y exhibidores comerciales", 1200, 5000),
            ("Limpieza", "cleaning_services", "Limpieza profunda de apartamentos, casas y muebles", 1500, 5000),
            ("Jardinería", "yard", "Poda de árboles, corte de grama y mantenimiento de áreas verdes", 1000, 4000)
        ]
        
        for name, icon, desc, min_p, max_p in categories_data:
            if not db.query(Category).filter(Category.name == name).first():
                db.add(Category(
                    name=name,
                    icon_name=icon,
                    description=desc,
                    min_price_rd=min_p,
                    max_price_rd=max_p
                ))
                
        # 3. Dominican Reference Prices (RD$)
        prices_data = [
            ("Plomería", "Instalación de Fregadero / Lavamanos", "unidad", 1000, 2000, "1-2 horas", False, "Mano de obra para conexión de desagüe y llaves"),
            ("Plomería", "Instalación de Inodoro", "unidad", 1500, 2800, "2-3 horas", False, "Fijación y sellado con cera y silicon"),
            ("Plomería", "Reparación de Fuga de Tubería", "punto", 800, 1800, "1-3 horas", False, "Detección y empalme PVC"),
            ("Plomería", "Instalación de Tinaco / Bomba de Agua", "unidad", 2500, 5500, "3-5 horas", False, "Incluye conexiones hidráulicas y eléctricas"),
            
            ("Electricidad", "Instalación de Tomacorriente / Interruptor", "punto", 350, 700, "30-60 min", False, "Por cada punto eléctrico nuevo o sustitución"),
            ("Electricidad", "Instalación de Lámpara / Abanico de Techo", "unidad", 800, 1800, "1-2 horas", False, "Fijación y balanceo"),
            ("Electricidad", "Revisión y Balanceo de Panel de Breakers", "unidad", 1500, 3500, "2-4 horas", False, "Diagnóstico de sobrecargas y cortocircuitos"),
            ("Electricidad", "Instalación / Chequeo de Inversor", "unidad", 2000, 4500, "2-3 horas", False, "Conexión a banco de baterías"),
            
            ("Pintura", "Pintura de Paredes Interiores", "m2", 150, 300, "Según metraje", False, "Dos manos de pintura vinil/acrílica"),
            ("Pintura", "Pintura de Fachada Exterior", "m2", 200, 450, "Según metraje", False, "Incluye sellador y pintura resistente a intemperie"),
            ("Pintura", "Impermeabilización de Techos", "m2", 300, 650, "Según metraje", False, "Lona asfáltica o impermeabilizante acrílico"),
            
            ("Aire Acondicionado", "Mantenimiento Preventivo (Split)", "unidad", 1200, 2200, "1-2 horas", False, "Lavado químico de evaporador y condensador"),
            ("Aire Acondicionado", "Instalación de A/C Split (12k - 24k BTU)", "unidad", 3000, 5500, "2-4 horas", False, "Mano de obra, no incluye tubería adicional"),
            ("Aire Acondicionado", "Recarga de Gas Refrigerante (R410A/R22)", "unidad", 1800, 3500, "1 hora", True, "Incluye gas y prueba de fuga rápida"),
            
            ("Cerrajería", "Apertura de Puerta Residencial", "salida", 1000, 2500, "30-60 min", False, "Apertura sin daños mayores"),
            ("Cerrajería", "Instalación de Cerradura / Cerrojo", "unidad", 800, 1800, "1 hora", False, "Mano de obra"),
            
            ("Albañilería", "Colocación de Cerámica / Porcelanato", "m2", 400, 850, "Según metraje", False, "Nivelación y fraguado"),
            ("Albañilería", "Jornada Diaria de Albañil Maestro", "jornada_dia", 1800, 3000, "8 horas", False, "Tarifa estándar por día laborable")
        ]
        
        for cat, serv, unit, p_min, p_max, time_est, inc_mat, notes in prices_data:
            existing_ref = db.query(PriceReference).filter(
                PriceReference.category == cat,
                PriceReference.service_name == serv
            ).first()
            if not existing_ref:
                db.add(PriceReference(
                    category=cat,
                    service_name=serv,
                    unit_type=unit,
                    min_price_rd=p_min,
                    max_price_rd=p_max,
                    estimated_time=time_est,
                    includes_materials=inc_mat,
                    notes=notes
                ))
                
        # 3.1 Support Configs
        support_configs = [
            ("support_phone", "829-837-0908", "Número telefónico oficial de atención al cliente"),
            ("support_whatsapp", "18298370908", "Número de WhatsApp oficial para soporte"),
            ("support_hours", "Lunes a Viernes: 8:00 AM - 6:00 PM | Sábados: 9:00 AM - 1:00 PM", "Horario oficial de atención"),
            ("support_email", "soporte@chambard.com", "Correo electrónico de soporte"),
            ("support_whatsapp_message", "Hola CHAMBA RD, necesito asistencia con la plataforma.", "Mensaje inicial sugerido para WhatsApp")
        ]
        for key, val, desc in support_configs:
            cfg = db.query(PlatformConfig).filter(PlatformConfig.key == key).first()
            if not cfg:
                db.add(PlatformConfig(key=key, value=val, description=desc))

        # 4. Protected Seed Initial Administrator
        existing_admin = db.query(User).filter(User.role == "admin").first()
        if existing_admin:
            print(f"Administrador ya existente en el sistema ({existing_admin.email}). Omitiendo creación.")
        else:
            admin_email = (os.getenv("ADMIN_EMAIL") or settings.ADMIN_EMAIL or "admin@chambard.com").strip().lower()
            admin_password = os.getenv("ADMIN_PASSWORD") or settings.ADMIN_PASSWORD
            
            if not admin_password:
                # Fallback password solely for local initial run if unset
                admin_password = "AdminChamba2026!Temporal"
            
            db.add(User(
                email=admin_email,
                password_hash=get_password_hash(admin_password),
                full_name="Administrador Principal CHAMBA RD",
                phone="809-555-0100",
                role="admin",
                province="Distrito Nacional",
                municipality="Santo Domingo",
                description="Cuenta Oficial de Moderación y Administración de Chamba RD",
                is_verified=True,
                verification_status="aprobado",
                must_change_password=True
            ))
            print(f"Primer administrador creado exitosamente ({admin_email}) con contraseña encriptada.")
            
        # 5. Verified Sample Worker
        worker_email = "juan.perez@chambard.com"
        if not db.query(User).filter(User.email == worker_email).first():
            db.add(User(
                email=worker_email,
                password_hash=get_password_hash("Trabajador123!"),
                full_name="Juan Carlos Pérez",
                phone="809-555-0199",
                role="trabajador",
                province="Santo Domingo",
                municipality="Santo Domingo Este",
                description="Técnico profesional en electricidad residencial e industrial, pintura y plomería con 8 años de experiencia certificada.",
                experience_years=8,
                hourly_rate_rd=800,
                is_verified=True,
                verification_status="aprobado",
                is_id_card_verified=True,
                id_card_number="402-2849102-5",
                has_infotep_certificate=True,
                infotep_course_name="Electricidad Residencial e Industrial - INFOTEP",
                rating_average=4.95,
                total_ratings=28,
                completed_jobs=32
            ))
            
        db.commit()
        print("Database seeded successfully with Dominican categories, prices, config, and admin.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
