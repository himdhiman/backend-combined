import os, requests


class Github:
    @staticmethod
    def validate(auth_token):
        baseURL_AcessToken = "https://github.com/login/oauth/access_token"
        baseURLData = "https://api.github.com/user"
        baseURLMail = "https://api.github.com/user/emails"
        send_data = {
            "client_id": os.environ.get("GITHUB_CLIENT_ID"),
            "client_secret": os.environ.get("GITHUB_CLIENT_SECRET"),
            "code": auth_token,
            "redirect_uri": "",
        }
        try:
            res = requests.post(
                baseURL_AcessToken,
                data=send_data,
                headers={"Accept": "application/json"},
            )
            access_token = res.json()["access_token"]
            headers = {"Authorization": f"token {access_token}"}
            response = requests.get(baseURLData, headers=headers)
            email_response = requests.get(baseURLMail, headers=headers)
            if "id" in response.json():
                send_data = {}
                for i in email_response.json():
                    if i["primary"]:
                        send_data["email"] = i["email"]
                        break
                send_data["username"] = response.json()["login"]
                send_data["name"] = response.json()["name"]
                send_data["avatar_url"] = response.json()["avatar_url"]
                return send_data
            else:
                return "The token is either invalid or has expired"
        except:
            return "The token is either invalid or has expired"
