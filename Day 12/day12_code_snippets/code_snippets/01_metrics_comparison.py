"""Demo 01, Block 1 slide "What word-overlap metrics see": BLEU, ROUGE and BERTScore on four answers.

Every metric ranks a wrong answer above the two correct paraphrases. No API calls.
BERTScore downloads roberta-large (about 1.4 GB) on the first run, so run it once before the session:

    uv run python code_snippets/01_metrics_comparison.py
"""

import warnings

import nltk
from bert_score import BERTScorer
from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu
from rouge_score import rouge_scorer
from transformers.utils import logging as hf_logging

warnings.filterwarnings("ignore")
hf_logging.set_verbosity_error()

nltk.download("punkt", quiet=True)

REFERENCE = "The capital of France is Paris."
CANDIDATES = [
    ("correct", "Paris serves as France's capital city."),
    ("correct", "France's most important city is Paris."),
    ("wrong", "London is the capital of France."),
    ("wrong", "The capital of France is London."),
]


def bleu4(reference: str, candidate: str) -> float:
    return sentence_bleu(
        [reference.lower().split()], candidate.lower().split(),
        weights=(0.25, 0.25, 0.25, 0.25), smoothing_function=SmoothingFunction().method1,
    )


rouge = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=False)
print("Loading BERTScore (roberta-large, rescaled)...")
bert = BERTScorer(lang="en", rescale_with_baseline=True)

print(f"\nReference: {REFERENCE}\n")
print(f"{'Answer':<42} {'':<8} {'BLEU-4':>7} {'ROUGE-L':>8} {'BERTScore':>10}")
print("-" * 78)
for verdict, candidate in CANDIDATES:
    b = bleu4(REFERENCE, candidate)
    r = rouge.score(REFERENCE, candidate)["rougeL"].fmeasure
    _, _, f1 = bert.score([candidate], [REFERENCE])
    print(f"{candidate:<42} {verdict:<8} {b:>7.2f} {r:>8.2f} {f1.item():>10.2f}")

print("\nThe wrong answers score at least as high as the correct paraphrases on all three metrics.")
print("They measure how close the words are to the reference, and here the fact is a single word.")
