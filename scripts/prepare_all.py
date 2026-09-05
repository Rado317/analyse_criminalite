from scripts.init_db import init_database
from scripts.prepare_artifacts import main as prepare_artifacts


def main() -> None:
    prepare_artifacts()
    count = init_database(force=True)
    print(f"Projet entièrement préparé : {count} lignes en base.")


if __name__ == "__main__":
    main()
