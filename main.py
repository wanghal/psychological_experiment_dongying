# -*- coding: utf-8 -*-

from psychopy import visual, core, event, gui
import random, datetime, csv
from UserActionLog import UserActionLog
from Experiment import Practice_1, Practice_2, Formal_Experiment
from UserInfo import UserInfo



def main(*args, **kwargs):
    win = visual.Window(fullscr=False, size=(1200, 800), color=(-1, -1, -1))
    user_info = UserInfo()

    ##测试1
    practice_1 = Practice_1(user_info, win, max_correct=2, max_total=5)
    practice_1.process()

    ##测试2
    practice_2 = Practice_2(user_info, win, go_trail_number=3, stop_trail_number=1)
    practice_2.process()

    ##正式实验
    formal_experiment = Formal_Experiment(user_info, win, go_trail_number=3, stop_trail_number=1)
    formal_experiment.process()
    formal_experiment.process()
    formal_experiment.process()

    win.close()
    return True


if __name__ == '__main__':
    main()