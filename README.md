# 🧠 API Coders — Advanced Programming Contest Backend (Django REST)

Ushbu loyiha real kompaniyalar beradigan “advanced backend test-vazifa” asosida yaratilgan.  
Tizim onlayn dasturlash olimpiadalari uchun **contest**, **coder**, **problem**, **submission**,  
va **leaderboard/rating** boshqaruvini ta’minlaydi.

API to‘liq **open API** tarzida ishlaydi (test uchun).  
Barcha ma’lumotlar **JSON** formatida qaytariladi.

---

## 📦 Apps Strukturası
```
contests/       — Contest management
coders/         — Coder profiles & stats
problems/       — Problems inside contests
submissions/    — Code submissions & judging
leaderboard/    — Rating change & leaderboards
```

---

# 🧩 Models (xulosa)

# 🧩 Models (to‘liq aniqlangan)


---

## 🧩 Models

### contests.models.Contest
| Field           | Type               | Notes |
|-----------------|------------------|-------|
| id              | AutoField (PK)     |       |
| title           | CharField(200)    | required |
| slug            | SlugField(220)    | unique |
| description     | TextField         | null=True, blank=True |
| location        | CharField(100)    |       |
| start_date      | DateTimeField     | required |
| end_date        | DateTimeField     | required, must be > start_date |
| visibility      | CharField         | choices=['public','private'], default='public' |
| finalized       | BooleanField      | default=False |
| problems_count  | IntegerField      | default=0 |
| created_at      | DateTimeField     | auto_now_add=True |
| updated_at      | DateTimeField     | auto_now=True |

**Meta:** `ordering = ['-start_date']`  
**Delete rule:** ❌ Cannot delete if submissions exist  

---

### coders.models.Coder
| Field                   | Type         | Notes |
|-------------------------|-------------|-------|
| id                      | AutoField   | PK |
| nickname                | CharField(50) | unique |
| display_name            | CharField(120) | blank=True |
| country                 | CharField(50)  |       |
| bio                     | TextField   | blank=True, null=True |
| rating                  | IntegerField | default=1500 |
| points_total            | IntegerField | default=0 |
| total_submissions       | IntegerField | default=0 |
| accepted_submissions    | IntegerField | default=0 |
| created_at              | DateTimeField | auto_now_add=True |
| updated_at              | DateTimeField | auto_now=True |

**Delete rule:** ❌ Cannot delete if coder has submissions

---

### problems.models.Problem
| Field           | Type          | Notes |
|-----------------|---------------|-------|
| id              | AutoField     |       |
| contest         | FK → Contest  | CASCADE |
| title           | CharField(200)|       |
| code            | CharField(20) | unique per contest (A, B, C…) |
| max_score       | IntegerField  | default=100 |
| time_limit_ms   | IntegerField  | default=1000 |
| memory_limit_kb | IntegerField  | default=65536 |
| created_at      | DateTimeField | auto_now_add=True |

**Meta:** `unique_together = (contest, code)`  
**Delete rule:** ❌ Cannot delete if submissions exist  

---

### submissions.models.Submission
| Field         | Type       | Notes |
|---------------|-----------|-------|
| id            | AutoField |       |
| contest       | FK → Contest | PROTECT |
| problem       | FK → Problem | PROTECT |
| coder         | FK → Coder | PROTECT |
| language      | CharField(50) |       |
| code          | TextField |       |
| status        | CharField | choices=['pending','accepted','wrong_answer','runtime_error','time_limit','compilation_error','partial'], default='pending' |
| score         | IntegerField | default=0 |
| attempt_no    | IntegerField | default=1 |
| submitted_at  | DateTimeField | auto_now_add=True |
| judged_at     | DateTimeField | null=True, blank=True |

**Meta:** `ordering = ['-submitted_at']`

---

### leaderboard.models.RatingChange
| Field      | Type       | Notes |
|------------|-----------|-------|
| id         | AutoField |       |
| coder      | FK → Coder | CASCADE |
| contest    | FK → Contest | CASCADE |
| old_rating | IntegerField |       |
| new_rating | IntegerField |       |
| delta      | IntegerField |       |
| reason     | CharField(255) |       |
| created_at | DateTimeField | auto_now_add=True |

**Index:** `(coder, created_at)`

---

## 🌐 Full API Endpoints (base: `/api/`)

Barcha endpointlar **JSON** formatida ishlaydi.  
Har bir endpoint uchun:
- `Request` (curl yoki HTTP)
- `Success response`
- `Possible error responses`

---

### 🏆 Contests
- `POST /api/contests/` — Create contest  
- `GET /api/contests/` — List contests (filter/pagination)  
- `GET /api/contests/{id}/` — Retrieve contest  
- `PATCH /api/contests/{id}/` — Update contest  
- `DELETE /api/contests/{id}/` — Delete contest (blocked if submissions exist)  
- `POST /api/contests/{id}/finalize/` — Finalize contest, compute ratings  

### 👤 Coders
- `POST /api/coders/` — Create coder  
- `GET /api/coders/` — List coders (filter/order/pagination)  
- `GET /api/coders/{id}/` — Retrieve coder (with recent submissions & rating history)  
- `PATCH /api/coders/{id}/` — Update coder  
- `DELETE /api/coders/{id}/` — Delete coder (blocked if submissions exist)  

### 📝 Problems
- `POST /api/contests/{contest_id}/problems/` — Create problem  
- `GET /api/contests/{contest_id}/problems/` — List problems  
- `DELETE /api/problems/{id}/` — Delete problem (blocked if submissions exist)  

### 📨 Submissions
- `POST /api/submissions/` — Create submission  
- `GET /api/submissions/` — List submissions (filters)  
- `GET /api/submissions/{id}/` — Retrieve submission  
- `PATCH /api/submissions/{id}/judge/` — Judge update (internal)  
- `DELETE /api/submissions/{id}/` — Delete submission  

### 📊 Leaderboards & Analytics
- `GET /api/leaderboard/?contest_id={id}` — Contest leaderboard  
- `GET /api/leaderboard/top/?contest_id={id}&limit=N` — Top N leaderboard  
- `GET /api/leaderboard/global/?country=X&limit=N` — Global rating leaderboard  
- `GET /api/analytics/contests/{id}/summary/` — Contest analytics summary  

---

## ✅ Common Error Responses
- **Validation error:** 400 Bad Request `{ "field_name": ["error message"] }`  
- **Not found:** 404 Not Found `{ "detail": "Not found." }`  
- **Protected delete:** 400 Bad Request `{ "error": "Cannot delete X with existing submissions." }`  

---

## 🔧 Implementation Tips
- Use **Django REST Framework** (ViewSets + Routers recommended)  
- `django-filter` + `SearchFilter` + `OrderingFilter` for list endpoints  
- Use `UniqueConstraint` in `Meta.constraints`  
- Wrap multiple updates with `transaction.atomic()`  
- Use Celery/RQ for background tasks (judge simulation, finalize)  
- Add unit tests for rating algorithm, leaderboard ordering, deletion constraints  
- Add OpenAPI docs (`drf-spectacular` or `drf-yasg`) + Postman collection  

---

## 🎯 Next Steps
Agar xohlasang, men hozir:
1. Shu README asosida **Django project skeleton** (models, serializers, basic views/urls) yozib bera olaman  
2. **Postman collection** va **drf-spectacular** konfiguratsiyasini tayyorlab bera olaman  
3. **Rating algorithm unit tests** yozib bera olaman  

---

> Tayyor README.md fayli endi to‘liq, chiroyli va GitHub-ready holatda.


# 🌐 Full API Endpoints (base: `/api/`) — Barcha example’lar bilan

> Har bir endpoint uchun: `Request` (curl yoki HTTP), `Success response` va `Possible error responses`.

---

## 🏆 Contests

### 1) Create Contest
**Request**
```
POST /api/contests/
Content-Type: application/json

{
  "title": "Tashkent Code Sprint 2026",
  "location": "Tashkent, Uzbekistan",
  "start_date": "2026-05-10T09:00:00Z",
  "end_date": "2026-05-10T15:00:00Z",
  "description": "One-day rapid contest"
}
```

**Success Response**
```
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": 12,
  "title": "Tashkent Code Sprint 2026",
  "slug": "tashkent-code-sprint-2026",
  "location": "Tashkent, Uzbekistan",
  "start_date": "2026-05-10T09:00:00Z",
  "end_date": "2026-05-10T15:00:00Z",
  "problems_count": 0,
  "finalized": false,
  "created_at": "2025-11-24T11:00:00Z"
}
```

**Validation Errors**
```
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "end_date": ["End date must be greater than start date."]
}
```

---

### 2) List Contests (with filtering, pagination)
**Request**
```
GET /api/contests/?search=sprint&location=Tashkent&page=1&page_size=10
```

**Success Response**
```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 12,
      "title": "Tashkent Code Sprint 2026",
      "location": "Tashkent, Uzbekistan",
      "start_date": "2026-05-10T09:00:00Z",
      "problems_count": 6
    },
    {
      "id": 7,
      "title": "Tashkent Code Sprint 2025",
      "location": "Tashkent, Uzbekistan",
      "start_date": "2025-05-10T09:00:00Z",
      "problems_count": 8
    }
  ]
}
```

---

### 3) Retrieve Contest (detail)
**Request**
```
GET /api/contests/12/
```

**Success Response**
```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 12,
  "title": "Tashkent Code Sprint 2026",
  "slug": "tashkent-code-sprint-2026",
  "description": "One-day rapid contest",
  "location": "Tashkent, Uzbekistan",
  "start_date": "2026-05-10T09:00:00Z",
  "end_date": "2026-05-10T15:00:00Z",
  "problems_count": 6,
  "finalized": false,
  "created_at": "2025-11-24T11:00:00Z",
  "problems": [
    {"id":45,"code":"A","title":"Sum of Two","max_score":100},
    {"id":46,"code":"B","title":"Array Max","max_score":100}
  ]
}
```

---

### 4) Update Contest (PATCH)
**Request**
```
PATCH /api/contests/12/
Content-Type: application/json

{
  "description": "Updated description with more details"
}
```

**Success Response**
```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 12,
  "description": "Updated description with more details",
  "updated_at": "2025-11-24T12:00:00Z"
}
```

---

### 5) Delete Contest (blocked if submissions exist)
**Request**
```
DELETE /api/contests/12/
```

**Error Response (if submissions exist)**
```
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": "Cannot delete contest with existing submissions. Tournament has active submissions."
}
```

**Success Response (if no submissions)**
```
HTTP/1.1 204 No Content
```

---

### 6) Finalize Contest (compute ratings)
**Request**
```
POST /api/contests/12/finalize/
Content-Type: application/json

{ "force": true }
```

**Success Response**
```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "contest_id": 12,
  "finalized_at": "2025-11-24T14:00:00Z",
  "processed_players": 120,
  "rating_changes": [
    { "coder_id": 3, "old_rating": 1803, "new_rating": 1878, "delta": 75 },
    { "coder_id": 7, "old_rating": 2080, "new_rating": 2150, "delta": 70 }
  ]
}
```

**Error Response (if not allowed yet)**
```
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": "Contest has not ended yet. Use force=true to override."
}
```

---

## 👤 Coders

### 1) Create Coder
**Request**
```
POST /api/coders/
Content-Type: application/json

{
  "nickname": "CodeMaster",
  "display_name": "Ali Akbar",
  "country": "Uzbekistan"
}
```

**Success Response**
```
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": 3,
  "nickname": "CodeMaster",
  "display_name": "Ali Akbar",
  "country": "Uzbekistan",
  "rating": 1500,
  "points_total": 0,
  "total_submissions": 0,
  "accepted_submissions": 0,
  "created_at": "2025-11-24T11:00:00Z"
}
```

**Error Response (duplicate nickname)**
```
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "nickname": ["This nickname is already taken."]
}
```

---

### 2) List Coders (filters, ordering, pagination)
**Request**
```
GET /api/coders/?country=Uzbekistan&min_rating=1600&search=master&ordering=-rating&page=1&page_size=20
```

**Success Response**
```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 3,
      "nickname": "CodeMaster",
      "country": "Uzbekistan",
      "rating": 1850,
      "total_games": 45,
      "accepted_submissions": 340
    }
  ]
}
```

---

### 3) Retrieve Coder (with recent submissions & rating history)
**Request**
```
GET /api/coders/3/
```

**Success Response**
```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 3,
  "nickname": "CodeMaster",
  "display_name": "Ali Akbar",
  "country": "Uzbekistan",
  "rating": 1850,
  "points_total": 4250,
  "total_submissions": 1200,
  "accepted_submissions": 950,
  "recent_submissions": [
    {"id":1023,"problem":{"code":"A"},"status":"accepted","score":100,"submitted_at":"2025-11-24T12:00:00Z"}
  ],
  "rating_changes": [
    {"contest_id":12,"old_rating":1803,"new_rating":1878,"delta":75,"created_at":"2025-11-24T14:00:00Z"}
  ]
}
```

---

### 4) Update Coder
**Request**
```
PATCH /api/coders/3/
Content-Type: application/json

{
  "display_name": "Ali A."
}
```

**Success Response**
```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 3,
  "display_name": "Ali A.",
  "updated_at": "2025-11-25T09:00:00Z"
}
```

---

### 5) Delete Coder (blocked if submissions)
**Request**
```
DELETE /api/coders/3/
```

**Error Response (has submissions)**
```
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": "Cannot delete coder. Player has 1200 recorded submissions."
}
```

**Success Response (if no submissions)**
```
HTTP/1.1 204 No Content
```

---

## 📝 Problems (nested under contest)

### 1) Create Problem
**Request**
```
POST /api/contests/12/problems/
Content-Type: application/json

{
  "title": "Sum of Two",
  "code": "A",
  "max_score": 100,
  "time_limit_ms": 1000
}
```

**Success Response**
```
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": 45,
  "contest": 12,
  "title": "Sum of Two",
  "code": "A",
  "max_score": 100,
  "time_limit_ms": 1000,
  "created_at": "2025-11-24T11:30:00Z"
}
```

**Error Response (duplicate code in same contest)**
```
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "code": ["Problem code must be unique per contest."]
}
```

---

### 2) List Problems
**Request**
```
GET /api/contests/12/problems/
```

**Response**
```
HTTP/1.1 200 OK
Content-Type: application/json

[
  {"id":45,"code":"A","title":"Sum of Two","max_score":100},
  {"id":46,"code":"B","title":"Array Max","max_score":100}
]
```

---

### 3) Delete Problem (blocked if submissions)
**Request**
```
DELETE /api/problems/45/
```

**Error Response**
```
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": "Cannot delete problem with existing submissions."
}
```

---

## 📨 Submissions

### 1) Create Submission
**Request**
```
POST /api/submissions/
Content-Type: application/json

{
  "contest": 12,
  "problem": 45,
  "coder": 3,
  "language": "python",
  "code": "print(sum(map(int, input().split())))"
}
```

**Success Response**
```
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": 1023,
  "contest": { "id": 12, "title": "Tashkent Code Sprint 2026" },
  "problem": { "id": 45, "code": "A", "title": "Sum of Two" },
  "coder": { "id": 3, "nickname": "CodeMaster" },
  "language": "python",
  "status": "pending",
  "score": 0,
  "attempt_no": 4,
  "submitted_at": "2025-11-24T12:00:00Z"
}
```

---

### 2) List Submissions (filters)
**Request**
```
GET /api/submissions/?contest=12&coder=3&status=accepted&problem_code=A&page=1
```

**Response**
```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {"id":1023,"problem":{"code":"A"},"status":"accepted","score":100,"submitted_at":"2025-11-24T12:00:00Z"}
  ]
}
```

---

### 3) Retrieve Submission
**Request**
```
GET /api/submissions/1023/
```

**Response**
```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 1023,
  "contest": { "id": 12, "title": "Tashkent Code Sprint 2026" },
  "problem": { "id": 45, "code": "A", "title": "Sum of Two" },
  "coder": { "id": 3, "nickname": "CodeMaster" },
  "language": "python",
  "status": "accepted",
  "score": 100,
  "attempt_no": 4,
  "submitted_at": "2025-11-24T12:00:00Z",
  "judged_at": "2025-11-24T12:00:30Z",
  "judge_log": "All tests passed"
}
```

---

### 4) Judge Update (internal)
> NOTE: This endpoint may be restricted to internal use in production; for test it can be public.

**Request**
```
PATCH /api/submissions/1023/judge/
Content-Type: application/json

{
  "status": "accepted",
  "score": 100,
  "judged_at": "2025-11-24T12:00:30Z",
  "judge_log": "All tests passed"
}
```

**Behavior**
- Update submission status/score/judged_at
- Recalculate `Coder.total_submissions`, `accepted_submissions`, `points_total`
- Rebuild contest-level cached leaderboard or mark for recalculation

**Success Response**
```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 1023,
  "status": "accepted",
  "score": 100,
  "judged_at": "2025-11-24T12:00:30Z"
}
```

**Error Response (invalid score)**
```
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "score": ["Score must be between 0 and problem.max_score (100)."]
}
```

---

### 5) Delete Submission
**Request**
```
DELETE /api/submissions/1023/
```

**Success Response**
```
HTTP/1.1 204 No Content
```

**Behavior**
- On delete, recalc coder counters and leaderboard

---

## 📊 Leaderboards & Analytics

### 1) Contest Leaderboard
**Request**
```
GET /api/leaderboard/?contest_id=12
```

**Response**
```
HTTP/1.1 200 OK
Content-Type: application/json

[
  {
    "rank": 1,
    "coder": "CodeMaster",
    "coder_id": 3,
    "country": "Uzbekistan",
    "rating": 1878,
    "points": 375,
    "accepted": 5,
    "attempts": 12,
    "rating_change": 75
  },
  {
    "rank": 2,
    "coder": "AlgoKing",
    "coder_id": 22,
    "country": "Kazakhstan",
    "rating": 2150,
    "points": 360,
    "accepted": 5,
    "attempts": 10,
    "rating_change": 70
  }
]
```

**Notes**
- Sort: `points desc`, `accepted_count desc`, `first_accepted_time asc`

---

### 2) Top N Leaderboard (contest)
**Request**
```
GET /api/leaderboard/top/?contest_id=12&limit=5
```

**Response**
```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "contest_id": 12,
  "contest_title": "Tashkent Code Sprint 2026",
  "limit": 5,
  "total_players": 120,
  "leaderboard": [
    { "rank": 1, "coder": "CodeMaster", "rating": 1878, "points": 375 },
    { "rank": 2, "coder": "AlgoKing", "rating": 2150, "points": 360 }
  ]
}
```

---

### 3) Global Rating Leaderboard
**Request**
```
GET /api/leaderboard/global/?country=Uzbekistan&limit=20
```

**Response**
```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "total_players": 156,
  "country": "Uzbekistan",
  "leaderboard": [
    { "rank": 1, "coder": "TopCoder", "rating": 2250, "total_games": 145 },
    { "rank": 2, "coder": "CodeMaster", "rating": 1878, "total_games": 120 }
  ]
}
```

---

### 4) Contest Analytics Summary
**Request**
```
GET /api/analytics/contests/12/summary/
```

**Response**
```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "contest_id": 12,
  "total_submissions": 2400,
  "unique_coders": 120,
  "avg_score_per_problem": { "A": 92.5, "B": 78.0, "C": 45.2 },
  "acceptance_rate": 0.42,
  "difficulty_histogram": { "easy": 2, "medium": 3, "hard": 1 }
}
```

---

# ✅ Common Error Responses (formats)

**Validation error**
```
HTTP/1.1 400 Bad Request
Content-Type: application/json

{ "field_name": ["error message"] }
```

**Not found**
```
HTTP/1.1 404 Not Found
Content-Type: application/json

{ "detail": "Not found." }
```

**Protected delete**
```
HTTP/1.1 400 Bad Request
Content-Type: application/json

{ "error": "Cannot delete X with existing submissions." }
```

---

# 🔧 Implementation tips for candidate (short checklist)
- Use `Django REST Framework` (ViewSets + Routers recommended).
- `django-filter` + `SearchFilter` + `OrderingFilter` for list endpoints.
- Use `UniqueConstraint` in `Meta.constraints`.
- Use `transaction.atomic()` when updating multiple counters (judge updates, finalize).
- Use Celery/RQ for background heavy tasks (judge simulation, finalize).
- Add unit tests for rating algorithm, leaderboard ordering, deletion constraints.
- Add OpenAPI docs (drf-spectacular or drf-yasg) + Postman collection.

---

# 🎯 Yordam kerakmi?
Agar xohlasang, men hozir:
- shu README asosida **Django project skeleton** (models, serializers, basic views/urls) yozib beraman; yoki
- **Postman collection** va **drf-spectacular** konfiguratsiyasini tayyorlab beraman; yoki
- **rating algorithm unit tests** yozib beraman.

Qaysi birini avtomatik tarzda hozirroq chiqarib berishimni xohlaysan?  
(So‘ra — men birdaniga to‘liq yozib beraman.)
