from django.conf import settings
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from problems.models import (
    Problem,
    Submission,
    Tag,
    UpvotesDownvote,
    Bookmark,
    Editorial,
    SavedCode,
    ProblemMedia,
)
import json
from problems.serializers import (
    AllSubmissionsSerializer,
    TagSerializer,
    TagSerializerCreateProblem,
    ProblemListSerializer,
    ProblemSerializer,
    GetProblemSerializer,
    ProblemListStatusSerializer,
    SubmissionListSerializer,
    EditorialSerializer,
    SavedCodeSerializer,
)
from datetime import datetime
from runcode.helper import encode_data
from problems.helper import convert_string_to_list, base_encoding


class getTagList(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, _):
        data = Tag.objects.all().order_by("name")
        data = TagSerializer(data, many=True)
        return Response(data=data.data, status=status.HTTP_200_OK)


class getTagListCreateProblem(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, _):
        data = Tag.objects.all().order_by("name")
        data = TagSerializerCreateProblem(data, many=True)
        res_dict = {}
        res_dict["success"] = True
        res_dict["results"] = data.data
        return Response(data=res_dict, status=status.HTTP_200_OK)


class getProblemsList(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, _):
        data = Problem.objects.filter(approved_by_admin=True)
        data = ProblemListSerializer(data, many=True, context={})
        return Response(data=data.data, status=status.HTTP_200_OK)


class getFilteredProblemList(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        req_data = request.data
        tags = req_data.get("tags")
        difficulty = req_data.get("difficulty")
        keyword = req_data.get("keyword")
        data = Problem.objects.filter(approved_by_admin=True)
        if keyword and keyword != "":
            data = data.filter(title__icontains=keyword).distinct()
        if tags and len(tags) > 0:
            data = data.filter(tags__id__in=tags).distinct()
        if difficulty and len(difficulty) > 0:
            data = data.filter(problem_level__in=difficulty).distinct()
        data = ProblemListSerializer(data, many=True)
        return Response(data=data.data, status=status.HTTP_200_OK)


class getProblemsStatus(APIView):
    def post(self, request):
        req_data = request.data["data"]
        data = Problem.objects.filter(id__in=req_data["ids"])
        data = ProblemListStatusSerializer(
            data, many=True, context={"mail_id": request.user.email}
        )
        return Response(data=data.data, status=status.HTTP_200_OK)


class AddProblem(APIView):
    def post(self, request):
        request_data = request.data["data"]
        request_data["created_by"] = request.user.email
        public_ids = request_data.pop("public_ids")
        serializer_obj = ProblemSerializer(data=request_data)
        if serializer_obj.is_valid():
            obj = serializer_obj.save()
            obj.media_ids = json.dumps(public_ids)
            setattr(obj, "max_score", 100)
            obj.save()
            return_data = serializer_obj.data
            return_data["id"] = obj.id
            return Response(data=return_data, status=status.HTTP_201_CREATED)
        return Response(data=serializer_obj.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateProblem(APIView):
    def post(self, request):
        request_data = request.data["data"]
        problem = Problem.objects.get(id=request_data["id"])
        for key, value in request_data.items():
            if key == "tags":
                problem.tags.set(value)
            elif key != "id":
                setattr(problem, key, value)
        problem.save()
        return Response(status=status.HTTP_202_ACCEPTED)


class UploadProblemImage(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        res = ProblemMedia.objects.create(
            image=base_encoding.base64_file(request.data["image"])
        )
        data = {"url": res.image.url, "public_id": res.id}
        return Response(data=data, status=status.HTTP_201_CREATED)


class UploadTestCases(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        probId = request.data["probId"]
        problem = Problem.objects.get(id=probId)
        setattr(problem, "sample_Tc", request.data["custom_test_cases"])
        setattr(problem, "total_Tc", request.data["test_cases"])
        problem.save()
        for key, _ in request.FILES.items():
            blob = settings.BUCKET.blob(f"media/TestCases/{str(probId)}/{key}.txt")
            blob.upload_from_file(request.FILES[key])
        return Response(status=status.HTTP_200_OK)


class GetProblem(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, _, id):
        prob_obj = Problem.objects.get(id=id)
        data = GetProblemSerializer(prob_obj)
        return Response(data=data.data, status=status.HTTP_200_OK)


class HandleUpvoteDownvote(APIView):
    def post(self, request):
        request_data = request.data["data"]
        request_data["email"] = request.user.email

        problem_obj = Problem.objects.get(id=request_data["problem_id"])

        obj = UpvotesDownvote.objects.filter(mail_Id=request_data["email"])
        if len(obj) == 0:
            vote_object = UpvotesDownvote(
                mail_Id=request_data["email"], upvote="[]", downvote="[]"
            )
            vote_object.save()
        else:
            vote_object = obj.first()
        if request_data["type"] == "upvote":
            list_data = convert_string_to_list.convert_to_list(vote_object.upvote)
            if request_data["problem_id"] in list_data:
                problem_obj.up_votes -= 1
                problem_obj.save()
                list_data.remove(request_data["problem_id"])
            else:
                problem_obj.up_votes += 1
                problem_obj.save()
                list_data.append(request_data["problem_id"])
            setattr(vote_object, "upvote", str(list_data))
            vote_object.save()
        elif request_data["type"] == "downvote":
            list_data = convert_string_to_list.convert_to_list(vote_object.downvote)
            if request_data["problem_id"] in list_data:
                problem_obj.down_votes -= 1
                problem_obj.save()
                list_data.remove(request_data["problem_id"])
            else:
                problem_obj.down_votes += 1
                problem_obj.save()
                list_data.append(request_data["problem_id"])
            setattr(vote_object, "downvote", str(list_data))
            vote_object.save()
        else:
            list_data = convert_string_to_list.convert_to_list(vote_object.upvote)
            if request_data["problem_id"] in list_data:
                problem_obj.up_votes -= 1
                problem_obj.save()
                list_data.remove(request_data["problem_id"])
            else:
                problem_obj.up_votes += 1
                problem_obj.save()
                list_data.append(request_data["problem_id"])
            setattr(vote_object, "upvote", str(list_data))
            vote_object.save()
            list_data = convert_string_to_list.convert_to_list(vote_object.downvote)
            if request_data["problem_id"] in list_data:
                problem_obj.down_votes -= 1
                problem_obj.save()
                list_data.remove(request_data["problem_id"])
            else:
                problem_obj.down_votes += 1
                problem_obj.save()
                list_data.append(request_data["problem_id"])
            setattr(vote_object, "downvote", str(list_data))
            vote_object.save()
        return Response(status=status.HTTP_200_OK)


class GetProblemPageData(APIView):
    def get(self, request, id):
        request_data = request.data
        request_data["problem_id"] = id
        request_data["email"] = request.user.email

        obj = UpvotesDownvote.objects.filter(mail_Id=request_data["email"])
        return_data = {
            "upvote": False,
            "downvote": False,
            "bookmarked": False,
            "submissions": 0,
        }
        submission_data = Submission.objects.filter(
            created_By=request_data["email"], problem_Id=request_data["problem_id"]
        )
        if len(submission_data) > 0:
            return_data["submissions"] = len(submission_data)
        bookmark_obj = Bookmark.objects.filter(user=request_data["email"])
        if len(bookmark_obj) != 0:
            bookmark_obj = bookmark_obj.first()
            bookmark_list = convert_string_to_list.convert_to_list(bookmark_obj.data)
            if request_data["problem_id"] in bookmark_list:
                return_data["bookmarked"] = True
        if len(obj) == 0:
            return Response(data=return_data, status=status.HTTP_200_OK)
        obj = obj.first()
        list_data = convert_string_to_list.convert_to_list(obj.upvote)
        if request_data["problem_id"] in list_data:
            return_data["upvote"] = True
            return Response(data=return_data, status=status.HTTP_200_OK)
        list_data = convert_string_to_list.convert_to_list(obj.downvote)
        if request_data["problem_id"] in list_data:
            return_data["downvote"] = True
            return Response(data=return_data, status=status.HTTP_200_OK)
        return Response(data=return_data, status=status.HTTP_200_OK)


class GetSubmissionsList(APIView):
    def get(self, request, id):
        request_data = request.data
        request_data["problem_id"] = id
        request_data["email"] = request.user.email

        data = Submission.objects.filter(
            created_By=request_data["email"], problem_Id=request_data["problem_id"]
        ).order_by("-submission_Date_Time")
        return_data = SubmissionListSerializer(data, many=True)
        return Response(data=return_data.data, status=status.HTTP_200_OK)


class HandleBookmark(APIView):
    def post(self, request):
        request_data = request.data
        request_data["email"] = request.user.email

        obj = Bookmark.objects.filter(user=request_data["email"])
        print(obj)
        if len(obj) == 0:
            bookmark_object = Bookmark(user=request_data["email"], data="[]")
            bookmark_object.save()
        else:
            bookmark_object = obj.first()
        list_data = convert_string_to_list.convert_to_list(bookmark_object.data)
        if request_data["problem_id"] in list_data:
            list_data.remove(request_data["problem_id"])
        else:
            list_data.append(request_data["problem_id"])
        setattr(bookmark_object, "data", list_data)
        bookmark_object.save()
        return Response(status=status.HTTP_200_OK)


class GetEditorial(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        data = Editorial.objects.filter(problem_Id=request.data["problem_id"])
        if len(data) > 0:
            data = EditorialSerializer(data.first())
            return Response(data=data.data, status=status.HTTP_200_OK)
        else:
            return Response(data="No Editorial Available", status=status.HTTP_200_OK)


class SaveCodeCloud(APIView):
    def post(self, request):
        request_data = request.data
        request_data["email"] = request.user.email

        obj = SavedCode.objects.filter(
            problem_Id=request_data["probId"], created_By=request_data["email"]
        )
        if len(obj) > 0:
            obj = obj.first()
            setattr(obj, "code", encode_data(request_data["code"]))
            setattr(obj, "language", request_data["language"])
            setattr(obj, "submission_Date_Time", datetime.now())
            obj.save()
        else:
            SavedCode.objects.create(
                problem_Id=request_data["probId"],
                created_By=request_data["email"],
                code=encode_data(request_data["code"]),
                language=request_data["language"],
            )
        return Response(status=status.HTTP_200_OK)


class GetsavedCode(APIView):
    def get(self, request, id):
        request_data = request.data
        request_data["problem_id"] = id
        request_data["email"] = request.user.email

        obj = SavedCode.objects.filter(
            problem_Id=request_data["problem_id"], created_By=request_data["email"]
        )
        data = SavedCodeSerializer(obj, many=True)
        return Response(data=data.data, status=status.HTTP_200_OK)


class GetUserSubmissions(APIView):
    def get(self, request):
        request_data = request.data
        request_data["email"] = request.user.email
        data = Submission.objects.filter(
            created_By=request_data["email"],
        ).order_by("-submission_Date_Time")
        return_data = AllSubmissionsSerializer(data, many=True)
        return Response(data=return_data.data, status=status.HTTP_200_OK)
