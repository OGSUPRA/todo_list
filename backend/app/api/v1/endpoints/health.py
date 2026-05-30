from fastapi import APIRouter

router = APIRouter()


@router.get("", summary="Проверка состояния API")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
