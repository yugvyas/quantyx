# 02 — Choosing the sources

## The original plan, and why it died

The first plan was to scrape [Internshala](https://internshala.com) daily. It is
India-specific, internship-heavy, and its listing pages looked server-rendered.

Before writing a line of scraper, the first thing to check is
`robots.txt`. Internshala's disallows exactly the paths a scraper would need:

```
Disallow: /internship/search/
Disallow: /internship/details/
Disallow: /job/search/
Disallow: /job/details/
Disallow: /*?*          # every query-string URL
```

That is not a grey area. The search and detail pages *are* the product, and they
are disallowed.

RemoteOK's `/api` endpoint was checked as a fallback and returned `403` to an
automated request.

### The practical argument, separate from the compliance one

Even setting compliance aside, a scraper was the wrong instrument for this
project specifically. The entire premise is a repository that is still correct in
six months without anyone tending it. A scraper fighting anti-bot defences does
not survive six months — it degrades quietly, and the failure mode is a dashboard
that keeps publishing while the data underneath it thins out.

So the source question was re-asked: **which sources actively want to be read
programmatically?**

## What replaced it

Four official APIs, all used as their operators intend.

| Source | Auth | What it covers |
| --- | --- | --- |
| [Adzuna India](https://developer.adzuna.com) | Free `app_id` / `app_key` | The broad Indian job market |
| [Greenhouse](https://developers.greenhouse.io/job-board.html) | None | Per-company job boards |
| [Lever](https://api.lever.co) | None | Per-company job boards |
| [Ashby](https://developers.ashbyhq.com/docs/public-job-posting-api) | None | Per-company boards, with structured pay |

The three ATS (applicant tracking system) sources are per-company: you ask
`boards-api.greenhouse.io/v1/boards/<company>/jobs` and get that company's
openings. That means coverage is set by a curated list of companies, which is
what `registry/companies.csv` is.

### Why this is better engineering, not a consolation prize

Scraping one site is one HTML parser. Four APIs is four genuinely different
response shapes normalised into one schema:

- **Ashby** nests compensation inside a `summaryComponents` array mixed with
  equity and bonus entries; only the salary component is comparable.
- **Lever** returns `createdAt` as epoch milliseconds and describes pay intervals
  in prose (`"per-year-salary"`).
- **Greenhouse** returns nothing but the board token as an identifier — the
  company name has to come from the registry — and only returns descriptions if
  you pass `?content=true`, HTML-escaped.
- **Adzuna** paginates, and flags predicted salaries with `salary_is_predicted`.

That normalisation is the actual work, and it is the part that resembles a real
data engineering job.

## Building the company registry

The registry started as guesses and ended as verified fact.

`pipeline/validate_registry.py` pings every board and reports whether it
resolves. The workflow is:

```bash
python -m pipeline.validate_registry --input registry/candidates.csv \
    --prune-to registry/companies.csv --min-jobs 1
```

`candidates.csv` is the discovery log — **843 attempted `(ats, slug)` pairs**,
dead ones included, so the search can be widened later without repeating work.
`companies.csv` is the pruned result: **90 boards, all verified live** (37 Ashby,
43 Greenhouse, 10 Lever; 20 India-headquartered), as of 2026-08-05.

### The trick that mattered

The first sweep assumed one ATS per company and wrote off anything that 404'd.
The second sweep tried **every company against all three vendors** — and found
that **CRED, Zomato (slug `eternal`) and Paytm had all been recorded as dead
purely because they were only ever tried on Greenhouse.** All three are live on
Lever. Paytm alone lists 242 roles.

A single-vendor miss proves nothing.

### Diminishing returns, stated plainly

- First sweep: 83 healthy of 267 attempted (31%)
- Second sweep: 17 healthy of 576 attempted (3%)

Most large Indian employers — Flipkart, Swiggy, Zerodha, Nykaa, Myntra,
BigBasket, Unacademy — do not use these three ATS platforms at all. They run
their own portals or Workday/SuccessFactors. Further registry expansion will keep
yielding a few percent.

**Adzuna does the heavy lifting for India coverage**, contributing roughly 40% of
relevant roles by itself. Before its API keys were added, India-located postings
were 25 of 551 (4.5%); after, 392 of 930 (42%). That single integration mattered
more than the entire registry expansion.

## Being a good citizen

Because these are other people's servers:

- A descriptive `User-Agent` naming the project with a contact URL
  (`pipeline/sources/base.py`)
- Bounded concurrency — at most 5 requests in flight
- Exponential backoff with jitter, honouring `Retry-After` on 429/5xx
- A hard call budget on Adzuna (24/day against a ~1,000/month free tier), so the
  pipeline cannot accidentally burn the quota by paginating unbounded
- Per-source and per-company isolation: one dead board never takes down the run

---

Next: [03 — The pipeline](03-the-pipeline.md).
