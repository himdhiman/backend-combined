import os, requests, json, ast
from authentication.models import StaticData

def convert_to_list(data):
    try:
        return_data = ast.literal_eval(data)
    except:
        qery_list = json.dumps(data)
        return_data = ast.literal_eval(qery_list)
    return return_data



def create_user_notifcation(email, username, create=True):
    endpoint = os.environ.get("NOTIFICATION_SERVER")
    if create:
        requests.post(endpoint + "addUser/", data={"user": email, "username": username})
    else:
        requests.post(
            endpoint + "deleteUser/", data={"user": email, "username": username}
        )
    return


class set_fixed_data:
    @classmethod
    def set_data(self, request_data):
        obj = StaticData.objects.all()[0]
        if request_data["type"] == "increase":
            if request_data["field"] == "easy":
                setattr(obj, "easy", obj.easy + 1)
            elif request_data["field"] == "medium":
                setattr(obj, "medium", obj.medium + 1)
            elif request_data["field"] == "hard":
                setattr(obj, "hard", obj.hard + 1)
        if request_data["type"] == "decrease":
            if request_data["field"] == "easy":
                setattr(obj, "easy", obj.easy - 1)
            elif request_data["field"] == "medium":
                setattr(obj, "medium", obj.medium - 1)
            elif request_data["field"] == "hard":
                setattr(obj, "hard", obj.hard - 1)
        obj.save()
        return

