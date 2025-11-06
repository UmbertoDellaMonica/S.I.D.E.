"""
Training Isolation Forest su dataset ATTACK + confronto con dataset CLEAN.
- concatena più CSV d'attacco
- prendi 70% degli attacchi per training
- carica tutto il dataset clean
- pulisci le feature selezionate (dropna)
- standardizza con StandardScaler fit sui dati d’attacco
- allena IsolationForest
- valuta su clean + validation se fornita
- genera grafico dei punteggi (attack vs clean), con soglia
- salva scaler, modello e soglia su disco
"""

import argparse
import logging
import os
import sys
import time
import threading
from typing import List, Tuple

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_recall_curve, auc

# -----------------------
# Configurazione logging
# -----------------------
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# -----------------------
# Spinner per il training
# -----------------------
class Spinner:
    def __init__(self, message="Training in corso..."):
        self.message = message
        self.stop_running = False
        self.thread = threading.Thread(target=self._spin)

    def _spin(self):
        spinner = ["|", "/", "-", "\\"]
        idx = 0
        while not self.stop_running:
            sys.stdout.write(f"\r{self.message} {spinner[idx % len(spinner)]}")
            sys.stdout.flush()
            time.sleep(0.2)
            idx += 1
        sys.stdout.write("\r" + " " * (len(self.message) + 4) + "\r")

    def start(self):
        self.thread.start()

    def stop(self):
        self.stop_running = True
        self.thread.join()


# -----------------------
# Funzioni di supporto
# -----------------------
def load_and_concat_attack_csv(paths: List[str], features: List[str]) -> pd.DataFrame:
    frames = []
    for p in paths:
        logging.info(f"Caricamento attacchi da: {p}")
        if not os.path.exists(p):
            logging.warning(f"File non trovato: {p} - saltato")
            continue
        df = pd.read_csv(p, usecols=lambda c: c in features)
        logging.info(f" {p}: {df.shape[0]} righe")
        frames.append(df)
    if not frames:
        raise FileNotFoundError("Nessun file d'attacco valido fornito.")
    df_all = pd.concat(frames, ignore_index=True)
    logging.info(f"Totale attacchi concatenati: {df_all.shape[0]} righe")
    df_clean = df_all.dropna()
    logging.info(f"Dopo dropna (attacks): {df_clean.shape[0]} righe rimanenti")
    return df_clean


def load_clean_csv(clean_path: str, features: List[str]) -> pd.DataFrame:
    """
    Carica il dataset clean, mantiene solo le feature selezionate,
    converte tutto in numerico, elimina righe non valide.
    """
    if not os.path.exists(clean_path):
        raise FileNotFoundError(f"Clean file non trovato: {clean_path}")

    logging.info(f"Caricamento clean da: {clean_path}")

    # Lettura CSV con controllo dei tipi e gestione righe malformate
    df = pd.read_csv(
        clean_path,
        usecols=lambda c: c in features,
        dtype=str,  # leggi tutto come stringa per evitare warning
        low_memory=False,  # evita warning di grandi CSV
        on_bad_lines="skip",  # salta righe corrotte
    )

    before = df.shape[0]

    # Conversione in numerico, valori non convertibili diventano NaN
    for col in features:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop righe con valori mancanti
    df = df.dropna(subset=features)
    after = df.shape[0]

    logging.info(
        f"Pulizia clean: da {before} a {after} righe dopo dropna e conversione numerica"
    )

    return df


def preprocess_and_scale(X: pd.DataFrame) -> Tuple[StandardScaler, np.ndarray]:
    logging.info("Inizio preprocessing: StandardScaler fit sui dati d'attacco")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    logging.info(f"Shape dati preprocessati: {X_scaled.shape}")
    return scaler, X_scaled


def train_isolation_forest(
    X_train: np.ndarray, contamination: float = 0.05, n_estimators: int = 200
) -> IsolationForest:
    logging.info("Avvio training Isolation Forest")
    spinner = Spinner("Training IsolationForest")
    spinner.start()

    model = IsolationForest(
        n_estimators=n_estimators, contamination=contamination, random_state=42
    )
    model.fit(X_train)

    spinner.stop()
    scores = model.decision_function(X_train)
    logging.info(
        f"Score (train) stats: min={scores.min():.6f}, max={scores.max():.6f}, mean={scores.mean():.6f}"
    )
    return model


def pick_default_threshold_from_train_scores(
    model: IsolationForest, X_train_scaled: np.ndarray, percentile: float = 50.0
) -> float:
    scores = model.decision_function(X_train_scaled)
    thresh = float(np.percentile(scores, percentile))
    logging.info(
        f"Soglia di default: percentile {percentile} dei punteggi di training -> {thresh:.6f}"
    )
    return thresh


def plot_score_distributions(
    scores_attack: np.ndarray,
    scores_clean: np.ndarray,
    threshold: float,
    out_path: str = "score_plot.png",
):
    """
    Disegna istogrammi/violin plot della distribuzione dei punteggi per attack e clean,
    con linea verticale della soglia.
    """
    logging.info("Generazione grafico delle distribuzioni dei punteggi")
    plt.figure(figsize=(10, 6))
    # istogrammi sovrapposti con trasparenza
    plt.hist(
        scores_clean,
        bins=50,
        alpha=0.5,
        label="Clean (legittimo)",
        color="blue",
        density=True,
    )
    plt.hist(
        scores_attack, bins=50, alpha=0.5, label="Attack", color="red", density=True
    )
    # linea soglia
    plt.axvline(
        x=threshold, color="black", linestyle="--", label=f"Soglia = {threshold:.4f}"
    )
    plt.xlabel("Score (decision_function)")
    plt.ylabel("Densità")
    plt.title("Distribuzione dei punteggi: attack vs clean")
    plt.legend(loc="best")
    plt.tight_layout()
    plt.savefig(out_path)
    logging.info(f"Grafico salvato come: {out_path}")
    # opzionale: plt.show() se vuoi visualizzare in realtime
    plt.show()


# -----------------------
# MAIN
# -----------------------
def main():
    parser = argparse.ArgumentParser(
        description="Train IsolationForest su attack + confronto clean"
    )
    parser.add_argument("--attack-files", nargs="+", required=True)
    parser.add_argument(
        "--clean-csv", type=str, required=True, help="CSV con traffico clean"
    )
    parser.add_argument(
        "--features",
        nargs="+",
        default=[
            "pkt_size",
            "ip_ttl",
            "ip_len",
            "ip_proto_num",
            "src_port",
            "dst_port",
            "modbus_function_code",
            "modbus_data_length",
        ],
    )
    parser.add_argument("--contamination", type=float, default=0.02)
    parser.add_argument("--n-estimators", type=int, default=200)
    parser.add_argument(
        "--thresh-percentile",
        type=float,
        default=65.0,
        help="Percentile da usare sui punteggi di training per soglia di default",
    )
    parser.add_argument(
        "--out-model", type=str, default="isoforest_modbus_model.joblib"
    )
    parser.add_argument(
        "--out-scaler", type=str, default="isoforest_modbus_scaler.joblib"
    )
    parser.add_argument(
        "--out-thresh", type=str, default="isoforest_modbus_threshold.txt"
    )
    parser.add_argument("--out-plot", type=str, default="score_distribution.png")
    args = parser.parse_args()

    try:
        # 1) carica attacchi
        df_attacks = load_and_concat_attack_csv(args.attack_files, args.features)
        # fai sampling 70% per training
        n_attacks = len(df_attacks)
        n_train = int(0.7 * n_attacks)
        df_attacks_train = df_attacks.sample(n=n_train, random_state=42)
        df_attacks_rest = df_attacks.drop(df_attacks_train.index)
        logging.info(
            f"Uso {n_train}/{n_attacks} attacchi per training, restante {len(df_attacks_rest)} per analisi"
        )

        # 2) carica clean
        df_clean = load_clean_csv(args.clean_csv, args.features)

        # 3) preprocessing sui dati attack-only per training
        scaler, X_train_scaled = preprocess_and_scale(df_attacks_train)

        # 4) train IsolationForest
        model = train_isolation_forest(
            X_train_scaled,
            contamination=args.contamination,
            n_estimators=args.n_estimators,
        )

        # 5) soglia di default
        chosen_thresh = pick_default_threshold_from_train_scores(
            model, X_train_scaled, percentile=args.thresh_percentile
        )

        # 6) calcolo punteggi sia per attacchi residui che per clean
        #    per attacchi residui (rest), per clean
        X_attacks_rest = df_attacks_rest.values
        X_clean_vals = df_clean.values

        X_att_rest_s = scaler.transform(X_attacks_rest)
        X_clean_s = scaler.transform(X_clean_vals)

        scores_attack_rest = model.decision_function(X_att_rest_s)
        scores_clean = model.decision_function(X_clean_s)

        # 7) grafico distribuzioni
        plot_score_distributions(
            scores_attack_rest, scores_clean, chosen_thresh, out_path=args.out_plot
        )

        # 8) validazione clean generale: percentuale segnate come anomalie
        preds_clean = model.predict(X_clean_s)  # -1 = anomalie, 1 = simili al training
        n_anom = np.sum(preds_clean == -1)
        pct = 100 * n_anom / len(preds_clean) if len(preds_clean) > 0 else 0
        logging.info(
            f"Clean dataset: {len(preds_clean)} campioni, {n_anom} segnalati anomalie ({pct:.2f}%)"
        )

        # 9) salva artefatti
        logging.info(f"Salvataggio modello -> {args.out_model}")
        joblib.dump(model, args.out_model)

        logging.info(f"Salvataggio scaler -> {args.out_scaler}")
        joblib.dump(scaler, args.out_scaler)

        logging.info(f"Salvataggio soglia -> {args.out_thresh}")
        with open(args.out_thresh, "w") as fh:
            fh.write(str(chosen_thresh))

        logging.info("Training + valutazione completati con successo ✅")

    except Exception as exc:
        logging.exception(f"Errore durante l'esecuzione: {exc}")


if __name__ == "__main__":
    main()
