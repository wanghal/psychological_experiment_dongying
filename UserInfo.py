from psychopy import visual, core, event, gui
import os, csv, datetime
from Experiment import Experiment

class UserInfo(object):
    def __init__(self):
        info = {'姓名': '', '性别': ['男', '女'], '年级': ''}
        infoDlg = gui.DlgFromDict(dictionary=info,
                                  title='被试者信息（请勿为空）',
                                  order=['姓名', '性别', '年级'])
        self.name = info['姓名']
        self.sex = info['性别']
        self.grade = info['年级']
        self.path_name = self.name + '_' + self.sex + '_' + self.grade
        self.mk_dir_with_user_info()
        self.result_list = []

    def mk_dir_with_user_info(self):
        ##创建目录
        if os.path.exists('outputs' + os.sep + self.path_name):
            return True
        else:
            os.mkdir('outputs' + os.sep + self.path_name)
            return True

    def record_user_result(self):
        ##每个用户将自己的record存在自己名下
        # file_path = 'outputs' + os.sep + self.path_name + os.sep + 'record.csv'
        file_path = 'outputs' + os.sep + 'records.csv'
        if not os.path.exists(file_path):
            with open(file_path, 'w+', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['姓名', '性别', '年级', '时间',
                                 'go trail正确平均反应时间',
                                 'go trail 错误数',
                                 'go trail missing数',
                                 'stop trail成功抑制比',
                                 'ssd平均时间'])
                ##每个用户将自己的record存在自己名下
                # date = datetime.datetime.now().strftime("%Y-%m-%d")
                # self.experiment_analyze_result()
                # writer.writerow([self.name, self.sex, self.grade, date,
                #                  round(self.ave_action_time, 2),
                #                  self.fail_cnt,
                #                  self.no_action_cnt,
                #                  round(self.stop_rate, 2),
                #                  round(self.ave_ssd, 2)])
                f.close()
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        with open(file_path, 'a', encoding='utf-8') as f:
            writer = csv.writer(f)
            self.experiment_analyze_result()
            writer.writerow([self.name, self.sex, self.grade, date,
                             round(self.ave_action_time, 2),
                             self.fail_cnt,
                             self.no_action_cnt,
                             round(self.stop_rate, 2),
                             round(self.ave_ssd, 2)])


    def experiment_analyze_result(self):
        self.fail_cnt, self.no_action_cnt, self.ave_action_time, self.stop_rate, self.ave_ssd = \
            Experiment.analyze_result(self.result_list)





