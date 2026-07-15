"""
02_errors_and_tests — чиним и тестируем 🛠️

В app.py лежит сломанное FastAPI-приложение. Найдите и исправьте ВСЕ проблемы.

Задача А: Исправить приложение (task.py)
    Скопируйте app.py сюда и исправьте все ошибки.
    Внимание: tests будут проверять ВАШУ реализацию, не оригинальный app.py.

    Чего ждут тесты:
        ✓ POST /items → 201 Created
        ✓ GET  /items/{id} → 200 или 404
        ✓ PUT  /items/{id} → 200 или 404
        ✓ DELETE /items/{id} → 204 или 404
        ✓ GET  /divide?a=10&b=0 → 400 (не 500!)
        ✓ GET  /items/{id}/counter → race condition отсутствует
        ✓ GET  /slow-sync → async def + await asyncio.sleep
        ✓ DELETE возвращает правильный статус (204)

Задача Б: Написать тесты в test_errors.py
    Покрыть все эндпоинты.
"""

import asyncio
import threading
from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

app = FastAPI()

ITEMS: dict[int, dict] = {}
NEXT_ID = 1
COUNTER = 0

_id_lock = threading.Lock()
_counter_lock = threading.Lock()


class ItemCreate(BaseModel):
    name: str


class ItemUpdate(BaseModel):
    name: str = ""


@app.get("/items")
def list_items():
    return {"items": list(ITEMS.values())}


@app.get("/items/{item_id}")
def get_item(item_id: int):
    item = ITEMS.get(item_id)
    if item is None:
        return JSONResponse(status_code=404, content={"detail": "Item not found"})
    return item


@app.post("/items", status_code=201)
def create_item(item: ItemCreate):
    global NEXT_ID
    with _id_lock:
        new_id = NEXT_ID
        NEXT_ID += 1
    obj = {"id": new_id, "name": item.name}
    ITEMS[new_id] = obj
    return {"id": new_id}


@app.get("/items/{item_id}/counter")
def get_counter(item_id: int):
    # counter increments should be atomic
    global COUNTER
    with _counter_lock:
        COUNTER += 1
        value = COUNTER
    return {"counter": value}


@app.put("/items/{item_id}")
def update_item(item_id: int, update: ItemUpdate):
    if item_id not in ITEMS:
        return JSONResponse(status_code=404, content={"detail": "Item not found"})
    ITEMS[item_id]["name"] = update.name
    return ITEMS[item_id]


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    if item_id not in ITEMS:
        return JSONResponse(status_code=404, content={"detail": "Item not found"})
    del ITEMS[item_id]
    return Response(status_code=204)


@app.get("/divide")
def divide(a: int, b: int):
    if b == 0:
        return JSONResponse(status_code=400, content={"detail": "division by zero"})
    return {"result": a / b}


@app.get("/slow-sync")
async def slow_sync():
    await asyncio.sleep(0.5)
    return {"status": "done"}
