from services.tasks import (
    create_task,
    get_all_tasks,
    mark_task_done,
    delete_task
)

def show_menu():
    print("\n--- TODO LIST ---")
    print("1. Создать задачу")
    print("2. Показать задачи")
    print("3. Отметить выполненной")
    print("4. Удалить задачу")
    print("0. Выход")

def run_cli():
    while True:
        show_menu()
        choice = input("Выбор: ")

        if choice == "1":
            title = input("Название: ")
            description = input("Описание: ")
            create_task(title, description)

        elif choice == "2":
            tasks = get_all_tasks()
            for task in tasks:
                print(f"[{task['id']}] {task['title']} - {task['status']}")

        elif choice == "3":
            task_id = input("ID задачи: ")
            mark_task_done(task_id)

        elif choice == "4":
            task_id = input("ID задачи: ")
            delete_task(task_id)

        elif choice == "0":
            break

        else:
            print("Неверный ввод")
