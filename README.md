# api-coders


---

## Models (full definitions)

> All timestamps stored in UTC, ISO-8601 strings in API responses.

### `contests.models.Contest`
- `id` — AutoField (pk)
- `title` — CharField(max_length=200) — **required**
- `slug` — SlugField(max_length=220, unique=True)
- `description` — TextField(blank=True, null=True)
- `location` — CharField(max_length=100)
- `start_date` — DateTimeField() — **required**
- `end_date` — DateTimeField() — **required**
- `visibility` — CharField(choices=('public','private'), default='public')
- `finalized` — BooleanField(default=False)  # whether ratings processed
- `problems_count` — IntegerField(default=0)
- `created_at` — DateTimeField(auto_now_add=True)
- `updated_at` — DateTimeField(auto_now=True)
- Meta: `ordering = ['-start_date']`
- Constraints:
  - `end_date > start_date`
  - unique together optional: (`title`,`start_date`,`location`) (recommended)

**Delete rule:** cannot delete if any `submissions` exist → HTTP 400.

---

### `coders.models.Coder`
- `id` — AutoField (pk)
- `nickname` — CharField(max_length=50, unique=True) — **required**
- `display_name` — CharField(max_length=120, blank=True)
- `country` — CharField(max_length=50)
- `bio` — TextField(blank=True, null=True)
- `rating` — IntegerField(default=1500)  # ELO-like initial rating
- `points_total` — IntegerField(default=0)
- `total_submissions` — IntegerField(default=0)
- `accepted_submissions` — IntegerField(default=0)
- `created_at` — DateTimeField(auto_now_add=True)
- `updated_at` — DateTimeField(auto_now=True)

**Delete rule:** cannot delete if coder has submissions → HTTP 400 with message.

---

### `problems.models.Problem`
- `id` — AutoField
- `contest` — ForeignKey(Contest, on_delete=CASCADE, related_name='problems')
- `title` — CharField(max_length=200)
- `code` — CharField(max_length=20)  # problem code within contest, e.g., "A","B"
- `max_score` — IntegerField(default=100)
- `time_limit_ms` — IntegerField(default=1000)
- `memory_limit_kb` — IntegerField(default=65536)
- `created_at` — DateTimeField(auto_now_add=True)
- Meta: `unique_together = ('contest','code')`

**Delete rule:** cannot delete if problem has submissions → HTTP 400.

---

### `submissions.models.Submission`
- `id` — AutoField
- `contest` — ForeignKey(Contest, on_delete=PROTECT, related_name='submissions')
- `problem` — ForeignKey(Problem, on_delete=PROTECT, related_name='submissions')
- `coder` — ForeignKey(Coder, on_delete=PROTECT, related_name='submissions')
- `language` — CharField(max_length=50)  # "python", "cpp", ...
- `code` — TextField()
- `status` — CharField(choices=('pending','accepted','wrong_answer','runtime_error','time_limit','compilation_error','partial'), default='pending')
- `score` — IntegerField(default=0)  # 0..problem.max_score
- `attempt_no` — IntegerField(default=1)  # incremented per coder-problem
- `submitted_at` — DateTimeField(auto_now_add=True)
- `judged_at` — DateTimeField(null=True, blank=True)
- Meta: `ordering = ['-submitted_at']`

**Behavior:** When judged, update `status`, `score`, `judged_at` and recalc coder counters.

---

### `leaderboard.models.RatingChange`
- `id` — AutoField
- `coder` — ForeignKey(Coder, on_delete=CASCADE, related_name='rating_changes')
- `contest` — ForeignKey(Contest, on_delete=CASCADE, related_name='rating_changes')
- `old_rating` — IntegerField()
- `new_rating` — IntegerField()
- `delta` — IntegerField()
- `reason` — CharField(max_length=255)  # e.g., "contest_finish"
- `created_at` — DateTimeField(auto_now_add=True)

**Index:** index on (`coder`, `created_at`).

---

## Business rules (detailed)

1. **Open API** — All endpoints are public by default for the test. (In production, apply Auth.)
2. **Submission scoring**
   - `score` must be integer: `0 <= score <= problem.max_score`.
   - `accepted` if `status == 'accepted'` or `score == problem.max_score`.
   - `attempt_no` increments: new submission attempt for same coder+problem gets previous max `attempt_no` + 1.
3. **Contest finalize**
   - A special endpoint `POST /api/contests/{id}/finalize/` triggers rating recalculation and sets `finalized=True`.
   - Finalize allowed if `end_date <= now` or `force=true`.
4. **Rating calculation (ELO-like, simplified)**
   - For contest with N participants:
     - `max_points = sum(problem.max_score for problem in contest.problems)`
     - For coder `i`: `P_i = sum(best score per problem)`; normalized `S_i = P_i / max_points` (0..1).
     - For each opponent `j`: expected `E_ij = 1 / (1 + 10 ** ((R_j - R_i)/400))`
     - `E_i_total = sum_j E_ij`
     - `S_i_total = S_i * (N-1)`
     - `K = 40 if coder.total_submissions < 30 else 20`
     - `delta_i = round(K * (S_i_total - E_i_total))`
     - `new_rating = R_i + delta_i`
   - Edge cases:
     - If `N < 2` → no rating changes.
     - Clamp delta to reasonable bounds, e.g., `abs(delta_i) <= 400`.
   - Save `RatingChange` entries and update `Coder.rating`.
5. **Leaderboard rules**
   - **Contest leaderboard** groups by coder:
     - `points`: sum of best scores per problem
     - `accepted_count`: number of problems fully accepted
     - `attempts`: total attempts across problems
     - Sort by `points desc`, tie-breaker: `accepted_count desc`, then `first_accepted_time asc`.
   - **Global leaderboard**: all coders sorted by `rating desc`.
6. **Deletion constraints**
   - `Contest`, `Problem`, `Coder` cannot be deleted if they have related `Submission` records.
   - `Submission` deletions are allowed; deletion should recalc coder stats and any derived leaderboards.
7. **Consistency & Transactions**
   - Use DB transactions (atomic) for operations that modify multiple counters (e.g., judge update, finalize).
8. **Search & Filters**
   - Coders: `?country=Uzbekistan&min_rating=1600&search=master&ordering=-rating`
   - Contests: `?search=sprint&location=Tashkent&date_from=2026-01-01&date_to=2026-01-31`
   - Submissions: `?contest=12&coder=3&status=accepted&problem_code=A`
9. **Pagination**
   - All list endpoints: `page` and `page_size`. Default `page_size=20`, max `100`.
10. **Indexing**
    - Add DB indices on `coders.rating`, `submissions.submitted_at`, `contests.start_date`.

---

## API Endpoints (full list, base: `/api/`)

> For all POST/PATCH endpoints: `Content-Type: application/json`. Responses use HTTP standard codes.

### Contests
- `POST /api/contests/` — Create contest.
- `GET /api/contests/` — List contests. Filters: `search`, `location`, `date_from`, `date_to`, `visibility`. Ordering: `-start_date`, `start_date`.
- `GET /api/contests/{id}/` — Retrieve contest detail (includes problems summary).
- `PATCH /api/contests/{id}/` — Partial update (allowed fields: `description`, `end_date`, `location`, `visibility`).
- `DELETE /api/contests/{id}/` — Delete (blocked if submissions exist).
- `POST /api/contests/{id}/finalize/` — Finalize contest & compute ratings. Body optional: `{"force": true}`.

### Coders
- `POST /api/coders/` — Create coder.
- `GET /api/coders/` — List coders. Filters: `country`, `min_rating`, `search`. Ordering: `-rating`, `-points_total`.
- `GET /api/coders/{id}/` — Retrieve coder profile (with recent submissions and rating_changes).
- `PATCH /api/coders/{id}/` — Update profile (display_name, country, bio).
- `DELETE /api/coders/{id}/` — Delete coder (blocked if submissions exist).

### Problems (nested under contest)
- `POST /api/contests/{contest_id}/problems/` — Create problem for contest.
- `GET /api/contests/{contest_id}/problems/` — List problems for contest.
- `GET /api/problems/{id}/` — Retrieve problem.
- `PATCH /api/problems/{id}/` — Update problem.
- `DELETE /api/problems/{id}/` — Delete problem (blocked if submissions exist).

### Submissions
- `POST /api/submissions/` — Create submission (status defaults to `pending`). Request contains `contest`, `problem`, `coder`, `language`, `code`.
- `GET /api/submissions/` — List submissions. Filters: `contest`, `coder`, `status`, `problem_code`. Ordering: `-submitted_at`.
- `GET /api/submissions/{id}/` — Retrieve single submission.
- `PATCH /api/submissions/{id}/judge/` — (internal) Judge update: `{"status":"accepted", "score":100, "judged_at":"ISO8601"}`. On judge update, coder counters and leaderboards recalculated.
- `DELETE /api/submissions/{id}/` — Delete submission (allowed; triggers recalculation).

### Leaderboard & Analytics
- `GET /api/leaderboard/?contest_id={id}` — Contest leaderboard (required param).
- `GET /api/leaderboard/top/?contest_id={id}&limit={n}` — Top N for contest; default limit=10, max=50.
- `GET /api/leaderboard/global/?country={country}&limit={n}` — Global rating leaderboard.
- `GET /api/analytics/contests/{id}/summary/` — Contest analytics: submission counts, acceptance rate, avg score per problem, difficulty histogram.

---

## Example Requests & Responses (JSON)

### 1) Create Contest
**Request**
