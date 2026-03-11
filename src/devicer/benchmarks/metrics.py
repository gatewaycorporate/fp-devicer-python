from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, TypedDict


class ScoredPair(TypedDict):
    score: float
    sameDevice: bool
    isAttractor: bool


@dataclass(frozen=True)
class BenchmarkResult:
    threshold: int
    precision: float
    recall: float
    f1: float
    far: float
    frr: float
    eer: float
    attr: float


def calculate_metrics(
    scored_pairs: Sequence[ScoredPair], thresholds: Sequence[int] | None = None
) -> List[BenchmarkResult]:
    threshold_values = list(thresholds) if thresholds is not None else [i * 5 for i in range(21)]
    results: List[BenchmarkResult] = []

    for threshold in threshold_values:
        tp = 0
        fp = 0
        tn = 0
        fn = 0

        for pair in scored_pairs:
            predicted_same = pair["score"] >= threshold
            if pair["sameDevice"] and predicted_same:
                tp += 1
            elif (not pair["sameDevice"]) and predicted_same:
                fp += 1
            elif (not pair["sameDevice"]) and (not predicted_same):
                tn += 1
            else:
                fn += 1

        precision = (tp / (tp + fp)) if (tp + fp) else 0.0
        recall = (tp / (tp + fn)) if (tp + fn) else 0.0
        far = (fp / (fp + tn)) if (fp + tn) else 0.0
        frr = (fn / (tp + fn)) if (tp + fn) else 0.0
        eer = abs(far - frr)

        attractor_impostors = [p for p in scored_pairs if (not p["sameDevice"]) and p["isAttractor"] is True]
        if attractor_impostors:
            attr_above = [p for p in attractor_impostors if p["score"] >= threshold]
            attr = len(attr_above) / len(attractor_impostors)
        else:
            attr = 0.0

        denominator = precision + recall
        f1 = (2 * precision * recall / denominator) if denominator else 0.0

        results.append(
            BenchmarkResult(
                threshold=int(threshold),
                precision=precision,
                recall=recall,
                f1=f1,
                far=far,
                frr=frr,
                eer=eer,
                attr=attr,
            )
        )

    return results
