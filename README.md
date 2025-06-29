# Calorie Tracker

This project contains a simple command-line application to record daily food intake and report macro and micronutrient totals.

You can use it either from the command line or through a small built-in web interface.

## Usage

Add foods you eat with macro and micronutrients:

```bash
python tracker.py add --name "Apple" --calories 95 --carbs 25 --protein 0.5 --fat 0.3 \
  --micro vitamin_c=8.4 --micro iron=0.1
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
