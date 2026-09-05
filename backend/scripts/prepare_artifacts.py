from src.anomaly_detection import main as anomalies_main
from src.clustering import main as clustering_main
from src.data_cleaning import main as cleaning_main
from src.train import main as training_main


def main() -> None:
    cleaning_main()
    clustering_main()
    anomalies_main()
    training_main()
    print("Préparation des données et artefacts terminée.")


if __name__ == "__main__":
    main()
