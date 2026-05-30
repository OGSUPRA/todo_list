from __future__ import annotations

from fastapi.testclient import TestClient


def test_task_crud_archive_restore_and_filters(client: TestClient, auth_headers: dict[str, str]) -> None:
    create_response = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={"title": "Собрать API", "description": "Проверить все маршруты"},
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    list_response = client.get("/api/v1/tasks", headers=auth_headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    update_response = client.patch(
        f"/api/v1/tasks/{task_id}",
        headers=auth_headers,
        json={"title": "Собрать production API", "description": "Обновить сервисы"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Собрать production API"

    toggle_response = client.post(f"/api/v1/tasks/{task_id}/toggle", headers=auth_headers)
    assert toggle_response.status_code == 200
    assert toggle_response.json()["status"] == "done"

    search_response = client.get("/api/v1/tasks", headers=auth_headers, params={"search": "production"})
    assert search_response.status_code == 200
    assert len(search_response.json()) == 1

    archive_response = client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert archive_response.status_code == 200

    active_tasks_response = client.get("/api/v1/tasks", headers=auth_headers)
    assert active_tasks_response.status_code == 200
    assert active_tasks_response.json() == []

    deleted_tasks_response = client.get(
        "/api/v1/tasks",
        headers=auth_headers,
        params={"include_deleted": True},
    )
    assert deleted_tasks_response.status_code == 200
    assert deleted_tasks_response.json()[0]["is_deleted"] is True

    restore_response = client.post(f"/api/v1/tasks/{task_id}/restore", headers=auth_headers)
    assert restore_response.status_code == 200
    assert restore_response.json()["is_deleted"] is False


def test_mark_all_done_updates_all_open_tasks(client: TestClient, auth_headers: dict[str, str]) -> None:
    for index in range(2):
        client.post(
            "/api/v1/tasks",
            headers=auth_headers,
            json={"title": f"Task {index}", "description": ""},
        )

    response = client.post("/api/v1/tasks/mark-all-done", headers=auth_headers)
    assert response.status_code == 200

    tasks_response = client.get("/api/v1/tasks", headers=auth_headers)
    assert all(task["status"] == "done" for task in tasks_response.json())
