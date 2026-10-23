# Sherma-JEV

## Setup

```console
python -m pip install -r requirements.txt
```

Set `TYPESAFE_API_KEY` in the environment or in `.env` beside this README.

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

## Configuration

Use `test-config.json` as the configuration template. `-1` means unlimited for
fields that support it.

- `seed`: deterministic random seed; default `0`.
- `repair.n`: n-gram size.
- `repair.ngrams_batch_size`: n-grams processed per batch; positive or `-1`.
- `repair.max_candidate_length`: maximum candidate length; positive or `-1`.
- `repair.num_candidates`: maximum accepted candidates per malformed value;
  default `5`.
- `repair.edit_distance_cap`: maximum Levenshtein distance; default `3`.
- `batching.initial_positive_capacity`: initial positive examples retained;
  positive or `-1`.
- `batching.initial_negative_capacity`: initial negative examples retained;
  positive or `-1`.
- `batching.positive_capacity`: ongoing positive-example capacity; positive or
  `-1`, and not below its initial capacity.
- `batching.negative_capacity`: ongoing negative-example capacity; positive or
  `-1`, and not below its initial capacity.
- `batching.cell_timeout_seconds`: timeout for each malformed value, in seconds.
- `jev.confidence_threshold`: minimum accepted JEV confidence from `0` to `1`;
  default `0.5`.
- `jev.timeout_seconds`: timeout for each JEV request, in seconds; default `15`.
- `limits.max_iterations`: maximum repair-search iterations; positive or `-1`.
- `limits.max_states`: maximum automaton states; positive or `-1`.
- `limits.max_queue_size`: maximum repair-search queue size; positive or `-1`.
- `limits.max_rsr_candidates`: maximum RSR candidates; positive or `-1`.

## Test

```console
python -m unittest discover -s . -p "test_*.py"
python test_suite.py smoke
python test_suite.py test
make smoke
make test
make clean
```

## Generate corrupted datasets

The dataset generator is bundled in `test-case-generator-tool`. From this
directory, generate all configured cases with:

```console
python test-case-generator-tool/benchmark.py generate
```

To add a new dataset:

1. Create `test-case-generator-tool/datasets/<dataset-name>/clean.csv`. The CSV
   must have a header with unique, non-empty column names.
2. Create `test-case-generator-tool/oracles/<dataset-name>/oracles.json`. Its `oracles` array
   must contain one entry per CSV column, in header order. Use an existing
   manifest as a template; each entry defines either an accepted `regex` or an
   `enum` with its accepted `values`.
3. Add `<dataset-name>` to the `DATASETS` tuple near the top of
   `test-case-generator-tool/benchmark.py`.
4. Adjust `test-case-generator-tool/config.json` if needed. `max_rows` controls the sampled
   row count, `corruption_rates` controls the fraction of eligible cells changed,
   and `missing_rate` controls how many changed cells are made empty. The
   remaining changed cells receive random character insertions, deletions, or
   substitutions.
5. Run the generation command above. To generate only one configured corruption
   rate, pass its percentage, for example:

   ```console
   python test-case-generator-tool/benchmark.py generate --rates 50
   ```

Generated cases are written to
`test-case-generator-tool/generated-<rate>/<dataset-name>/`. Each case contains the sampled
`original.csv`, its `corrupted.csv`, and `case.json` describing every changed
cell. The generator uses the configured seed, so identical inputs and settings
produce identical cases.
