import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Tuple

LOG_FILE = Path('daily_log.json')

@dataclass
class FoodItem:
    name: str
    calories: float
    carbs: float
    protein: float
    fat: float
    micros: Dict[str, float]


def load_log() -> List[FoodItem]:
    if LOG_FILE.exists():
        data = json.loads(LOG_FILE.read_text())
        return [FoodItem(**item) for item in data]
    return []


def save_log(items: List[FoodItem]) -> None:
    LOG_FILE.write_text(json.dumps([asdict(i) for i in items], indent=2))


def parse_micros(micro_list: List[str]) -> Dict[str, float]:
    micros: Dict[str, float] = {}
    for item in micro_list or []:
        if '=' not in item:
            raise ValueError(f"Invalid micro format: {item}")
        key, value = item.split('=', 1)
        micros[key] = micros.get(key, 0.0) + float(value)
    return micros


def parse_micros_string(micro_str: str) -> Dict[str, float]:
    """Parse micronutrients from a single string separated by commas or spaces."""
    parts = [p.strip() for p in re.split(r'[ ,]+', micro_str or '') if p.strip()]
    return parse_micros(parts)


def get_totals() -> Tuple[float, float, float, float, Dict[str, float]]:
    """Return totals for calories, carbs, protein, fat and micronutrients."""
    items = load_log()
    total_calories = sum(f.calories for f in items)
    total_carbs = sum(f.carbs for f in items)
    total_protein = sum(f.protein for f in items)
    total_fat = sum(f.fat for f in items)

    micro_totals: Dict[str, float] = {}
    for f in items:
        for k, v in f.micros.items():
            micro_totals[k] = micro_totals.get(k, 0.0) + v
    return total_calories, total_carbs, total_protein, total_fat, micro_totals


def add_food(args: argparse.Namespace) -> None:
    items = load_log()
    micros = parse_micros(args.micro)
    food = FoodItem(
        name=args.name,
        calories=args.calories,
        carbs=args.carbs,
        protein=args.protein,
        fat=args.fat,
        micros=micros,
    )
    items.append(food)
    save_log(items)
    print(f"Added {args.name}")


def summary(_: argparse.Namespace) -> None:
    total_calories, total_carbs, total_protein, total_fat, micro_totals = get_totals()

    print(f"Calories: {total_calories}")
    print(f"Carbs: {total_carbs}g")
    print(f"Protein: {total_protein}g")
    print(f"Fat: {total_fat}g")
    if micro_totals:
        print("Micronutrients:")
        for k, v in micro_totals.items():
            print(f"  {k}: {v}")


def reset(_: argparse.Namespace) -> None:
    if LOG_FILE.exists():
        LOG_FILE.unlink()
    print("Log reset")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Daily calorie tracker")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_p = subparsers.add_parser("add", help="Add a food item")
    add_p.add_argument("--name", required=True)
    add_p.add_argument("--calories", type=float, required=True)
    add_p.add_argument("--carbs", type=float, required=True)
    add_p.add_argument("--protein", type=float, required=True)
    add_p.add_argument("--fat", type=float, required=True)
    add_p.add_argument("--micro", action="append", default=[], help="micronutrient in name=value form")
    add_p.set_defaults(func=add_food)

    summary_p = subparsers.add_parser("summary", help="Show daily totals")
    summary_p.set_defaults(func=summary)

    reset_p = subparsers.add_parser("reset", help="Clear the log")
    reset_p.set_defaults(func=reset)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
