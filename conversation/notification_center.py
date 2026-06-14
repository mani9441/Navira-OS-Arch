class NotificationCenter:

    def __init__(self):

        self.notifications = []

    def notify(
        self,
        user_id,
        title,
        message
    ):

        self.notifications.append(
            {
                "user_id": user_id,
                "title": title,
                "message": message
            }
        )

    def get_user_notifications(
        self,
        user_id
    ):

        return [
            n
            for n in self.notifications
            if n["user_id"] == user_id
        ]