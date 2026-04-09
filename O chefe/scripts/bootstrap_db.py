from app.db import Base, SessionLocal, engine, ensure_schema
from app.models import ChurchCourse, Member


def main():
    Base.metadata.create_all(bind=engine)
    ensure_schema()
    db = SessionLocal()
    try:
        samples = [
            ("Maria Silva", "+5511999991111", "adult"),
            ("Joao Pereira", "+5511988882222", "youth"),
            ("Ana Souza", "+5511977773333", "senior"),
        ]
        for name, phone, age_group in samples:
            if not db.query(Member).filter(Member.phone == phone).first():
                db.add(Member(name=name, phone=phone, preferred_channel="whatsapp", age_group=age_group))

        if not db.query(ChurchCourse).filter(ChurchCourse.name == "Discipulado Basico").first():
            db.add(
                ChurchCourse(
                    name="Discipulado Basico",
                    description="Fundamentos da fe crista para novos convertidos.",
                    fee_amount=0,
                    is_active=True,
                )
            )

        if not db.query(ChurchCourse).filter(ChurchCourse.name == "Casados para Sempre").first():
            db.add(
                ChurchCourse(
                    name="Casados para Sempre",
                    description="Curso gratuito para fortalecimento do casamento (inscricao obrigatoria).",
                    fee_amount=0,
                    is_active=True,
                )
            )
        db.commit()
        print("Banco inicializado com membros de exemplo.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
