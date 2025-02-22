import datetime
import time

from tooldelta import Utils, Config, Plugin, Print, plugins
import pytz



@plugins.add_plugin
class BetterAnnounce(Plugin):
    name = "公告栏"
    author = "Mono"
    version = (0, 0, 3)
    def on_def(self):

        self.ads_texts_bak = [
                "§7***************",
                "§7",
                "§b| §7{year}/{month}/{day} {week_day}",
                "§b| §7{time_cn} §{time_color}{hour}:{minute}:{second}",
                "§b",
                "§b| §f延迟 : {tps}§r",
                "§b| §f在线 §r§7: §e{num_players}",
                "§r§7",
                "§r§7***************"
            ]
        self.刷新时间 = 1
        self.title = "公告栏"
        self.tpscalc = plugins.get_plugin_api("tps计算器", (0, 0, 1), False)
        self.on_first_run = True
        
    
    def on_inject(self):
        self.flush_gg()
        self.flush_scoreboard_text()
    
    @Utils.thread_func
    def flush_gg(self):
        self.game_ctrl.sendwocmd("/scoreboard objectives remove 公告")
        time.sleep(0.3)
        self.game_ctrl.sendwocmd(
            f"/scoreboard objectives add 公告 dummy {self.title}"
        )
        self.game_ctrl.sendwocmd("/scoreboard objectives setdisplay sidebar 公告")
    
    def get_tps_str(self, color=False):
        if self.tpscalc is None:
            return "§c无前置tps计算器"
        elif color:
            return self.get_tps_color() + str(round(self.tpscalc.get_tps(), 1))
        else:
            return str(round(self.tpscalc.get_tps(), 1))
    
    def get_tps_color(self):
        tps = self.tpscalc.get_tps()
        if tps > 14:
            return "§a"
        elif tps > 10:
            return "§6"
        else:
            return "§c"
    
    def get_time_color(self,nowTime):
        hour = int(nowTime.strftime("%H"))
        if 4 <= hour < 7:
            return_value = ("清晨", "9")
        elif 7 <= hour < 11:
            return_value = ("早晨", "a")
        elif 11 <= hour < 13:
            return_value = ("午时", "c")
        elif 13 <= hour < 17:
            return_value = ("下午", "g")
        elif 17 <= hour < 22:
            return_value = ("夜晚", "b")
        elif (22 <= hour <= 23) or (0 <= hour < 4):
            return_value = ("深夜", "3")
        else:
            return_value = ("未知", "f")
        return return_value
            

    @Utils.thread_func("计分板公告文字刷新")
    def flush_scoreboard_text(self):
        self.lastest_texts=[]
        time.sleep(3)
        while True:
            
            beijing_tz = pytz.timezone('Asia/Shanghai')
            nowTime = datetime.datetime.now(beijing_tz)
            self.year = nowTime.strftime("%Y")
            self.month = nowTime.strftime("%m")
            self.day = nowTime.strftime("%d")
            self.hour=nowTime.strftime("%H")
            self.minute=nowTime.strftime("%M")
            self.second=nowTime.strftime("%S")
            self.num_players = self.game_ctrl.allplayers.__len__()
            return_value = self.get_time_color(nowTime)
            (self.time_cn,self.time_color)=return_value
            scb_score=len(self.ads_texts_bak)
            self.lastest_texts_bak=self.lastest_texts.copy()
            self.lastest_texts_bak.reverse()
            self.lastest_texts=[]
            for text in self.ads_texts_bak:
                text=Utils.SimpleFmt(
                                {
                                    "{num_players}": len(self.game_ctrl.allplayers),
                                    "{week_day}": "周"+"一二三四五六日"[time.localtime().tm_wday],
                                    "{tps}": self.get_tps_str(True),
                                    "{year}":self.year,
                                    "{month}":self.month,
                                    "{day}":self.day,
                                    "{time_cn}":self.time_cn,
                                    "{time_color}":self.time_color,
                                    "{hour}":self.hour,
                                    "{minute}":self.minute,
                                    "{second}":self.second,

                                },
                                text,
                            )
                scb_score-=1
                if not self.on_first_run:
                    if self.lastest_texts_bak[scb_score] == text:
                        self.lastest_texts.append(text)
                        continue
                    self.game_ctrl.sendwocmd(f'/scoreboard players reset "{self.lastest_texts_bak[scb_score]}" 公告')
                self.game_ctrl.sendwocmd(f'/scoreboard players set "{text}" 公告 {scb_score}')
                self.lastest_texts.append(text)
            self.on_first_run=False
            time.sleep(self.刷新时间)
    