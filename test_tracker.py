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

    def tearDown(self):
        # clean up log file
        if os.path.exists('daily_log.json'):
            os.remove('daily_log.json')

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

if __name__ == '__main__':
    unittest.main()
