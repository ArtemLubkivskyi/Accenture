"""Demo 09, Block 5 slide "Is the difference real?".

Mean ± 2 × SE per metric for two runs, then the per-question difference (cloud minus local) with
its own ± 2 × SE. If that range includes zero, the runs have not shown a difference.

    uv run python code_snippets/09_difference_real.py eval_results_local.json eval_results_cloud.json
    uv run python code_snippets/09_difference_real.py --example     # 20 made-up questions

Input files are the practice format: a list of rows with "id" and
"metrics": {metric_name: {"score": float | None, ...}}.
"""

import json
import random
import statistics
import sys


def mean_2se(values: list[float]) -> tuple[float, float]:
    if len(values) < 2:
        return (values[0] if values else float("nan")), float("nan")
    return statistics.mean(values), 2 * statistics.stdev(values) / len(values) ** 0.5


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return {row["id"]: row["metrics"] for row in json.load(f)}


def example() -> tuple[dict, dict]:
    rng = random.Random(1)
    local, cloud = {}, {}
    for i in range(20):
        difficulty = rng.uniform(-0.3, 0.15)
        local[f"q{i:02d}"] = {"Faithfulness": {"score": min(1.0, max(0.0, 0.78 + difficulty + rng.gauss(0, 0.03)))}}
        cloud[f"q{i:02d}"] = {"Faithfulness": {"score": min(1.0, max(0.0, 0.84 + difficulty + rng.gauss(0, 0.03)))}}
    return local, cloud


if "--example" in sys.argv or len(sys.argv) < 3:
    if "--example" not in sys.argv:
        print("No files given, using 20 made-up questions.\n")
    a, b = example()
else:
    a, b = load(sys.argv[1]), load(sys.argv[2])

metrics = sorted({m for row in a.values() for m in row} & {m for row in b.values() for m in row})
print(f"{'metric':<22} {'local':>14} {'cloud':>14} {'paired diff':>16}  n   verdict")
for m in metrics:
    ids = [i for i in a if i in b and a[i].get(m, {}).get("score") is not None
           and b[i].get(m, {}).get("score") is not None]
    la, lb = [a[i][m]["score"] for i in ids], [b[i][m]["score"] for i in ids]
    (ma, ea), (mb, eb) = mean_2se(la), mean_2se(lb)
    md, ed = mean_2se([y - x for x, y in zip(la, lb)])
    verdict = "no clear difference" if md - ed <= 0 <= md + ed else ("cloud higher" if md > 0 else "local higher")
    print(f"{m:<22} {ma:>6.2f} ± {ea:<5.2f} {mb:>6.2f} ± {eb:<5.2f} {md:>+7.2f} ± {ed:<6.2f} {len(ids):>3}   {verdict}")

print("\nA range that includes zero means no clear difference. Comparing per question removes the noise from")
print("some questions simply being harder, so the paired range is usually narrower than the two separate ones.")
print("In a local vs cloud run retrieval is identical, so any gap in the Contextual metrics is judge noise.")
