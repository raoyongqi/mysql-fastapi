from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd
import os

app = FastAPI()

# CORS中间件
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 可以根据需要调整
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库连接配置
DATABASE_URL = "mysql+pymysql://root:123456@localhost/excel_db"

# SQLAlchemy引擎和会话
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 数据库会话依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 上传Excel文件并处理
@app.post("/upload_excel/")
async def upload_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        # 确保上传目录存在
        os.makedirs("uploads", exist_ok=True)

        # 保存上传的文件到磁盘
        file_location = f"uploads/{file.filename}"
        with open(file_location, "wb") as f:
            f.write(file.file.read())

        # 读取Excel文件
        df = pd.read_excel(file_location)

        # 删除完全重复的行
        df.drop_duplicates(inplace=True)

        # 格式化浮点数列，保留六位小数
        for col in df.select_dtypes(include=['float']):
            df[col] = df[col].round(6)

        # 动态创建SQLAlchemy模型
        metadata = MetaData()
        table_name = "uploaded_data"

        # 删除已有的表
        with engine.connect() as connection:
            connection.execute(text(f"DROP TABLE IF EXISTS {table_name}"))

        # 动态创建表
        columns = [Column("id", Integer, primary_key=True, autoincrement=True)]
        for col in df.columns:
            if df[col].dtype == 'object':
                dtype = String(255)
            elif df[col].dtype == 'float':
                dtype = Float
            else:
                dtype = Integer
            columns.append(Column(col, dtype))

        table = Table(table_name, metadata, *columns)
        metadata.create_all(engine)

        # 插入数据
        with db.begin():
            for _, row in df.iterrows():
                data = {col: row[col] for col in df.columns}
                db.execute(table.insert().values(**data))

        # 返回文件名作为响应
        return {"filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
