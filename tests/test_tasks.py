from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_create_task():
    response = client.post(
        "/tasks",
        json={
            "title": "Test task",
            "description": "Testing pytest",
            "priority": "high",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Test task"
    assert data["description"] == "Testing pytest"
    assert data["priority"] == "high"
    assert data["status"] == "todo"


def test_get_tasks():
    response = client.get("/tasks")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)


def test_get_missing_task():
    response = client.get("/tasks/9999999")

    assert response.status_code == 404

    data = response.json()
    assert data["detail"] == "Task not found"


def test_update_task():
    response = client.post(
        "/tasks",
        json={
            "title": "Task to update",
            "description": "Will be changed",
            "priority": "low",
        },
    )

    task_id = response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={
            "status": "done",
            "priority": "high",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "done"
    assert data["priority"] == "high"
    assert data["title"] == "Task to update"


def test_delete_task():
    response = client.post(
        "/tasks",
        json={
            "title": "Task to delete",
            "description": "Will be changed",
            "status": "todo",
            "priority": "low",
        },
    )

    task_id = response.json()["id"]

    response = client.delete(f"/tasks/{task_id}")

    assert response.status_code == 204

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 404

    data = response.json()
    assert data["detail"] == "Task not found"


def test_create_task_invalid_title():
    response = client.post(
        "/tasks",
        json={
            "title": "",
            "description": "Invalid task",
            "priority": "high"
        },
    )

    assert response.status_code == 422


def test_filtering_task():
    response = client.post(
        "/tasks",
        json={
            "title": "Test task",
            "description": "Testing pytest",
            "priority": "high",
            "status": "todo",
        },
    )

    response = client.post(
        "/tasks",
        json={
            "title": "Test task1",
            "description": "Testing pytest1",
            "priority": "high",
            "status": "done",
        },
    )

    response = client.post(
        "/tasks",
        json={
            "title": "Test task2",
            "description": "Testing pytest2",
            "priority": "high",
            "status": "done",
        },
    )


    response = client.get("/tasks?status=done")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert all(task["status"] == "done" for task in data)


    response = client.get("/tasks?priority=high")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert all(task["priority"] == "high" for task in data) 


def test_pagination_task():
    for i in range(4):
        response = client.post(
            "/tasks",
            json={
                "title": f"Pagination task {i}",
                "description": f"Pagination test {i}",
                "status": "in_progress",
                "priority": "low",
            },
        )

        assert response.status_code == 201

    response = client.get("/tasks?page=1&limit=2")

    assert response.status_code == 200

    page_one = response.json()

    assert isinstance(page_one, list)
    assert len(page_one) == 2

    response = client.get("/tasks?page=2&limit=2")

    assert response.status_code == 200

    page_two = response.json()

    assert isinstance(page_two, list)
    assert len(page_two) == 2

    page_one_ids = {task["id"] for task in page_one}
    page_two_ids = {task["id"] for task in page_two}

    assert page_one_ids.isdisjoint(page_two_ids)