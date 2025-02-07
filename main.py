import logging
import csv
import io # 导入 io 模块
from pkg.plugin.context import register, handler, BasePlugin, APIHost, EventContext
from pkg.plugin.events import PersonNormalMessageReceived, GroupNormalMessageReceived

CSV_DATA = """角色ID,角色名称,种族,职业,所属组织/势力,性格特征,目标/动机,当前状态,备注
char_001,艾尔维,精灵,术士,灰色小队,未知,寻找知识、保护朋友、解决法术瘟疫,活跃,法师之子,有龙族血统，与加莱斯特订婚。在深水城进行冒险和学习，被卷入法术瘟疫、夺心魔、无形之主等事件。
char_002,弗利西亚,半精灵,黎儿拉牧师/诗人,竖琴手同盟,善良、纯真、有艺术天赋,寻找母亲、传播欢乐、学习,活跃,杰西纳之女，在深水城进行冒险和表演，被卷入各种事件。
char_003,瑟曼莎,梭罗鱼人,游侠/德鲁伊,翠绿闲庭/深洋隐修会,善良、好奇、有正义感,寻找身世、保护海洋、对抗夺心魔,活跃,塔萨神选试炼中，来自佩萨纳，被植入夺心魔蝌蚪，在深水城进行冒险和调查。
char_004,斯坦纳,矮人,奇械师,灰手小队,未知,寻找妻子、服务深水城,活跃,被妻子赶出家门，加入灰手小队，参与深水城冒险。
char_005,塔莱伊,歌利亚人,战士,城主联盟,勇敢、无畏、重视家庭,保护深水城、寻找安南背叛者、照顾孩子,活跃,歌利亚部落前酋长，与雷纳结婚，在深水城进行冒险和调查。
char_006,加莱斯特·银鬃,人类,未知,领主联盟/前紫龙骑士,正直、善良、有责任感，自卑,保护深水城、与艾尔维相爱,活跃,曾是圣武士，与艾尔维订婚。科米尔贵族，逃离婚约，父亲去世，曾为洛山达圣武士，后失去信仰。
char_007,雷纳·无烬,人类,未知,竖琴手同盟/十二星,善良、温柔、包容,保护深水城、帮助朋友,活跃,前公开领主之子，与塔莱伊结婚。被误认、绑架，后被小队解救。曾被夺心魔蝌蚪寄生。
char_008,福卢恩·布拉格玛,人类,园丁/狼人,无,善良、单纯、忠诚,陪伴朋友,活跃,雷纳的伴童和挚友,被妮奥月星转变为狼人。智力受损，喜欢园艺。
char_009,维纶,人类,管家,布兰达斯庄园,未知,忠于布兰达斯家族,未知,曾被噬脑怪控制。
char_010,威尔玛·布拉格玛,人类,园丁,布兰达斯庄园,未知,酗酒、家暴,死亡,被噬脑怪控制，后被证实死亡。
char_011,马崔姆·“三弦”·布莱格,卓尔/半卓尔,吟游诗人,竖琴手同盟,未知,寻找安全藏身处、帮助朋友,活跃,曾是达耶特佣兵团成员，真卓尔索伦的弟弟，被卓尔追杀。
char_012,法拉·莱法丽尔,木精灵,德鲁伊,翠绿闲庭,善良、热情,保护自然,活跃,科瑞隆的花冠老板娘，提供草药和治疗。
char_013,麦伦·战龙,人类,战士,未知,正直、豪爽,保护深水城、帮助朋友,活跃,瓦婕拉·黑杖的朋友，曾参与营救瓦婕拉。
char_014,瓦婕拉·黑杖·萨法尔,人类,法师,黑杖塔/灰色小队,未知,保护深水城,活跃,黑杖的继承人，与莱拉·银手关系微妙。
char_015,莱拉·银手,人类,法师,深水城公开领主,未知,管理深水城,活跃,深水城现在的公开领主。
char_016,里提斯·阿拉布兰特,人类,骑士,城主联盟/前铁手教团,正直、古板,维护法律,活跃,曾被执行死刑后复活，与阿拉布兰特家族有关。
char_017,达米拉,侏儒,未知,达格特·无烬的下属,未知,送信,死亡,死于午夜之泪毒药，曾受雇于达格特·无烬。
char_018,邦妮,人类/变形怪,服务员,哈欠门酒馆,未知,未知,死亡/失踪,真邦妮四年前死亡，现有邦妮为变形怪，被夺心魔蝌蚪寄生。
char_019,杜尔南,人类,哈欠门酒馆,未知,经营酒馆,活跃,哈欠门酒馆老板，曾参与山下区冒险。
char_020,雅歌拉·石拳,半兽人,雇佣兵,散塔林会,未知,未知,活跃,与达维尔·星歌合作。
char_021,达维尔·星歌,精灵,吟游诗人,散塔林会/末日劫掠者,未知,未知,被捕后释放,曾委托小队寻找福卢恩。
char_022,瓦罗普桑·格达姆,人类,作家,未知,未知,撰写书籍,活跃,曾委托小队寻找福卢恩，称号为传承制。
char_023,扎多姿·佐德/贾拉索·班瑞,人类/未知,演员/佣兵团首领,海洋少女嘉年华/达耶特佣兵团,未知,未知,活跃,路斯坎秘密领主，与达耶特佣兵团有关。
char_024,塞塔拉,人类,未知,西拉芬的愉悦,未知,经营赌场,活跃,赌场老板，涉及奴隶贸易和毒品。
char_025,萨梅雷扎·萨尔方提斯,人类,未知,珊娜萨公会（前）/血拳,未知,未知,失踪,珊娜萨公会管理者，血拳的主人，涉及非法生意。
char_026,蒙蒂娜,人类/半精灵,裁缝,未知,善良，热情，未知,活跃,f2ns的妻子，与火发相识。
char_027,火发·夜星,人类/精灵,未知,未知/前塞伦涅祭司,未知,未知,活跃,与黑蝰蛇合作，曾为塞伦涅祭司。
char_028,妮奥·月星,人类,月星家族,未知,研究狼人诅咒,活跃,狼人，福卢恩的朋友，进行狼人实验。
char_029,蜜拉贝尔,人类,牧师,苏伦教会/月之高塔,未知,侍奉苏伦,活跃,帮助治疗狼人诅咒，提供复活服务。
char_030,奥斯瓦多·卡萨兰特,人类/链魔,商人,卡萨兰特家族,未知,被转化为链魔，后恢复人形，灵魂消散,活跃,卡萨兰特家族长子，被阿斯蒙蒂斯夺走灵魂。
char_031,阿玛利亚·卡萨兰特,人类,邪术师,卡萨兰特家族/阿斯蒙蒂斯教团,未知,出卖孩子灵魂给阿斯蒙蒂斯,被捕,卡萨兰特家族女主人，与阿斯蒙蒂斯签订契约。
char_032,维克托罗·卡萨兰特,半精灵,未知,卡萨兰特家族,未知,未知,被捕,卡萨兰特家族男主人。
char_033,奥特·钢趾,矮人,未知,珊娜萨公会,未知,照料金鱼希尔加,被珊娜萨石化,珊娜萨公会的矮人。
char_034,珊娜萨,眼魔,未知,珊娜萨公会,未知,统治公会,被炸飞，下落不明,珊娜萨公会头目，陷入疯狂。
char_035,丽芙·罗达,人类,幽魂,巨魔颅骨大宅,未知,寻找父母,复活,父母双亡，生前被托付给女儿经营酒馆，后病死。
char_036,西尔维娅·罗达,人类,未知,未知,未知,寻找骷髅港,死亡,幽魂状态，丽芙的母亲。
char_037,达伦·罗达,人类,未知,未知,未知,寻找骷髅港,死亡,幽魂状态，丽芙的父亲。
char_038,吉姆船长,人类,未知,未知,未知,寻找宝藏,附身于提灯,消散,幽魂，希望回到自己的船上。
char_039,麦基,侏儒,未知,半身人幸运酒馆,未知,经营酒馆,活跃,半身人幸运酒馆老板。
char_040,法尔孔/莱瑞斯卡斯·科尔莫恩斯玛格,青铜龙/梭罗鱼人,德鲁伊,翠绿闲庭/深洋隐修会,未知,保护自然、守护深海,被囚禁后脱困，下落不明,来自佩萨纳，被夺心魔和无形之主囚禁。
char_041,斯诺彼得,矮人/高等精灵,德鲁伊,斯诺彼得庄园,未知,经营酒庄,活跃,被转生为精灵，儿子变成鼠人。
char_042,巴迪,狗,圣武士,斯诺彼得庄园,未知,守护庄园,活跃,被斯诺彼得立誓。
char_043,哈科·践誓,矮人,未知,珊娜萨公会,未知,作恶,死亡,被塔莱伊杀死，参与码头区招募天狗。
char_044,文森特·特兰齐,人类/罗刹,侦探,虎眼侦探所,未知,调查案件,被f2ns杀死,罗刹，伪装成侦探，委托小队调查。
char_045,沙奎姆,人类/夺心魔,未知,深洋隐修会,未知,未知,活跃,白色夺心魔，传达塔萨的意愿。
char_046,赫尔达,半精灵,未知,未知,未知,盗窃,死亡,被索伦杀死，与丈夫在码头区活动。
char_047,索伦·希布林达斯,卓尔,火枪手,达耶特佣兵团,未知,憎恨精灵和半精灵,未知,玛崔姆的哥哥，杀死半精灵。
char_048,乌尔奎斯,夺心魔,未知,无形之主,未知,未知,死亡,被瑟曼莎杀死，在萨格斯之阶活动。
char_049,格罗,底栖魔鱼,未知,格罗之石,未知,提供信息,活跃,在格罗之石中提供信息。
char_050,卡尔-阿尔·克拉达尼,半卓尔,未知,龙与酒壶,未知,经营酒馆,活跃,信仰伊莉丝翠，提供竖琴手同盟安全屋。
char_051,泽丽丝·浅叶,人类,法师,安民法师会,未知,未知,活跃,可以检测拟像。
char_052,格里达,灰矮人,未知,未知,未知,拐卖奴隶,被捕，判处死刑，在雾滩拐卖奴隶。
char_053,塔什林·雅菲拉,人类,未知,散塔林会/末日劫掠者,未知,接替达维尔·星歌,活跃,委托f2ns藏匿。
char_054,安布罗斯·永晓,人类,骑士,凯兰沃,未知,抓捕死灵法师,活跃,在死者之城巡逻。
char_055,欧芭雅·乌黛,人类,未知,未知,未知,资助山下区远征,活跃,
char_056,克莱蒙特·奥克斯贝尔,人类,战士,领主联盟,未知,与加莱斯特相似,活跃,出现在加莱斯特的回忆中。
char_057,克拉特双子,未知,未知,未知,未知,邪恶双生子,未知,
char_058,科亚·松节油,人类,未知,未知,未知,学生,活跃,在黑杖学院请求画像。
char_059,妮奥·月星,人类,未知,未知,未知,学生,寻找水晶玫瑰,活跃,月星家族最后的遗孤，进行狼人实验。
char_060,杰西纳,人类/精灵,未知,辛特莱格剧院,未知,表演魔术,活跃,弗利西亚的父亲，达耶特佣兵团的掩护。
char_061,艾利昂,精灵,未知,未知,未知,送信,变成大象形态,活跃,艾尔维的弟弟，送信并帮助寻找抑制法术瘟疫方法。
char_062,费恩,精灵,未知,未知,未知,未知,未知,艾尔维的父亲,疑似法术瘟疫感染，居住银月城。
char_063,艾蜜莉雅,银龙,未知,未知,未知,未知,未知,艾尔维的母亲，居住银月城。
char_064,欧芭雅·乌黛,人类,未知,未知,未知,雇佣麦伦·战龙,未知,
char_065,瓦坎加·欧塔姆,人类,未知,未知,未知,南扎路港,未知,
char_066,格鲁姆沙,兽人,神祇,未知,未知,未知,未知,
char_067,卡瑞达斯,红龙,未知,高岗格吕姆,未知,守卫高岗格吕姆,死亡,被瑟曼莎杀死，与泽瑞斯结盟。
char_068,艾加莎,矮人,未知,未知,未知,未知,未知,
char_069,凯瑟琳,矮人,战士,高岗格吕姆,未知,未知,死亡,参与高岗格吕姆战斗。
char_070,黎明泰坦迈盖拉,泰坦,未知,未知,未知,被封印,未知,曾被夺心魔蝌蚪控制，引发火山喷发。
char_071,第伯多夫·潘特,矮人,吸血鬼,高岗格吕姆,未知,成为吸血鬼,未知,布鲁诺战锤的朋友，被活宝石控制。
char_072,拉莱勒,斑猫人,未知,灰手小队,未知,未知,活跃,
char_073,阿斯皮尔,精灵,未知,灰手小队,未知,未知,活跃,
char_074,哈格纳什,冰霜巨人,未知,灰手小队,未知,未知,活跃,
char_075,塔林德拉·勒法莱尔,木精灵,大德鲁伊,翠绿闲庭,未知,保护自然，对精灵友好,活跃,法拉的妈妈，提供抑制法术瘟疫方法。
char_076,维吉尼亚·阿拉布兰特,人类/魔裔,未知,阿拉布兰特家族,未知,传播童谣,活跃,里提斯的侄女，被复活，传播童谣，协助小队。
char_077,莉莉娅·阿拉布兰特,魅魔/人类,未知,阿拉布兰特家族/阿斯蒙蒂斯教团,未知,未知,未知,
char_078,莉莉，白猫,未知,法尔孔庄园,未知,未知,活跃,
char_079,卡瑞达克斯,红龙,未知,高岗格吕姆,未知,守卫高岗格吕姆,死亡,与卓尔合作。
char_080,瑞斯，人类,未知,高岗格吕姆,未知,未知,未知,
char_081,伊芙丽·酒锤,矮人,未知,高岗格吕姆,未知,未知,活跃,马博的女儿，高岗格吕姆领导者。
char_082,斯特森·战锤,矮人,未知,高岗格吕姆,未知,未知,活跃,帮助重建高岗格吕姆。
char_083,先知阿兰多,人类,未知,未知,未知,做出预言,未知,圣人，做出关于托瑞尔陨灭的预言。
char_084,阿巴达·牧月者/桃雀,人类,法师,未知/十二星,未知,寻找乐谱,活跃,在遗迹中寻找乐谱。
char_085,卡琳娜姨姨,人类,未知,未知,未知,塞尔人，做药水生意,未知,
char_086,格威兹·圣·劳普桑,人类,未知,圣劳普森孤儿院,未知,院长,活跃,
char_087,艾泽瑞娜·卡萨兰特,人类,未知,卡萨兰特家族,未知,未知,被f2ns领养,卡萨兰特家族双胞胎。
char_088,特兰佐·卡萨兰特,人类,未知,卡萨兰特家族,未知,未知,被f2ns领养,卡萨兰特家族双胞胎。
char_089,黛拉·西莫海尔,人类,未知,深水理事会,未知,莱拉银手心腹,活跃,接替加莱斯特成为小队联络人。
char_090,艾诺尔·忒琳娜,卓尔,法师,艾梵德家族,未知,未知,活跃,参与萨格斯之阶战斗。
char_091,忒丽莎·艾梵德,卓尔,祭司,艾梵德家族,未知,培养巨蜘蛛,未知,被二姐要求杀死
char_092,塞尔菲斯克,卓尔,未知,艾梵德家族,未知,未知,未知,参与水刑和萨格斯之阶战斗。
char_093,乌索恩,人类,幽魂,黑杖学院,未知,制造惊喜,消散,幻术系教师，制造烟花。
char_094,加里恩/奥斯卡,变形怪,未知,满溢之缸（前）/丽芙酒馆,未知,未知,活跃,曾为满溢之缸老板，现为丽芙酒馆员工。
char_095,奥兰,未知,未知,未知,未知,未知,活跃,
char_096,尼姆,人类/侏儒,发明家,贡德神殿,未知,制造密偶,活跃,制造密偶，被小队带出神殿。
char_097,瓦莉塔,青铜龙裔,牧师,贡德神殿,未知,未知,活跃,看管尼姆和密偶。
char_098,安南,巨人,神祇,未知,未知,未知,未知,
char_099,贝拉布兰塔家族,人类,贵族,未知,未知,未知,深水城贵族，训练狮鹫,
char_100,罗兹纳家族,人类,未知,未知,未知,未知,来自安姆，曾因奴隶贸易被驱逐,
char_0014,达舍尔·斯诺彼得,矮人/鼠人,未知,珊娜萨公会,未知,未知,斯诺彼得的儿子，变成鼠人。
char_105,卡尔·阿尔·克拉达尼,卓尔,半卓尔,伊莉丝翠,未知,未知,未知,
char_106,莎莎，老鼠,未知,法尔孔庄园,未知,未知,活跃,
char_107,莫特,人类,未知,竖琴手同盟,未知,未知,活跃,
char_108,欧文·希布林达斯,卓尔,未知,未知,未知,可能为马崔姆,未知,
char_109,加克斯利·破舵,人类,未知,深水城屁股报,未知,未知,伊玛玛街和骏马街的交角处,
char_110,阿左克,大地精,未知,萨格斯之阶,未知,未知,活跃,与小队合作，对抗卓尔。
char_111,鲁尔卡纳,大地精,未知,萨格斯之阶,未知,未知,活跃,阿左克的妻子，参与萨格斯之阶战斗。
char_112,格里达,灰矮人,未知,未知,未知,拐卖奴隶,被捕，判处死刑,
char_113,祖克,歌利亚人,未知,血拳,未知,未知,活跃,
char_114,加利娜,歌利亚人,未知,西拉芬的愉悦,未知,未知,活跃,
char_115,希芙,人鱼,未知,娇羞人鱼,未知,未知,活跃,
char_116,阿拉蒂尼夫人,人鱼,未知,娇羞人鱼,未知,未知,活跃,
char_117,卡拉西亚,人类,美人鱼臂弯,未知,未知,活跃,
char_118,修斯图斯·斯塔格特,人类,士兵,未知,未知,未知,活跃,
char_119,卡尔德拉,鬼婆,未知,未知,未知,未知,未知,
char_120,费尔拉克斯,龙裔,未知,竖琴手同盟,未知,未知,活跃,
char_121,廷布尔温恩,岩侏儒,未知,当铺,未知,死亡,
char_122,塔林,岩侏儒,未知,当铺,未知,未知,活跃,
char_123,亚拉,未知,未知,未知,未知,未知,未知,
char_124,克伦拉克·布莱格,人类,未知,未知,未知,未知,马崔姆的父亲,
char_125,马博·酒锤,矮人,未知,铁手教团,未知,未知,死亡,被莉莉娅杀死，头颅在荆棘堡火盆中。
char_126,莱尔斯,提夫林,未知,荆棘堡旅店,未知,未知,未知,被维吉尼亚替换
char_127,鲁迪,人类,士兵,荆棘堡,未知,未知,死亡,被次级复原术杀死。
char_128,卢锡安,人类,士兵,荆棘堡,未知,未知,未知,
char_129,伊丝垂德·号角,矮人,未知,末日劫掠者,未知,未知,活跃,
char_130,威利福特·克维洛,提夫林,管家,卡萨兰特庄园,未知,未知,穆尔霍兰德的奴隶,
char_131,马纳夫雷特·樱港,半身人,厨师,克拉特双子塔,未知,未知,未知,
char_132,丝德拉·罗米尔,半兽人,未知,克拉特双子塔,未知,未知,未知,
char_133,尤恩,半兽人,未知,克拉特双子塔,未知,活跃,瓦罗的朋友
char_134,薇薇特·黑水,人类,未知,曼松一派,未知,未知,未知,
char_135,胡拉姆,人类,武僧,未知,未知,未知,住在深水山上, 活跃"""


@register(name="CharacterInfoPlugin", description="角色信息查询插件，从嵌入的 CSV 数据读取角色数据", version="1.2", author="AI & KirifujiNagisa") # 更新版本号
class CharacterInfoPlugin(BasePlugin):

    def __init__(self, host: APIHost):
        self.characters = []
        # 初始化 logger (使用 Python 标准库 logging)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.WARNING)
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)


    async def initialize(self):
        """插件初始化时加载角色数据"""
        try:
            self.characters = self._load_character_data(CSV_DATA) # 直接传入 CSV_DATA 字符串
            if not self.characters:
                self.logger.warning(f"嵌入的 CSV 数据为空或未找到角色数据。")
            else:
                self.logger.info(f"成功加载 {len(self.characters)} 个角色数据 from 嵌入的 CSV 数据。")
        except Exception as e:
            self.logger.exception(f"加载嵌入的 CSV 数据时发生错误: {e}")


    def _load_character_data(self, csv_string_data):
        """从 CSV 字符串加载角色数据，返回一个角色字典列表"""
        characters = []
        try:
            csv_file = io.StringIO(csv_string_data) # 使用 io.StringIO 将字符串转换为 file-like object
            reader = csv.DictReader(csv_file) # 使用 DictReader 读取 file-like object
            for row in reader:
                characters.append(row)
        except Exception as e:
            raise Exception(f"读取 CSV 字符串数据失败: {e}")
        return characters

    def _find_character_by_name(self, character_name):
        """根据角色名称查找角色信息，返回角色字典或 None"""
        for char_data in self.characters:
            if char_data.get('角色名称', '').strip() == character_name.strip():
                return char_data
            return None

    def _format_character_info(self, char_info):
        """格式化角色信息为易于阅读的字符串"""
        if not char_info:
            return "未找到该角色信息。"

        info_lines = [f"**{key}:** {value}" for key, value in char_info.items()]
        return "\n".join(info_lines)

    def _format_character_list(self):
        """格式化角色列表为易于阅读的字符串"""
        if not self.characters:
            return "角色列表为空。"
        character_names = [char['角色名称'] for char in self.characters]
        return "\n- " + "\n- ".join(character_names)

    @handler(PersonNormalMessageReceived)
    async def person_normal_message_received(self, ctx: EventContext):
        await self._handle_message(ctx)

    @handler(GroupNormalMessageReceived)
    async def group_normal_message_received(self, ctx: EventContext):
        await self._handle_message(ctx)

    async def _handle_message(self, ctx: EventContext):
        """处理私聊和群聊消息的通用逻辑"""
        msg = ctx.event.text_message.strip()

        if msg.startswith(".查询角色"):
            character_name = msg[len(".查询角色"):].strip()
            if not character_name:
                reply = "请在 `.查询角色` 命令后输入要查询的角色名称，例如：`.查询角色 艾尔维·曼维尔`"
            else:
                char_info = self._find_character_by_name(character_name)
                reply = self._format_character_info(char_info)
            ctx.add_return("reply", [reply])
            ctx.prevent_default()

        elif msg == ".列出角色名单":
            reply = self._format_character_list()
            ctx.add_return("reply", [reply])
            ctx.prevent_default()

    def __del__(self):
        pass