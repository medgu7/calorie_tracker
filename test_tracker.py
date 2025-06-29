import os
import unittest
import json
from pathlib import Path
from tracker import (
    parse_micros,
    parse_micros_string,
    add_food,
    summary,
    reset,
    load_log,
    get_totals,
    find_food_row,
)

class TestTracker(unittest.TestCase):
    def setUp(self):
        # ensure log file is clear
        reset(None)
        Path("data").mkdir(exist_ok=True)
        self.csv_path = Path("data/food.csv")
        self.csv_path.write_text(
            "Description,Data.Kilocalories,Data.Carbohydrate,Data.Protein,Data.Fat.Total Lipid,Data.Vitamins.Vitamin C\n"
            "Apple,95,25,0.5,0.3,8.4\n"
            "Banana,105,27,1.3,0.4,10\n"
            "Rice,130,28,2.7,0.3,0\n"
        )

    def tearDown(self):
        # clean up log file
        if os.path.exists('daily_log.json'):
            os.remove('daily_log.json')
        if hasattr(self, 'csv_path') and self.csv_path.exists():
            self.csv_path.unlink()

    def test_parse_micros(self):
        result = parse_micros(['vit_c=10', 'iron=2'])
        self.assertEqual(result['vit_c'], 10)
        self.assertEqual(result['iron'], 2)

    def test_parse_micros_string(self):
        result = parse_micros_string('a=1,b=2 c=3')
        self.assertEqual(result, {'a': 1.0, 'b': 2.0, 'c': 3.0})

    def test_add_and_summary(self):
        class Args:
            pass
        args = Args()
        args.name = 'Apple'
        args.calories = 95
        args.carbs = 25
        args.protein = 0.5
        args.fat = 0.3
        args.micro = ['vit_c=8']
        args.csv = None
        add_food(args)

        items = load_log()
        self.assertEqual(len(items), 1)

        # capture summary output
        from io import StringIO
        import sys
        buf = StringIO()
        sys_stdout = sys.stdout
        sys.stdout = buf
        summary(None)
        sys.stdout = sys_stdout
        output = buf.getvalue()
        self.assertIn('Calories: 95', output)
        self.assertIn('vit_c: 8', output)

        totals = get_totals()
        self.assertEqual(totals[0], 95)  # calories

    def test_find_food_row(self):
        row = find_food_row('Apple', Path('data/food.csv'))
        self.assertIsNotNone(row)
        self.assertEqual(row['Description'], 'Apple')

    def test_add_from_csv(self):
        class Args:
            pass
        args = Args()
        args.name = 'Banana'
        args.calories = None
        args.carbs = None
        args.protein = None
        args.fat = None
        args.micro = []
        args.csv = 'data/food.csv'
        add_food(args)
        items = load_log()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].calories, 105)

    def test_add_from_default_csv(self):
        class Args:
            pass

        args = Args()
        args.name = 'Rice'
        args.calories = None
        args.carbs = None
        args.protein = None
        args.fat = None
        args.micro = []
        args.csv = None
        add_food(args)
        items = load_log()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].carbs, 28)

if __name__ == '__main__':
    unittest.main()
