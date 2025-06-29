import argparse
import csv
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Tuple, Optional

LOG_FILE = Path("daily_log.json")
DEFAULT_CSV = Path("data/food.csv")

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


def find_food_row(name: str, csv_path: Path = DEFAULT_CSV) -> Optional[Dict[str, str]]:
    """Return the row from the CSV matching the description."""
    if not csv_path.exists():
        return None
    with csv_path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Description', '').lower() == name.lower():
                return row
    return None


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
    """Add a food entry to the daily log."""
    items = load_log()

    csv_path = Path(args.csv) if getattr(args, "csv", None) else DEFAULT_CSV
    row = find_food_row(args.name, csv_path)
    if row:
        if args.calories is None:
            args.calories = float(row.get("Data.Kilocalories", 0) or 0)
        if args.carbs is None:
            args.carbs = float(row.get("Data.Carbohydrate", 0) or 0)
        if args.protein is None:
            args.protein = float(row.get("Data.Protein", 0) or 0)
        if args.fat is None:
            args.fat = float(row.get("Data.Fat.Total Lipid", 0) or 0)
        if not args.micro:
            for k, v in row.items():
                if k.startswith("Data.") and k not in (
                    "Data.Kilocalories",
                    "Data.Carbohydrate",
                    "Data.Protein",
                    "Data.Fat.Total Lipid",
                ) and v:
                    args.micro.append(f"{k}={v}")

    micros = parse_micros(args.micro)
    food = FoodItem(
        name=args.name,
        calories=args.calories or 0,
        carbs=args.carbs or 0,
        protein=args.protein or 0,
        fat=args.fat or 0,
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


def lookup_food(args: argparse.Namespace) -> None:
    row = find_food_row(args.name, Path(args.csv))
    if row is None:
        print(f"No data found for {args.name}")
    else:
        print(json.dumps(row, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Daily calorie tracker")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_p = subparsers.add_parser("add", help="Add a food item")
    add_p.add_argument("--name", required=True)
    add_p.add_argument("--calories", type=float)
    add_p.add_argument("--carbs", type=float)
    add_p.add_argument("--protein", type=float)
    add_p.add_argument("--fat", type=float)
    add_p.add_argument(
        "--micro",
        action="append",
        default=[],
        help="micronutrient in name=value form",
    )
    add_p.add_argument("--csv", help="CSV file to look up nutrient data")
    add_p.set_defaults(func=add_food)

    summary_p = subparsers.add_parser("summary", help="Show daily totals")
    summary_p.set_defaults(func=summary)

    reset_p = subparsers.add_parser("reset", help="Clear the log")
    reset_p.set_defaults(func=reset)

    lookup_p = subparsers.add_parser("lookup", help="Show nutrient data from CSV")
    lookup_p.add_argument("--name", required=True)
    lookup_p.add_argument("--csv", required=True, help="CSV file containing nutrient data")
    lookup_p.set_defaults(func=lookup_food)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
