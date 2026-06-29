# Company Research — Search-Only (100 companies)

A search-only company-research benchmark over **100 companies**, each researched with
**one search endpoint per engine, no chaining and no extract** — the fair
single-primitive comparison.

**Endpoints (one call type per engine, search-only):**
| Engine | Endpoint |
|---|---|
| **Linkup** | `/v1/search` (sourcedAnswer, standard depth) |
| **Exa** | `/search` with `highlights` (excerpts, not full-page contents) |
| **Perplexity** | Search API |
| **Parallel** | Search API |

Every engine returns search-result snippets — like-for-like, no engine gets a free
extract step (Exa is run with **highlights** rather than full-page `contents` so the
comparison stays even). Each company is researched across **5 sections** (offering,
pain → solution, case studies, customers, CTAs); a shared synthesizer structures each
engine's results and an LLM judge scores relevance against the verified company
identity.

## Result (n = 100 companies × 5 sections)

| Engine | On-target sources | Answers what was asked | Right company found | Information repeated | Worst-case consistency (P10) |
|---|---|---|---|---|---|
| **Linkup** | **80.7%** | **76.8%** | **83%** | 5% | **★ 57.7** |
| Exa | 76.8% | 73.0% | 80% | 10% | 56.0 |
| Perplexity | 73.4% | 68.5% | 76% | 3% | 53.7 |
| Parallel | 71.0% | 66.1% | 73% | 12% | 39.7 |

Linkup leads every relevance and identification dimension — most on-target sources,
most often answering the actual question, most often the right company, and the
steadiest worst-case. Exa is the consistent runner-up; Parallel is weakest on
worst-case consistency.

**Column meanings**
- **On-target sources** — share of retrieved signals actually pointing at the **target company** (entity relevance / purity).
- **Answers what was asked** — share of signals that **address the section's question** (topical relevance).
- **Right company found** — % of sections where the engine identified the **correct entity**, not a namesake.
- **Information repeated** — % of returned items that were duplicates (lower = less padding).
- **Worst-case consistency (P10)** — relevance composite at the engine's **worst 10%** of companies (higher = degrades less).

Relevance composite = mean over the 5 sections of `(entity_relevance + topical_relevance)/2`.

## Data
- [`results/scorecard.json`](results/scorecard.json) — aggregate scorecard over the 100 companies.
