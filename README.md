# MovieLens Recommendation System with Collaborative Filtering

An offline movie-discovery prototype: give it one movie you like and receive ten different titles, with an explicit fallback when a title has too little collaborative history.

## Question and decision

Can item-to-item collaborative filtering retrieve a held-out liked movie more effectively than recommending the same globally popular movies? This research benchmark helps a recommendation team decide whether behavioral similarity deserves further prospective evaluation. It is not a deployed product or a claim about actual viewer satisfaction.

## Data and quality

The official **MovieLens 32M** research release contains **32,000,204 ratings**, **200,948 anonymous users**, **87,585 catalog titles**, and **2,000,072 tags**. The notebook verifies all four CSV files against the release's documented counts and MD5 hashes, then scans every rating in one-million-row chunks. No invalid half-star ratings, missing rating fields, or duplicate user–movie pairs were found. All valid ratings are preserved. Surrounding whitespace is normalized in 156 display titles; original values remain unchanged. Ratings of at least four stars define positive preference, yielding **15,938,231 positive interactions**.

The release describes activity through October 12, 2023; the observed maximum Unix timestamp converts to **October 13, 2023 at 02:29:07 UTC**. The notebook records the actual UTC boundary rather than silently changing it to the description's calendar date.

## Method

1. Draw a seeded sample of 20,000 users; 19,950 have at least two positive interactions.
2. Reserve each eligible user's last positive interaction as the target, using the preceding positive as the one-movie input. Remove that target interaction from training.
3. Require at least 25 positive **training** ratings per item. Construct a sparse item–user matrix with **13,280 titles** and **15,740,145 positive training interactions**, using approximately **120.1 MiB** for its CSR arrays rather than a dense matrix.
4. Weight the matrix with TF-IDF, fit a randomized truncated SVD, and compare nested 16-, 32-, and 64-factor representations using validation NDCG@10. Rank neighbors by cosine similarity.
5. Split evaluation users into disjoint validation and final-test groups before model selection. Compare the chosen model with training-only popularity on identical test cases. Report coverage, Wilson intervals, and paired uncertainty as well as rank metrics.

The notebook contains `recommend_movies("Toy Story (1995)")`, ambiguity handling, close-title suggestions, and a genre-and-quality fallback. Both the main and fallback interfaces are checked to return ten unique alternatives without the input title. The fallback is not claimed to have separately validated ranking quality.

## Verified result

Fresh full-data execution on **October 28, 2026** selected **64 factors**. The final test covers **9,769 of 9,975 reserved users (97.93%)**.

| Final-test measure | Popularity | Collaborative |
|---|---:|---:|
| Hit Rate@10, supported pairs | 3.163% | 8.988% |
| NDCG@10 | 0.01554 | 0.04923 |
| MRR@10 | 0.01074 | 0.03690 |
| Hit Rate@10, all reserved users; uncovered pairs count as misses | 3.098% | 8.802% |
| Eligible catalog reached by recommendations | 0.083% | 59.752% |

The paired hit-rate difference is **5.825 percentage points**, with a user-pair bootstrap 95% interval of **5.169–6.480 points**. Full machine-readable evidence is in [validation.json](validation.json); charts, validation comparisons, and the working interface are embedded in [the notebook](movielens_recommender.ipynb).

## Important boundaries

This is **transductive held-interaction evaluation**, not global point-in-time forecasting or unseen-user evaluation. Earlier interactions from evaluation users remain in the common training matrix. Other users' records span the entire historical release. There are **2,093 same-second seed–target pairs**, ordered deterministically by movie ID; these do not establish real chronological sequence. An online or prospective claim requires a global-time backtest and a consent-aware experiment.

The positive threshold and 25-support cutoff are declared assumptions. Conditional metrics exclude unsupported pairs; all-user retrieval is also reported so this exclusion is visible. One observed target cannot identify every relevant recommendation. The data reflect historical MovieLens exposure and self-selected ratings, not all viewers, streaming availability, or causal preference. No demographic fairness or commercial-performance claim is made.

## Reproduce

Use Python **3.12** and the pinned numerical dependencies. Approximately 2 GB of free disk for the extracted source and several GB of free RAM are appropriate; the verified run used a 32-GB machine and limited numerical workers to four. The implementation does not load the 836-MiB ratings CSV into one dense dataframe.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Download the **MovieLens 32M** archive from [GroupLens](https://grouplens.org/datasets/movielens/32m/), extract it, and keep `movies.csv`, `ratings.csv`, `tags.csv`, `links.csv`, `README.txt`, and `checksums.txt` together. Set the source directory, then run:

```bash
export PROJECT_DATA_DIR="/path/to/extracted/ml-32m"
python run.py
```

Alternatively, put the extracted files in an ignored `data/` folder. `run.py` clears saved execution state, starts a fresh Python kernel, executes every cell, saves the notebook, and verifies execution counts and absence of saved errors. It regenerates `validation.json` and ignored `outputs/` charts/example recommendations. No raw data or fitted model is committed. Re-run the notebook before calling its recommendation function; the in-memory trained representation is intentionally not serialized.

## Repository and attribution

Seven release files: this README, the notebook, `run.py`, `requirements.txt`, `.gitignore`, `validation.json`, and `LICENSE.md`. Original source analysis is preserved separately; its SHA-256 is recorded in validation evidence. Source files are never edited by the runner. Cleanup corrected the unrelated original title, replaced working-directory data assumptions, removed machine-specific output paths and raw-record previews, made chart labels follow the selected factor count, bounded parallelism, and clarified the retrospective evaluation design.

MovieLens data and derived examples retain the [GroupLens research/noncommercial conditions](https://files.grouplens.org/datasets/movielens/ml-32m-README.html). No University of Minnesota or GroupLens endorsement is implied. Data are downloaded from the authoritative source, not redistributed here. Commercial or revenue-bearing use requires the permission described in those terms.

Harper, F. M., & Konstan, J. A. (2015). The MovieLens datasets: History and context. *ACM Transactions on Interactive Intelligent Systems, 5*(4), Article 19. [https://doi.org/10.1145/2827872](https://doi.org/10.1145/2827872). Release documentation and usage terms checked October 28, 2026.
