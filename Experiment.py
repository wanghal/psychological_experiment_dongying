from psychopy import visual, core, event, gui
import random, datetime, csv, os
from UserActionLog import UserActionLog

class Experiment(object):
    SIGN_ENUM = ['left', 'right']
    KEYBOARD_ENUM = ['f', 'j']

    def __init__(self, user_info, win):
        self.user_info = user_info
        self.win = win
        self.result_list=[]
        self.experiment_cnt=0

    def get_random_list_without_repetition(self, m, n):
        results = []
        while (len(results) < n):
            s = random.randint(0, m - 1)
            if s not in results:
                results.append(s)
        return results

    def entrance_sign(self):
        ##进入循环
        ##圆圈0.25秒，点0.5秒，空白0.2秒
        entrance_circle = visual.ImageStim(self.win, image='images/stimu_.002.jpeg')
        entrance_circle.draw()
        self.win.flip()
        core.wait(0.25)
        entrance_point = visual.ImageStim(self.win, image='images/stimu_.001.jpeg')
        entrance_point.draw()
        self.win.flip()
        core.wait(0.5)
        self.win.flip()
        core.wait(0.2)
        return True

    def show_initialized_screen(self, screen_path):
        ##初始界面
        initialized_screen = visual.ImageStim(self.win, image=screen_path)
        initialized_screen.draw()
        self.win.flip()
        core.wait(0)
        _ = event.waitKeys(keyList=['space'])
        return True

    def go_trail(self):
        timer = core.Clock()
        self.entrance_sign()

        ##显示按键信号
        sign = self.SIGN_ENUM[random.randint(0, 1)]
        user_action_item = UserActionLog(sign)

        if sign == 'left':
            pic = visual.ImageStim(self.win, image='images/stimu_.003.jpeg')
        elif sign == 'right':
            pic = visual.ImageStim(self.win, image='images/stimu_.004.jpeg')
        pic.draw()
        self.win.flip()
        core.wait(0)

        ##用户键入, f代表left, j代表right，并记录时间
        timer.reset()
        k = event.waitKeys(keyList=self.KEYBOARD_ENUM, maxWait=1.25)
        user_action_item.user_action_time = int(timer.getTime() * 1000)

        ##检查用户选择结果
        if user_action_item.user_action_time >= 1250:
            pic = visual.ImageStim(self.win, image='images/stimu_.008.jpeg')
            pic.draw()
            self.win.flip()
            core.wait(0.25)
            self.win.flip()
            core.wait(2)
            user_action_item.user_action_time = 1250
            user_action_item.user_action = 'no actions'
        elif self.KEYBOARD_ENUM.index(k[0]) != self.SIGN_ENUM.index(sign):
            pic = visual.ImageStim(self.win, image='images/stimu_.007.jpeg')
            pic.draw()
            self.win.flip()
            core.wait(0.25)
            user_action_item.user_action = 'incorrect'
        else:
            user_action_item.user_action = 'correct'

        return user_action_item

    def stop_trail(self, ssd_time):
        timer = core.Clock()
        self.entrance_sign()

        ##显示按键信号
        sign = self.SIGN_ENUM[random.randint(0, 1)]
        user_action_item = UserActionLog(sign)

        if sign == 'left':
            pic = visual.ImageStim(self.win, image='images/stimu_.003.jpeg')
        elif sign == 'right':
            pic = visual.ImageStim(self.win, image='images/stimu_.004.jpeg')
        pic.draw()
        self.win.flip()
        core.wait(0)

        ##SSD 在[50, 1150] 之间
        if ssd_time < 50:
            ssd_time = 50
        elif ssd_time > 1150:
            ssd_time = 1150
        user_action_item.ssd_time = ssd_time

        # 等待ssd时间，看用户是否输入
        timer.reset()
        k_1 = event.waitKeys(keyList=self.KEYBOARD_ENUM, maxWait=float(ssd_time) / 1000)

        ##显示stop信号
        if sign == 'left':
            pic = visual.ImageStim(self.win, image='images/stimu_.006.jpeg')
        elif sign == 'right':
            pic = visual.ImageStim(self.win, image='images/stimu_.005.jpeg')
        pic.draw()
        self.win.flip()
        core.wait(0)

        # 等待1250 - ssd时间，看用户是否输入
        k_2 = event.waitKeys(keyList=self.KEYBOARD_ENUM, maxWait=float(1250 - ssd_time) / 1000)

        if not k_1 and not k_2:
            user_action_item.whether_stoped = True
        else:
            user_action_item.whether_stoped = False

        self.win.flip()
        core.wait(2)

        return user_action_item

    def record_to_user_info(self):
        self.user_info.fail_cnt.append(self.fail_cnt)
        self.user_info.no_action_cnt.append(self.no_action_cnt)
        self.user_info.ave_action_time.append(self.ave_action_time)
        self.user_info.stop_rate.append(self.stop_rate)
        self.user_info.ave_ssd.append(self.ave_ssd)

    def process(self):
        self.experiment_cnt += 1
        ssd_time = 250
        if self.experiment_cnt == 1:
            self.show_initialized_screen()

        stop_list = self.get_random_list_without_repetition(self.go_trail_number + self.stop_trail_number,
                                                            self.stop_trail_number)
        for i in range(self.go_trail_number + self.stop_trail_number):
            if i in stop_list:
                user_action_item = self.stop_trail(ssd_time)
                if user_action_item.whether_stoped:
                    ssd_time += 50
                else:
                    ssd_time -= 50
            else:
                user_action_item = self.go_trail()
            self.result_list.append(user_action_item)
        self.write_logs()

        self.fail_cnt, self.no_action_cnt, self.ave_action_time, self.stop_rate, self.ave_ssd = \
            self.analyze_result(self.result_list)
        self.show_analyze_result()
        self.user_info.result_list.extend(self.result_list)
        self.result_list = []

        if self.experiment_cnt in [1, 2]:
            self.show_gap_screen()
        elif self.experiment_cnt in [3]:
            self.show_ending_screen()
            self.user_info.record_user_result()
        return True

    def write_logs(self, file_path):
        with open('outputs'+ os.sep + self.user_info.path_name + os.sep + file_path + '.csv', 'w+') as f:
            writer = csv.writer(f, dialect='unix')
            writer.writerow(['sign', 'user_action', 'user_action_time', 'whether_stoped', 'ssd_time'])
            for item in self.result_list:
                writer.writerow(item.attributes_to_list())
        f.close()
        return True

    @staticmethod
    def analyze_result(result_list):
        action_time, pass_cnt, fail_cnt, no_action_cnt = 0, 0, 0, 0
        ssd_time, stop_cnt, not_stop_cnt = 0, 0, 0
        for item in result_list:
            # 计算平均用户反应时间
            # 计算正确率
            if item.user_action == 'correct':
                pass_cnt += 1
                action_time += item.user_action_time
            elif item.user_action == 'incorrect':
                fail_cnt += 1
            elif item.user_action == 'no actions':
                no_action_cnt += 1
            else:
                # 计算平均ssd时间
                if item.whether_stoped:
                    stop_cnt += 1
                else:
                    not_stop_cnt += 1
                ssd_time += item.ssd_time
        if pass_cnt != 0:
            ave_action_time = float(action_time) / pass_cnt
        else:
            ave_action_time = 0
        if (stop_cnt + not_stop_cnt) != 0:
            stop_rate = float(stop_cnt) / (stop_cnt + not_stop_cnt)
        else:
            stop_rate = 0
        if (stop_cnt + not_stop_cnt) != 0:
            ave_ssd = float(ssd_time) / (stop_cnt + not_stop_cnt)
        else:
            ave_ssd = 0
        return fail_cnt, no_action_cnt, ave_action_time, stop_rate, ave_ssd

    def show_analyze_result(self):
        text_stop_rate = visual.TextStim(self.win, text='stop trail 成功抑制比: ' + str(round(self.stop_rate, 2)),
                                         pos=(0.0, 0.2), color='red')
        text_ave_ssd = visual.TextStim(self.win, text='平均ssd时间: ' + str(round(self.ave_ssd, 2)),
                                       pos=(0.0, 0), color='blue')
        text_ave_action_time = visual.TextStim(self.win, text='判断正确的平均反应时间: ' + str(round(self.ave_action_time, 2)),
                                               pos=(0.0, -0.2), color='green')
        text_stop_rate.draw()
        text_ave_ssd.draw()
        text_ave_action_time.draw()
        self.win.flip()
        core.wait(5)
        return True

    def show_gap_screen(self):
        ##每段实验结束后的间隔
        rest_screen = visual.ImageStim(self.win, image='images/stimu_.013.jpeg')
        rest_screen.draw()
        self.win.flip()
        core.wait(5)

        restart_screen = visual.ImageStim(self.win, image='images/stimu_.014.jpeg')
        restart_screen.draw()
        self.win.flip()
        core.wait(0)
        _ = event.waitKeys(keyList=['space'])
        return True

    def show_ending_screen(self):
        ##全部实验结束后
        ending_screen = visual.ImageStim(self.win, image='images/stimu_.015.jpeg')
        ending_screen.draw()
        self.win.flip()
        core.wait(1)



class Practice_1(Experiment):
    def __init__(self, user_info, win, max_correct=20, max_total=50):
        """
        初始化 练习1， 成功通过max_correct个测试或练习了max_total次可通过练习实验
        :param user_info: 被测的信息
        :param win: 显示的视窗
        :param max_correct: 成功通过max_correct个测试或练习了max_total次可通过练习实验
        :param max_total: 成功通过max_totalt个测试或练习了max_total次可通过练习实验
        """
        Experiment.__init__(self, user_info, win)
        self.max_correct = max_correct
        self.max_total = max_total

    def show_initialized_screen(self):
        return super().show_initialized_screen(
            os.path.dirname(os.path.abspath(__file__)) + os.sep + 'images' + os.sep + 'stimu_.010.jpeg')

    def process(self):
        self.show_initialized_screen()
        ##两张图呈现的概率都是50%，成功通过max_correct个测试或练习了max_total次可通过练习实验
        correct_num = 0
        total_num = 0

        while (correct_num < self.max_correct and total_num < self.max_total):
            user_action_item = self.go_trail()
            total_num += 1
            if user_action_item.user_action == 'correct':
                correct_num += 1
            self.result_list.append(user_action_item)
        self.write_logs()

        self.fail_cnt, self.no_action_cnt, self.ave_action_time, self.stop_rate, self.ave_ssd = \
            self.analyze_result(self.result_list)
        self.show_analyze_result()
        return True

    def write_logs(self):
        date = datetime.datetime.now().strftime("%Y-%m-%d--%H_%M_%S")
        file_path = date + "_" + self.user_info.path_name + "_Practice_1"
        return super().write_logs(file_path)

    def show_analyze_result(self):
        text_fail_cnt = visual.TextStim(self.win, text='判断错误数量: ' + str(self.fail_cnt),
                                        pos=(0.0, 0.2), color='red')
        text_no_action_cnt = visual.TextStim(self.win, text='未作出判断数量: ' + str(self.no_action_cnt),
                                        pos=(0.0, 0), color='yellow')
        text_ave_action_time = visual.TextStim(self.win, text='判断正确的平均反应时间: ' + str(self.ave_action_time),
                                        pos=(0.0, -0.2), color='green')
        text_fail_cnt.draw()
        text_no_action_cnt.draw()
        text_ave_action_time.draw()
        self.win.flip()
        core.wait(2)
        return True

class Practice_2(Experiment):
    def __init__(self,user_info, win, go_trail_number=9, stop_trail_number=3):
        """
        初始化 练习2，
        :param user_info: 被测的信息
        :param win: 显示的视窗
        :param go_trail_number: go_trail 预设数量
        :param stop_trail_number: stop_trail 预设数量
        """
        Experiment.__init__(self, user_info, win)
        self.go_trail_number = go_trail_number
        self.stop_trail_number = stop_trail_number

    def show_initialized_screen(self):
        return super().show_initialized_screen(
            os.path.dirname(os.path.abspath(__file__)) + os.sep + 'images' + os.sep + 'stimu_.011.jpeg')

    def process(self):
        ssd_time = 250
        self.show_initialized_screen()

        stop_list = self.get_random_list_without_repetition(self.go_trail_number + self.stop_trail_number,
                                                            self.stop_trail_number)
        for i in range(self.go_trail_number + self.stop_trail_number):
            if i in stop_list:
                user_action_item = self.stop_trail(ssd_time)
                if user_action_item.whether_stoped:
                    ssd_time += 50
                else:
                    ssd_time -= 50
            else:
                user_action_item = self.go_trail()
            self.result_list.append(user_action_item)
        self.write_logs()

        self.fail_cnt, self.no_action_cnt, self.ave_action_time, self.stop_rate, self.ave_ssd = \
            self.analyze_result(self.result_list)
        self.show_analyze_result()
        self.result_list = []
        return True

    def write_logs(self):
        date = datetime.datetime.now().strftime("%Y-%m-%d--%H_%M_%S")
        file_path = date + "_" + self.user_info.path_name + "_Practice_2"
        return super().write_logs(file_path)


class Formal_Experiment(Experiment):
    def __init__(self, user_info, win, go_trail_number=12, stop_trail_number=4):
        """
        初始化 正式实验，
        :param user_info: 被测的信息
        :param win: 显示的视窗
        :param go_trail_number: go_trail 预设数量
        :param stop_trail_number: stop_trail 预设数量
        """
        Experiment.__init__(self, user_info, win)
        self.go_trail_number = go_trail_number
        self.stop_trail_number = stop_trail_number

    def show_initialized_screen(self):
        return super().show_initialized_screen(
            os.path.dirname(os.path.abspath(__file__)) + os.sep + 'images' + os.sep + 'stimu_.012.jpeg')

    def write_logs(self):
        date = datetime.datetime.now().strftime("%Y-%m-%d--%H_%M_%S")
        file_path = date + "_" + self.user_info.path_name + "_Formal_Experiment_" + str(self.experiment_cnt)
        return super().write_logs(file_path)




