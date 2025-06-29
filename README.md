# Calorie Tracker

This project contains a simple command-line application to record daily food intake and report macro and micronutrient totals.

You can use it either from the command line or through a small built-in web interface.

## Usage

Add foods you eat with macro and micronutrients:

```bash
python tracker.py add --name "Apple" --calories 95 --carbs 25 --protein 0.5 --fat 0.3 \
  --micro vitamin_c=8.4 --micro iron=0.1
```

You can also look up nutrient values from a CSV database using the
`--csv` option. If macros are omitted when adding a food, they will be
filled from the CSV file:

```bash
python tracker.py add --name "Apple" --csv /path/to/food.csv
```

To inspect the values stored in the CSV for a food without adding it to
the log, use the `lookup` command:

```bash
python tracker.py lookup --name "Apple" --csv /path/to/food.csv
```

Print a summary of today's totals:

```bash
python tracker.py summary
```

Reset the log for a new day:

```bash
python tracker.py reset
```

### Web Interface

To launch the web UI run:

```bash
python webapp.py
```

Then open `http://localhost:8000` in your browser to add foods and view the daily summary.

## Tests

Run the tests with:

```bash
python -m unittest
```
