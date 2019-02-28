class UserActionLog(object):
    def __init__(self, sign):
        self.sign = sign
        self.user_action = "unsigned"
        self.user_action_time = 1250    #单位为ms
        self.whether_stoped = "unsigned"    #是否成功抑制被测
        self.ssd_time = -9999

    def attributes_to_list(self):
        return [
            self.sign,
            self.user_action,
            self.user_action_time,
            self.whether_stoped,
            self.ssd_time
        ]

