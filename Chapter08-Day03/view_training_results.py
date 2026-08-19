"""Print saved CPU LoRA training results in a readable format."""
import argparse
import json
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="View CPU LoRA training metrics")
    parser.add_argument("--results-file", type=Path, default=Path("outputs/training_results.json"))
    parser.add_argument("--json", action="store_true", help="Print the original JSON instead of a summary")
    args = parser.parse_args()
    results_file = args.results_file if args.results_file.is_absolute() else project_root / args.results_file
    if not results_file.is_file():
        raise FileNotFoundError(f"Results file was not found: {results_file}")
    result = json.loads(results_file.read_text(encoding="utf-8"))
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    print(f"Status: {result['status']} | Device: {result['device']}")
    print(f"Model: {result['model_id']}")
    print(f"Completed (UTC): {result['completed_at_utc']}")
    print(f"Training examples: {result['training_examples']}")
    print(
        "Trainable parameters: "
        f"{result['trainable_parameters']:,} / {result['total_parameters']:,} "
        f"({result['trainable_parameter_ratio_percent']}%)"
    )
    print("\nEpoch metrics")
    for metric in result['epoch_metrics']:
        print(f"  epoch {metric['epoch']}: mean_loss={metric['mean_loss']:.6f}")


if __name__ == "__main__":
    main()
