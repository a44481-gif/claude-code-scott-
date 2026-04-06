"""
数据库会话管理
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path
import json
from loguru import logger

DB_PATH = Path(__file__).parent.parent.parent / "data" / "health_food.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        raise


def init_db():
    """初始化数据库表"""
    from .models import Base
    Base.metadata.create_all(bind=engine)
    logger.info(f"数据库初始化完成: {DB_PATH}")


def get_or_create(db: Session, model, defaults=None, **kwargs):
    """通用获取或创建"""
    instance = db.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    params = {**kwargs, **(defaults or {})}
    instance = model(**params)
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance, True


def export_to_json(db: Session, table_name: str, limit: int = 1000):
    """导出表数据为JSON"""
    from sqlalchemy import text
    result = db.execute(text(f"SELECT * FROM {table_name} LIMIT {limit}"))
    columns = result.keys()
    data = [dict(zip(columns, row)) for row in result.fetchall()]
    for item in data:
        for key, value in item.items():
            if hasattr(value, 'value'):
                item[key] = value.value
            elif isinstance(value, str) and len(value) > 100:
                item[key] = value[:100] + "..."
    return data
