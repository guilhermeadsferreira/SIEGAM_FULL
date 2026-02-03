
from main import download_file


def main():
    task = download_file.delay()
    print(f"Tarefa disparada. ID: {task.id}")

    result = task.get(timeout=60)
    print("Resultado:")
    print(result)


if __name__ == "__main__":
    main()
