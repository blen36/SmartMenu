from fastapi import Request

def get_current_user_id(request: Request):

    user_id = request.session.get("user_id")

    if not user_id:
        return None

    return user_id