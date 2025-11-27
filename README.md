# 🧠 API Coders — Advanced Programming Contest Backend (Django REST)

Ushbu loyiha real kompaniyalar beradigan “advanced backend test-vazifa” asosida yaratilgan.  
Tizim onlayn dasturlash olimpiadalari uchun **contest**, **coder**, **problem**, **submission**,  
va **leaderboard/rating** boshqaruvini ta’minlaydi.

API to‘liq **open API** tarzida ishlaydi (test uchun).  
Barcha ma’lumotlar **JSON** formatida qaytariladi.

---

## 📦 **Apps Strukturası**
```
contests/       — Contest management
coders/         — Coder profiles & stats
problems/       — Problems inside contests
submissions/    — Code submissions & judging
leaderboard/    — Rating change & leaderboards
```

---

# 🧩 **Models (to‘liq aniqlangan)**

> **Timestamps:** barcha vaqtlar UTC, API’da ISO-8601 qaytadi.

---

## `contests.models.Contest`
```
id              AutoField(pk)
title           CharField(200)  [required]
slug            SlugField(220, unique)
description     TextField(null=True, blank=True)
location        CharField(100)
start_date      DateTimeField [required]
end_date        DateTimeField [required]
visibility      CharField(choices=['public','private'], default='public')
finalized       BooleanField(default=False)
problems_count  IntegerField(default=0)
created_at      DateTimeField(auto_now_add=True)
updated_at      DateTimeField(auto_now=True)

Meta:
    ordering = ['-start_date']

Constraints:
    end_date > start_date
    optional unique: (title, start_date, location)

Delete rule:
    ❌ Cannot delete if submissions exist → return HTTP 400
```

---

## `coders.models.Coder`
```
id                  AutoField(pk)
nickname            CharField(50, unique)  [required]
display_name        CharField(120, blank=True)
country             CharField(50)
bio                 TextField(blank=True, null=True)
rating              IntegerField(default=1500)
points_total        IntegerField(default=0)
total_submissions   IntegerField(default=0)
accepted_submissions IntegerField(default=0)
created_at          DateTimeField(auto_now_add=True)
updated_at          DateTimeField(auto_now=True)

Delete rule:
    ❌ Cannot delete if coder has submissions
```

---

## `problems.models.Problem`
```
id                  AutoField
contest             FK → Contest (CASCADE)
title               CharField(200)
code                CharField(20)  # e.g. A, B, C
max_score           IntegerField(default=100)
time_limit_ms       IntegerField(default=1000)
memory_limit_kb     IntegerField(default=65536)
created_at          DateTimeField(auto_now_add=True)

Meta:
    unique_together = (contest, code)

Delete rule:
    ❌ Cannot delete if submissions exist
```

---

## `submissions.models.Submission`
```
id              AutoField
contest         FK → Contest (PROTECT)
problem         FK → Problem (PROTECT)
coder           FK → Coder (PROTECT)
language        CharField(50)
code            TextField
status          CharField(choices=[
                    'pending','accepted','wrong_answer',
                    'runtime_error','time_limit',
                    'compilation_error','partial'
                ], default='pending')
score           IntegerField(default=0)
attempt_no      IntegerField(default=1)
submitted_at    DateTimeField(auto_now_add=True)
judged_at       DateTimeField(null=True, blank=True)

Meta:
    ordering = ['-submitted_at']

Behavior:
    - Judge update sets score/status/judged_at
    - Recalculates coder stats
```

---

## `leaderboard.models.RatingChange`
```
id          AutoField
coder       FK → Coder (CASCADE)
contest     FK → Contest (CASCADE)
old_rating  IntegerField
new_rating  IntegerField
delta       IntegerField
reason      CharField(255)
created_at  DateTimeField(auto_now_add=True)

Index:
    (coder, created_at)
```

---

# ⚙️ **Business Rules**

### ✔ 1. Open API
Test topshirig‘i sifatida barcha endpointlar autentifikatsiyasiz mavjud.

### ✔ 2. Submission scoring
```
0 <= score <= problem.max_score
accepted if status=="accepted" OR score == max_score
attempt_no auto-increment per coder+problem
```

### ✔ 3. Contest Finalization
```
POST /api/contests/{id}/finalize/
```
- Recalculates all coder ratings  
- Saves `RatingChange` records  
- Sets `finalized=True`

### ✔ 4. ELO-like Rating Calculation
```
max_points = sum(max_score)
S_i = normalized performance
E_ij = expected score vs each opponent
delta_i = K * (S_i_total - E_i_total)
clamped to ±400
```

### ✔ 5. Leaderboard Rules
Sorted by:
```
1. points desc
2. accepted_count desc
3. first_accepted_time asc
```

### ✔ 6. Deletion Protection
```
Contest ❌ if submissions exist
Coder   ❌ if submissions exist
Problem ❌ if submissions exist
Submission ✔ allowed (recalculate stats)
```

### ✔ 7. Filters & Search
Examples:
```
/api/coders/?country=Uzbekistan&min_rating=1600&search=king
/api/contests/?location=Tashkent&date_from=2026-01-01
/api/submissions/?problem_code=A&status=accepted
```

---

# 🌐 **Full API Endpoints (base: /api/)**

## 🏆 Contests
```
POST    /api/contests/
GET     /api/contests/
GET     /api/contests/{id}/
PATCH   /api/contests/{id}/
DELETE  /api/contests/{id}/       (protected)
POST    /api/contests/{id}/finalize/
```

## 👤 Coders
```
POST    /api/coders/
GET     /api/coders/
GET     /api/coders/{id}/
PATCH   /api/coders/{id}/
DELETE  /api/coders/{id}/          (protected)
```

## 📝 Problems
```
POST    /api/contests/{contest_id}/problems/
GET     /api/contests/{contest_id}/problems/
GET     /api/problems/{id}/
PATCH   /api/problems/{id}/
DELETE  /api/problems/{id}/         (protected)
```

## 📨 Submissions
```
POST    /api/submissions/
GET     /api/submissions/
GET     /api/submissions/{id}/
PATCH   /api/submissions/{id}/judge/
DELETE  /api/submissions/{id}/      (allowed)
```

## 📊 Leaderboards & Analytics
```
GET     /api/leaderboard/?contest_id={id}
GET     /api/leaderboard/top/?contest_id={id}&limit={n}
GET     /api/leaderboard/global/?country=&limit=
GET     /api/analytics/contests/{id}/summary/
```

---

# 📘 **JSON Examples**

## 1) Create Contest
```json
POST /api/contests/

{
  "title": "Tashkent Code Sprint 2026",
  "location": "Tashkent, Uzbekistan",
  "start_date": "2026-05-10T09:00:00Z",
  "end_date": "2026-05-10T15:00:00Z",
  "description": "One-day rapid contest"
}
```

**Response**
```json
{
  "id": 12,
  "title": "Tashkent Code Sprint 2026",
  "slug": "tashkent-code-sprint-2026",
  "location": "Tashkent, Uzbekistan",
  "start_date": "2026-05-10T09:00:00Z",
  "end_date": "2026-05-10T15:00:00Z",
  "problems_count": 0,
  "finalized": false
}
```

---

## 2) Create Coder
```json
POST /api/coders/

{
  "nickname": "CodeMaster",
  "display_name": "Ali Akbar",
  "country": "Uzbekistan"
}
```

**Response**
```json
{
  "id": 3,
  "nickname": "CodeMaster",
  "display_name": "Ali Akbar",
  "country": "Uzbekistan",
  "rating": 1500,
  "points_total": 0,
  "total_submissions": 0,
  "accepted_submissions": 0
}
```

---

## 3) Create Submission
```json
POST /api/submissions/

{
  "contest": 12,
  "problem": 45,
  "coder": 3,
  "language": "python",
  "code": "print(sum(map(int, input().split())))"
}
```

**Response**
```json
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

### Judge update
```json
PATCH /api/submissions/1023/judge/

{
  "status": "accepted",
  "score": 100,
  "judged_at": "2025-11-24T12:00:30Z"
}
```

---

## 4) Finalize Contest
```json
POST /api/contests/12/finalize/

{ "force": true }
```

**Response**
```json
{
  "contest_id": 12,
  "processed_players": 120,
  "rating_changes": [
    { "coder_id": 3, "old_rating": 1803, "new_rating": 1878, "delta": 75 },
    { "coder_id": 7, "old_rating": 2080, "new_rating": 2150, "delta": 70 }
  ]
}
```

---

## 5) Contest Leaderboard
```json
GET /api/leaderboard/?contest_id=12
```

**Response**
```json
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

---

# 🎯 Yakuniy izoh
Ushbu README real kompaniyalar beradigan advanced backend test-vazifa formatida tuzilgan.  
GitHub’ga tayyor, professional, to‘liq va tartibli.

Agar xohlasang, shu loyihaning **Swagger**, **ERD diagramma**, **Postman collection**, yoki  
**Django project skeleton**ni ham chiqarib beraman.
