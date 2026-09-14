import json

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import config
from ..db import get_db
from ..models import Document, User
from ..schemas import DocMetaOut, DocOut, DocPutIn
from ..security import enforce_doc_rate, get_current_user

router = APIRouter(prefix="/api/docs", tags=["docs"])


@router.get("", response_model=list[DocMetaOut])
def list_docs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.scalars(
        select(Document)
        .where(Document.user_id == user.id)
        .order_by(Document.updated_at.desc())
    ).all()


@router.get("/{doc_id}", response_model=DocOut)
def get_doc(doc_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    doc = db.scalar(select(Document).where(Document.id == doc_id, Document.user_id == user.id))
    if doc is None:
        raise HTTPException(404, "Documento não encontrado")
    return doc


@router.put("/{doc_id}", response_model=DocOut)
def put_doc(
    doc_id: int,
    body: DocPutIn,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    enforce_doc_rate(request)
    doc = db.scalar(select(Document).where(Document.id == doc_id, Document.user_id == user.id))
    if doc is None:
        raise HTTPException(404, "Documento não encontrado")

    if body.base_version is not None and body.base_version != doc.version:
        raise HTTPException(409, "Documento atualizado por outro dispositivo. Recarregue e refaça.")

    raw = json.dumps(body.data, ensure_ascii=False)
    size = len(raw.encode("utf-8"))
    if size > config.DOC_MAX_BYTES:
        raise HTTPException(413, f"Documento excede o limite de {config.DOC_MAX_BYTES // 1_048_576} MiB")

    if body.name is not None and body.name.strip():
        doc.name = body.name.strip()
    doc.data = body.data
    doc.version += 1
    db.commit()
    db.refresh(doc)
    return doc


@router.post("", response_model=DocOut, status_code=201)
def create_doc(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    doc = Document(user_id=user.id, name="Meu plano", data={})
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc