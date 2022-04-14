from rest_framework import status
from runcode import tasks
import json
from rest_framework.response import Response
from rest_framework.views import APIView
from runcode.helper import runcode_helper, runCustomTestCases


class CompileCode(APIView):
    def post(self, request):
        data = runcode_helper(request.data)
        return Response(data=data, status=status.HTTP_200_OK)


class RunTests(APIView):
    def post(self, request):
        data = runCustomTestCases(request.data)
        return Response(data=data, status=status.HTTP_200_OK)


class RunCode(APIView):
    def post(self, request):
        body = json.loads(request.body)
        body["created_By"] = request.user.email

        arr1 = body["created_By"].split("@")
        arr2 = arr1[1].split(".")
        uid = arr1[0] + arr2[0] + arr2[1]

        context = {"body": body, "uid": uid}
        tasks.runCode.delay(context)
        return Response(status=status.HTTP_202_ACCEPTED)
