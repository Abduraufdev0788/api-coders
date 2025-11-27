from django.shortcuts import render
from django.http import HttpRequest, JsonResponse
from django.views import View

from app.contests.models import Contest

import json

class Contests(View):
    def post(self, request:HttpRequest)-> JsonResponse:
        datas = json.loads(request.body.decode())
        if isinstance(datas, dict):
            datas = [datas]

        for data in datas:
            title = data.get("title")
            location = data.get("location")
            start_date = data.get("start_date")
            end_date = data.get("end_date")
            description = data.get("description")
            visibility = data.get("visibility", "public")
            description = data.get("description", "")
            finalized = data.get("finalized", False)

            if not title:
                return JsonResponse({"error": "Title is required"}, status=400)
            if len(title) > 200:
                return JsonResponse({"error": "Title exceeds maximum length of 200 characters"}, status=400)
            
            if not location:
                return JsonResponse({"error": "Location is required"}, status=400)
            if len(location) > 100:
                return JsonResponse({"error": "Location exceeds maximum length of 100 characters"}, status=400)
            
            if not start_date:
                return JsonResponse({"error": "Start date is required"}, status=400)
            if not end_date:
                return JsonResponse({"error": "End date is required"}, status=400)
            if start_date >= end_date:
                return JsonResponse({"error": "Start date must be before end date"}, status=400)
            
            contest = Contest(
                title=title,
                location=location,
                start_date=start_date,
                end_date=end_date,
                description=description,
                visibility=visibility,
                finalized=finalized
            )
            contest.save()

            to_json = {
                "id": contest.id,
                "title": contest.title,
                "slug": contest.slug,
                "description": contest.description,
                "location": contest.location,
                "start_date": contest.start_date,
                "end_date": contest.end_date,
                "visibility": contest.visibility,
                "finalized": contest.finalized,
                "problems_count": contest.problems_count,
                "created_at": contest.created_at,
                "updated_at": contest.updated_at
            }

            return JsonResponse(to_json, status = 201)

        





