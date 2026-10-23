# Sherma-JEV

Sherma learns one string grammar per column, generates multiple minimum-edit
repair candidates for each malformed cell, and validates them with external
oracles. It streams accepted candidates to a long-form temporary CSV, then uses
one JEV request per affected row to select a coherent final combination.

Sherma requires Python 3.11 or newer and has no third-party dependencies. From
this standalone directory, remote setup is still available through the
standard requirements workflow:

```console
python -m pip install -r requirements.txt
```

## Run

```console
python algorithm/sherma.py \
  --input corrupted.csv \
  --ground-truth original.csv \
  --schema schema.json \
  --config algorithm-config.json \
  --oracles-dir compiled-oracles \
  --output output.csv \
  --telemetry telemetry.json
```

`--output` is optional and defaults to `output.csv`. The candidate artifact
uses the same base name with `.tmp.csv` as its ending: `output.csv` therefore
writes `output.tmp.csv`. It is truncated when the run starts, receives its
header immediately, and is flushed after each distinct malformed value. Existing
candidate, final-output, telemetry, and stale error-log files are overwritten.
The requested `output.csv` is atomically published only after every JEV request
succeeds.

The candidate CSV columns are `row,column,malformed_value,candidate_rank,candidate`.
Rows are zero-based and ranks are one-based. Valid and originally missing cells
are omitted. A malformed cell with no accepted candidate receives one row with
blank rank and candidate fields. Repeated occurrences of the same malformed
value in a column share candidate generation but each cell receives its own rows.

The schema is a version-1 JSON object containing a non-empty description for
every CSV column. Set `TYPESAFE_API_KEY` in the environment or in `.env` beside
this README. For every affected row, JEV receives the fixed valid values and one
choice question for each cell with candidates. Missing cells, and malformed
cells without generated candidates, use observed oracle-valid column values
ordered by frequency and then lexically, capped by `num_candidates`. If a
column has no observed valid value, that cell remains empty. A fatal failure
preserves the candidate CSV, removes final output and telemetry, and writes a
UTC-timestamped traceback to `error.log` beside the requested output.

The ground-truth CSV is used only to record exact-correct cell counts before and
after repair. Ground-truth missing values are excluded. The file must have the
same header and row count as the input CSV.

The oracle directory contains `oracle_000`, `oracle_001`, and so on in CSV
column order (`.exe` is appended on Windows). Each process reads a JSON string
array from stdin and writes a non-empty JSON boolean prefix to stdout. A short
prefix is valid only when its final value is `true`.

## Configuration

```json
{
  "seed": 0,
  "repair": {
    "n": 4,
    "ngrams_batch_size": 5,
    "max_candidate_length": -1,
    "num_candidates": 5,
    "edit_distance_cap": 3
  },
  "batching": {
    "initial_positive_capacity": -1,
    "initial_negative_capacity": -1,
    "positive_capacity": -1,
    "negative_capacity": -1,
    "cell_timeout_seconds": 120
  },
  "jev": {
    "confidence_threshold": 0.5,
    "timeout_seconds": 15
  },
  "limits": {
    "max_iterations": -1,
    "max_states": -1,
    "max_queue_size": -1,
    "max_rsr_candidates": -1
  }
}
```

The string grammar is learned incrementally with RPNI2. Up to `num_candidates`
distinct accepted candidates are collected per distinct malformed value. A
candidate's unit-cost Levenshtein distance is checked before the oracle; search
stops when it exceeds `edit_distance_cap`. Accepted candidates become positive
examples only after collection finishes, while rejected values become negative
examples during search. The per-value timeout is `cell_timeout_seconds`; on
timeout, candidates found so far remain in the output and processing continues.
JEV calls run sequentially in row order. Responses below
`jev.confidence_threshold` fall back to the first candidate for that cell. A
JEV timeout, request failure, incomplete or malformed response, unexpected
model, or missing API key fails the entire run.
The initial DFA uses deterministically shuffled positive and negative examples
from the complete column scan: it starts from the coarsest quotient of the positive
PTA and applies initial negatives through RPNI2 acceptance-prefix splitting. All four
capacities default to `-1` (unlimited);
ongoing capacities must be at least their initial counterparts. When a retained
example is evicted FIFO, its existing DFA effect remains. All positive examples
remain in the n-gram model.

Empty strings and `?` are missing inputs. They are filled from observed valid
column values when possible. Cell values must be ASCII because the grammar
operates on byte symbols.

## Test

```console
python -m unittest discover -s . -p "test_*.py"
```

Run the bundled smoke case or all bundled 50% and 90% corruption cases:

```console
python test_suite.py smoke
python test_suite.py test
```

The same suites can be run through Make. The Makefile detects `python3` first,
then falls back to `python`; override it with `make smoke PYTHON=/path/to/python`
when needed.

```console
make smoke
make test
make clean
```

Both modes call the hosted JEV API for every affected row. They require a valid
`TYPESAFE_API_KEY`, consume API requests, and fail on any JEV request error.

Each run keeps its final and candidate CSVs, telemetry, benchmarks, and progress logs in
`test-results/smoke` or `test-results/test`. The local `test-config.json`
matches GammaMax-DT's unlimited search limits. A timer reports elapsed seconds
and completed cases throughout both suites. Cases run concurrently using the
available CPU count, capped by the number of cases.
