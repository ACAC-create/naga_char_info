import logging
import csv
import io  # 导入 io 模块
import random # 导入 random 模块
from pkg.plugin.context import register, handler, BasePlugin, APIHost, EventContext
from pkg.plugin.events import PersonNormalMessageReceived, GroupNormalMessageReceived

CSV_DATA = """角色ID,角色名称,种族,职业,所属组织/势力,性格特征,目标/动机,当前状态,备注
char_001,艾尔维·曼维尔,精灵,术士,灰色小队,未知,寻找知识、保护朋友、解决法术瘟疫,活跃,法师之子,有龙族血统，与加莱斯特订婚。在深水城进行冒险和学习，被卷入法术瘟疫、夺心魔、无形之主等事件。
char_002,弗利西亚,半精灵,黎儿拉牧师/诗人,竖琴手同盟,善良、纯真、有艺术天赋,寻找母亲、传播欢乐、学习,活跃,杰西纳之女，在深水城进行冒险和表演，被卷入各种事件。
char_003,瑟曼莎,梭罗鱼人,游侠/德鲁伊,翠绿闲庭/深洋隐修会,善良、好奇、有正义感,寻找身世、保护海洋、对抗夺心魔,活跃,塔萨神选试炼中，来自佩萨纳，被植入夺心魔蝌蚪，在深水城进行冒险和调查。
char_004,斯坦纳·火须,矮人,奇械师,灰手小队,未知,寻找妻子、服务深水城,活跃,被妻子赶出家门，加入灰手小队，参与深水城冒险。
char_005,塔莱伊·杀熊者,歌利亚人,战士,城主联盟,勇敢、无畏、重视家庭,保护深水城、寻找安南背叛者、照顾孩子,活跃,歌利亚部落前酋长，与雷纳结婚，在深水城进行冒险和调查。
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
char_084,阿巴达·牧月者/桃雀,人类,法师,未知/十二星,未知/十二星,未知,寻找乐谱,活跃,在遗迹中寻找乐谱。
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



EVENT_CSV_DATA = """事件ID,事件名称,详细描述,备注/线索
ID,事件名称,详细描述,备注/线索
DGJ001,降龙节遇袭,"降龙节庆典上，PC们与雅歌拉·石拳一同击退了珊娜萨盗贼公会的袭击。袭击者身上有眼魔纹身。遭遇了来自城下区的巨魔和蚊蝠，城卫队介入。",珊娜萨盗贼公会, 城下区, 巨魔, 蚊蝠
DGJ002,瓦罗的委托,"历史学家瓦罗普桑·格达姆委托PC们寻找失踪的朋友福卢恩·布拉格玛。最后一次见到福卢恩是在巨龙串烧酒馆外，他穿着华丽，与雷纳·无烬在一起。",福卢恩·布拉格玛, 雷纳·无烬, 巨龙串烧酒馆
DGJ003,蜡烛巷仓库,"PC们在蜡烛巷的散塔林仓库中发现了被绑架的雷纳·无烬。得知福卢恩被误认为雷纳而被带走。仓库中有天狗守卫，并发现了与塔莱伊相同的纸鹤。",散塔林会, 天狗, 纸鹤, 雷纳·无烬, 福卢恩
DGJ004,下水道营救,"PC们追踪下水道中的黄色标记（珊娜萨公会标志），找到了珊娜萨公会的一个据点。击败了夺心魔和兽人，成功营救出福卢恩。发现了传送魔法装置和法术书。",珊娜萨公会, 夺心魔, 传送魔法, 法术书
DGJ005,布兰达斯庄园,"雷纳·无烬邀请PC们到他家（布兰达斯庄园）做客。揭示了关于他父亲达格特·无烬贪污五十万龙金以及格罗之石的传闻。福卢恩的真实发色是棕色，红发是染的。",布兰达斯庄园, 达格特·无烬, 格罗之石, 五十万龙金, 福卢恩
DGJ006,发现丽芙幽魂,"PC们在巨魔颅骨大宅的地窖中发现了丽芙的幽魂。得知她的父母西尔维娅·罗达和达伦·罗达去了骷髅港，一直没有回来。",丽芙, 幽魂, 骷髅港, 西尔维娅·罗达, 达伦·罗达
DGJ007,马崔姆的秘密,"受伤的马崔姆·“三弦”·莫莱格在哈欠门酒馆与PC们会面。揭示了他卓尔的身份、与达耶特佣兵团的过往，以及达耶特佣兵团与莱拉·银手因为格罗之石达成的合作。",马崔姆, 卓尔, 达耶特佣兵团, 莱拉·银手, 格罗之石
DGJ008,达米拉之死,"在布兰达斯庄园，PC们发现达米拉被割喉，体内有午夜之泪毒药。雷纳和所有仆人被捕，后被黑杖保释。达米拉的胃里检测出午夜之泪毒药。",达米拉, 午夜之泪, 黑杖, 监狱
DGJ009,西拉芬的愉悦,"在西拉芬的愉悦赌场，PC们发现了塔莱伊的族人加利娜，并得知了萨梅雷扎·萨尔方提斯的信息。赌场老板塞塔拉提供线索，让PC们去找萨梅雷扎。",西拉芬的愉悦, 塞塔拉, 加利娜, 萨梅雷扎·萨尔方提斯, 奴隶贸易
DGJ010,蓝宝石之家密道,"福卢恩告诉PC们布兰达斯庄园浴室有一条通往月星庄园塔楼的密道。雷纳的刺剑（母亲遗物）在北区大市场被盗。",蓝宝石之家, 密道, 月星庄园, 雷纳的刺剑
DGJ011,邦妮和威尔玛,"PC们在布兰达斯庄园地窖密道中发现了变形怪假扮的邦妮和福卢恩的父亲威尔玛。击败了他们，并发现了噬脑怪。",变形怪, 邦妮, 威尔玛, 噬脑怪
DGJ012,阿斯蒙蒂斯神殿,"PC们在布兰达斯庄园地道中发现了一个阿斯蒙蒂斯神殿，并与邪教徒战斗。神殿中有阿斯蒙蒂斯的雕像和壁画。",阿斯蒙蒂斯, 邪教徒, 神殿
DGJ013,卡萨兰特家族,"PC们受文森特·特兰齐委托调查卡萨兰特家族。得知他们加入了阿斯蒙蒂斯教团，并计划在建城节举行献祭仪式。获得了卡萨兰特家族宴会的请柬。",卡萨兰特家族, 阿斯蒙蒂斯教团, 献祭, 宴会, 文森特·特兰齐
DGJ014,会说话的母马,"PC们在扁钱包巷找到了会说话的母马马柯丝涅，并从她那里获得了关于扎纳瑟公会的信息。PC们买下了马柯丝涅。",马柯丝涅, 扁钱包巷, 扎纳瑟公会
DGJ015,海少女嘉年华,"PC们调查海少女嘉年华，得知其老板是扎多兹·佐德，并怀疑他与贾拉索·班瑞有关。费尔南斯在船上被扎多兹·佐德招募为演员。",海少女嘉年华, 扎多兹·佐德, 贾拉索·班瑞
DGJ016,痛苦水事件,"PC们在码头区调查精灵和半精灵水手被杀事件，发现了痛苦水这种毒品，并进行了替换。",痛苦水, 毒品, 码头区
DGJ017,加入领主联盟和灰手,"塔莱伊加入领主联盟，接受了保护清洁工的任务。艾尔维加入灰手小队，接受了询问胡拉姆的任务。",领主联盟, 灰手小队, 加莱斯特·银鬃, 瓦婕拉·黑杖
DGJ018,杰西纳的魔术,"在辛特莱格剧院，PC们观看了杰西纳的魔术表演。得知了弗利西亚父亲的真实身份（杰西纳）和达耶特佣兵团的秘密（海洋少女嘉年华是掩护）。弗利西亚的父亲希望PC们调查海少女嘉年华。",辛特莱格剧院, 杰西纳, 弗利西亚的父亲, 达耶特佣兵团, 海洋少女嘉年华
DGJ019,胡拉姆的预言,"艾尔维拜访了住在深水山洞窟中的武僧胡拉姆，获得了关于“邪恶双生子”的预言：邪恶双生子暂时隐藏面容，冬季结束前便会卸下伪装。",胡拉姆, 预言, 邪恶双生子
DGJ020,费尔南斯入狱,"费尔南斯因试图撬锁罗兹纳庄园而被捕，被判处监禁和鞭刑。",费尔南斯, 罗兹纳庄园, 监狱
DGJ021,复活斯诺彼得,"瑟曼莎帮助法尔孔女士复活了斯诺彼得，后者转生成为了一名精灵。斯诺彼得委托PC们调查他的死因。",斯诺彼得, 法尔孔, 复活, 转生
DGJ022,雷纳被噬脑怪控制,"PC们发现雷纳被噬脑怪控制，并在黑杖的帮助下进入了他的意识（布兰达斯庄园、迷宫、山下区、飞船），成功将他救回。",雷纳, 噬脑怪, 黑杖, 意识世界
DGJ023,寻找瑟曼莎,"PC们接受了萨梅雷扎·萨尔方提斯的委托，前往高路尽头的猎人小屋寻找瑟曼莎·奥尔蒂斯。",萨梅雷扎·萨尔方提斯, 瑟曼莎·奥尔蒂斯, 猎人小屋
DGJ024,发现梭罗鱼人,"PC们在深水港发现了一头年轻的青铜龙卡拉丹基里斯迪莫勒斯·科尔莫恩斯玛格，并遇到了梭罗鱼人瑟曼莎，后者成为了新的PC。青铜龙被阿格哈荣龙幕困住。",青铜龙, 梭罗鱼人, 瑟曼莎, 卡拉丹基里斯迪莫勒斯·科尔莫恩斯玛格, 阿格哈荣龙幕
DGJ025,雾滩的奴隶贸易,"PC们在雾滩发现了灰矮人拐卖奴隶的证据，并救出了塔莱伊的女儿，发现她脑中有夺心魔蝌蚪。莱拉·银手介入，取缔了奴隶贸易船。",雾滩, 灰矮人, 奴隶贸易, 夺心魔蝌蚪, 莱拉·银手
DGJ026,猎人小屋的战斗,"PC们在高路尽头的猎人小屋遭遇了噬脑怪的袭击，弗利西亚被噬脑怪寄生。找到了瑟曼莎的信件和弓箭。",猎人小屋, 噬脑怪, 弗利西亚
DGJ027,法术瘟疫,"黑杖和莱拉·银手帮助塔莱伊和弗利西亚驱逐了噬脑怪蝌蚪，并告知了关于法术瘟疫的信息。艾尔维的母亲（银龙）出现，给予艾尔维祝福和新技能。",法术瘟疫, 黑杖, 莱拉·银手, 银龙
DGJ028,卡萨兰特庄园,"PC们潜入卡萨兰特庄园。得知女主人阿玛利亚·卡萨兰特为获得财富和地位信仰了阿斯蒙蒂斯，并出卖了自己孩子的灵魂。大儿子奥斯瓦多·卡萨兰特已经被转化为链魔，被锁在阁楼里。PC们获得了建城节晚会的请柬。",卡萨兰特家族, 阿玛利亚·卡萨兰特, 奥斯瓦多·卡萨兰特, 链魔, 阿斯蒙蒂斯, 建城节晚会
DGJ029,格罗之石,"PC们从珊娜萨眼魔手中夺回了格罗之石，并得知了关于龙金宝库的信息：入口在辛特莱格剧院下方，需要三把钥匙（女王的赠礼，眼魔的眼柄，秘银战锤）。弗利西亚可以与格罗之石同调，使用“通晓传奇”法术。",格罗之石, 龙金宝库, 辛特莱格剧院, 女王的赠礼, 眼魔的眼柄, 秘银战锤
DGJ030,卡萨兰特家族的覆灭,"PC们揭露了卡萨兰特家族的罪行。费尔南斯被链魔杀死，后被格拉兹特复活为邪魔。阿玛利亚·卡萨兰特试图魅惑费尔南斯失败。PC们在庄园中发现了午夜之泪毒药和记录邪恶仪式的书籍。最终，卡萨兰特夫妇被捕，财产被没收。",卡萨兰特家族, 阿斯蒙蒂斯, 链魔, 费尔南斯, 午夜之泪, 邪恶仪式
DGJ031,黑蝰蛇的委托,"黑蝰蛇委托PC们调查罗兹纳庄园。文森特·特兰齐透露，扎多兹·佐德就是贾拉索·班瑞。黑蝰蛇偷走了卡萨兰特家的两瓶午夜之泪。",黑蝰蛇, 罗兹纳庄园, 扎多兹·佐德, 贾拉索·班瑞, 午夜之泪
DGJ032,寻找水晶玫瑰,"妮奥·月星委托PC们前往地脉迷城寻找水晶玫瑰，以解除月星家族的狼人诅咒。月星家族因凡雅克·月星信仰莎尔并加入暗夜军团而受到诅咒。",妮奥·月星, 水晶玫瑰, 月星家族, 狼人诅咒, 凡雅克·月星, 莎尔
DGJ033,地脉迷城冒险,"PC们进入地脉迷城，遭遇了各种怪物和挑战。包括卓尔（艾凡德家族）、灰矮人、鬼婆（卡尔德拉）、夺心魔（尼希卢尔、乌尔奎斯、沙奎姆）等。获得了水晶玫瑰、匕首、秘银战锤。",地脉迷城, 卓尔, 灰矮人, 鬼婆, 夺心魔, 水晶玫瑰, 匕首, 秘银战锤
DGJ034,解救福卢恩,"PC们在月星庄园的月见池中发现了狼人化的福卢恩，并帮助他恢复了正常。妮奥·月星的实验成功，福卢恩可以控制狼人形态。蜜拉贝尔姨妈可以提供复活服务。",福卢恩, 狼人, 月星庄园, 月见池, 蜜拉贝尔, 妮奥·月星
DGJ035,无限阶梯,"PC们在深水山顶发现了无限阶梯，并得知了关于法尔孔被囚禁以及凛冬的真相。法尔孔的真名是莱瑞斯卡斯·科尔莫恩斯玛格，是一条青铜龙，她的心脏是高岗格吕姆的活宝石。无限阶梯的符号：潮汐、自然、荆棘、时光、深渊。",无限阶梯, 法尔孔, 莱瑞斯卡斯·科尔莫恩斯玛格, 青铜龙, 凛冬
DGJ036,重返高岗格吕姆,"PC们重返高岗格吕姆，与矮人们并肩作战，击败了卓尔和夺心魔的联军。瑟曼莎吸收了活宝石的力量，矮人王第伯多夫·潘特恢复了正常。",高岗格吕姆, 卓尔, 夺心魔, 矮人, 活宝石, 第伯多夫·潘特
DGJ037,雷纳和塔莱伊的婚礼,"在莱拉·银手的见证下，雷纳·无烬和塔莱伊举行了婚礼。PC们获得了丰厚的奖励。",雷纳·无烬, 塔莱伊, 婚礼, 莱拉·银手
DGJ038,巨魔颅骨大宅爆炸,"巨魔颅骨大宅遭遇了爆炸袭击，弗利西亚的父亲（克隆体）在爆炸中丧生。PC们怀疑是密偶所为。",巨魔颅骨大宅, 爆炸, 弗利西亚的父亲, 密偶
DGJ039,调查爆炸案,"PC们调查爆炸案，追踪密偶的踪迹，来到了神奇之手圣堂，并结识了密偶的制造者尼姆。",爆炸案, 密偶, 神奇之手圣堂, 尼姆
DGJ040,曼松的阴谋,"PC们得知了曼松的阴谋，他企图推翻莱拉·银手，成为深水城的统治者。曼松控制了蒙面领主中的一半成员（拟像）。",曼松, 蒙面领主, 拟像, 莱拉·银手
DGJ041,捣毁珊娜萨公会,"PC们与盟友们（加莱斯特、麦伦战龙、法拉等）一起捣毁了珊娜萨公会在山下区的据点。击败了夺心魔尼希卢尔。",珊娜萨公会, 夺心魔, 尼希卢尔, 山下区
DGJ042,克拉特双子塔之战,"PC们潜入克拉特双子塔，与曼松的拟像和手下战斗。加莱斯特险些丧命。最终击败了曼松，获得了他的法术书和传送戒指。",克拉特双子塔, 曼松, 拟像, 法术书, 传送戒指
DGJ043, 弗利西亚父亲的真相,"弗利西亚发现来参加婚礼的以及在爆炸中丧生的父亲是克隆体，真正的父亲早已离开无冬城。克隆体父亲留下了黑匣子。", 弗利西亚, 父亲, 克隆体, 黑匣子
DGJ044, 维吉尼亚的请求,"维吉尼亚·阿拉布兰特请求PC们调查荆棘堡的真相，并告知了关于自己和里提斯·阿拉布兰特的往事。", 维吉尼亚·阿拉布兰特, 里提斯·阿拉布兰特, 荆棘堡
DGJ045, 占星学院的线索,"PC们在荆棘堡的战斗中发现了一件占星学院的法袍，可能与斯坦纳的妻子有关。", 占星学院, 斯坦纳的妻子
DGJ046, 疯狂交响曲,"PC们得知了关于疯狂交响曲的信息，以及它与迈盖拉的关系。一百多年前，无形之主曾试图控制迈盖拉并创作了疯狂交响曲。", 疯狂交响曲, 迈盖拉
DGJ047, 黑蝰蛇的母亲,"PC们得知黑蝰蛇的母亲雅拉和弟弟扎尔坦也与阿斯蒙蒂斯达成了协议。", 黑蝰蛇, 雅拉, 扎尔坦, 阿斯蒙蒂斯
DGJ048, 邦妮的身份,"PC们得知真正的邦妮早在四年前就已死亡，现在的邦妮是变形怪。", 邦妮, 变形怪
DGJ049, 弗卢恩的狼人形态,"PC们在月星庄园得知福卢恩变成了狼人，以及妮奥·月星的实验。", 福卢恩, 狼人, 妮奥·月星
DGJ050, 获得月之尘,"弗利西亚获得了用于治疗法术瘟疫的材料月之尘。", 月之尘, 法术瘟疫
LY001,建立前线哨站,"PC们决定在颅骨岛建立前线哨站，并着手准备。需要考虑军队、装备、补给等问题。",颅骨岛, 前线哨站, 军队
LY002,里提斯·阿拉布兰特,"PC们调查里提斯·阿拉布兰特的过去，发现他与维吉尼亚·阿拉布兰特的关系，以及他被处决的原因（包庇维吉尼亚）。",里提斯·阿拉布兰特, 维吉尼亚·阿拉布兰特, 死刑
LY003,女魔鬼维吉尼亚,"PC们与维吉尼亚·阿拉布兰特会面，得知了她与阿斯蒙蒂斯教团的关系。维吉尼亚教孩子们唱童谣，传播关于糖果屋（斯特罗姆科伦多）的信息。",女魔鬼, 维吉尼亚·阿拉布兰特, 阿斯蒙蒂斯, 童谣, 糖果屋, 斯特罗姆科伦多
LY004,无冬森林,"PC们前往无冬森林的翡翠旅店，寻求大德鲁伊塔林德拉·勒法莱尔的帮助，以解决法术瘟疫的问题。塔林德拉要求PC们杀死红龙卡瑞达克斯作为交换。",无冬森林, 翡翠旅店, 塔林德拉·勒法莱尔, 法术瘟疫, 红龙, 卡瑞达克斯
LY005,屠龙,"PC们与红龙卡瑞达克斯战斗，并将其击败。获得了龙的尸体材料。发现红龙是泽瑞思的盟友，并受无形之主指使。",红龙, 卡瑞达克斯, 泽瑞思, 无形之主
LY006,无限阶梯试炼,"PC们通过无限阶梯进入了不同的时空，接受了法尔孔的试炼。瑟曼莎获得了掌控潮汐命运的力量。首先来到了1385年的伟大熔炉。",无限阶梯, 法尔孔, 试炼, 潮汐, 1385年, 伟大熔炉
LY007,夺心魔与卓尔,"PC们在地脉迷城中继续与夺心魔和卓尔战斗。发现了更多关于无形之主的秘密，以及卓尔与夺心魔的合作关系。得知了艾凡德家族与萨尔方提斯的关系。",夺心魔, 卓尔, 无形之主, 艾凡德家族, 萨尔方提斯
LY008,丽芙酒馆开业,"PC们的丽芙酒馆正式开业，并开始盈利。雇佣了员工，包括厨师、调酒师、服务员、荷官、按摩师和保安。",丽芙酒馆, 开业, 员工
LY009,蓝焰危机,"PC们发现深水城的气候异常与法术瘟疫有关，并开始寻找解决办法。得知了法术瘟疫的传播方式和症状（蓝火）。",蓝焰危机, 法术瘟疫, 气候异常
LY010,福卢恩的狼人形态,"PC们得知福卢恩的狼人形态，以及妮奥·月星的实验。福卢恩在月见池中恢复了理智，并可以控制狼人形态。",福卢恩, 狼人, 妮奥·月星, 月见池
LY011,格罗之石预言,"弗利西亚通过格罗之石获得了关于龙金宝库的预言。得知需要三把钥匙才能打开宝库：女王的赠礼（已获得）、眼魔的眼柄（已获得）、秘银战锤（已获得）。",格罗之石, 龙金宝库, 预言, 三把钥匙
LY012,翡翠之刃,"PC们在月罗之森找到了翡翠之刃特鲁纳，并从海拉斯特·黑袍那里获得了借用它的许可。需要日长石和月长石才能与特鲁纳同调。",翡翠之刃, 特鲁纳, 海拉斯特·黑袍, 月罗之森, 日长石, 月长石
LY013,疯狂交响曲,"PC们得知了关于疯狂交响曲的信息，以及它与迈盖拉的关系。疯狂交响曲由无形之主创作，可以控制人的心智。",疯狂交响曲, 迈盖拉, 无形之主
LY014,月星家族的诅咒,"PC们了解了月星家族的狼人诅咒，以及水晶玫瑰的可能作用。水晶玫瑰可以治愈狼人诅咒。",月星家族, 狼人诅咒, 水晶玫瑰
LY015, 费恩的法术瘟疫,"艾尔维的父亲费恩感染了法术瘟疫，艾尔的母亲正在寻找伊尔明斯特寻求帮助。", 费恩, 法术瘟疫, 伊尔明斯特
LY016, 蒙面领主中的叛徒,"PC们得知蒙面领主中有一半成员被曼松的拟像替换，并受其控制。需要找到叛徒名单。", 蒙面领主, 曼松, 拟像, 叛徒
LY017, 竖琴手同盟的叛徒,"港树女士委托弗利西亚寻找竖琴手同盟中的叛徒名单，这份名单可能在曼松手中。", 竖琴手同盟, 叛徒, 港树女士
LY018, 雷纳的联姻,"港树女士希望雷纳·无烬进行政治联姻，以巩固他在深水城的地位。", 雷纳·无烬, 联姻, 港树女士
LY019, 阿巴达·牧月者,"PC们在亡者沼泽的遗迹中遇到了阿巴达·牧月者，并从他那里获得了关于预言和占星学院的信息。", 阿巴达·牧月者, 预言, 占星学院
LY020, 灰矮人的匕首,"阿左克委托PC们从灰矮人铁眼氏族手中夺回被盗的匕首。", 灰矮人, 匕首, 阿左克
LY021, 夺心魔大使乌尔奎斯,"PC们得知夺心魔乌尔奎斯是珊娜萨公会派往灰矮人的大使。", 夺心魔, 乌尔奎斯, 珊娜萨公会
LY022, 哭泣女妖号,"吉姆船长希望PC们能带他回到他的船“哭泣女妖号”。", 哭泣女妖号, 吉姆船长
LY023, 巨魔颅骨大宅的清洁工,"PC们雇佣了清洁工公会的加里恩来打扫巨魔颅骨大宅。", 加里恩, 清洁工公会
LY024, 达舍尔·斯诺彼得,"斯诺彼得委托PC们寻找他失踪的儿子达舍尔·斯诺彼得，后者可能变成了鼠人，并与珊娜萨公会有关。", 达舍尔·斯诺彼得, 鼠人, 珊娜萨公会
LY025, 哈科·践誓,"加莱斯特委托塔莱伊抓捕通缉犯哈科·践誓。", 哈科·践誓, 通缉犯
LY026, 黑蝰蛇的真实身份,"PC们得知黑蝰蛇的真实身份是艾斯薇乐·罗兹那，并了解了罗兹纳家族与阿斯蒙蒂斯的交易。", 黑蝰蛇, 艾斯薇乐·罗兹那, 罗兹纳家族, 阿斯蒙蒂斯
LY027, 末日劫掠者,"塔什林·雅菲拉委托PC们找出末日劫掠者中的叛徒。", 末日劫掠者, 叛徒, 塔什林·雅菲拉
LY028, 深水城的冬天,"深水城出现了异常的寒冷天气，可能与法术瘟疫或迈盖拉有关。", 深水城, 冬天, 法术瘟疫, 迈盖拉
""" # 事件 CSV 数据



SUSPENSE_CSV_DATA = """悬念ID,悬念名称,悬念描述,相关线索,可能答案/方向
悬念ID,悬念名称,悬念描述,相关线索,可能答案/方向
XN001,颅骨岛的珊娜萨余党,"颅骨岛上仍有珊娜萨公会的残余势力，需要被驱逐。他们的具体兵力部署、防御工事、以及可能的反击计划尚不明确。",待处理事件-颅骨岛的前线哨站建立, 珊娜萨公会, 颅骨岛, 攻城弩, 吊桥, 地道？, 鼠人掩护？, 是否与无形之主有关？
XN002,谁将成为我们的军队？,"要建立颅骨岛前线哨站，需要一支军队。目前不清楚军队的具体构成，以及如何招募和指挥这支军队。",待处理事件-颅骨岛的前线哨站建立, 地精盟友, 灰手小队, 领主联盟？, 竖琴手同盟？, 招募费用？, 指挥权归属？
XN003,黑杖的不对劲之处？,"黑杖瓦婕拉·黑杖在某些方面显得不对劲，但具体是什么原因尚不清楚。可能与法术瘟疫、曼松事件、或黑杖本身有关。",待处理事件-颅骨岛的前线哨站建立, 黑杖, 瓦婕拉·黑杖, 法术瘟疫, 曼松, 黑杖的诅咒？, 灵魂影响？
XN004,里提斯·阿拉布兰特背后的故事,"里提斯·阿拉布兰特的身世复杂，与维吉尼亚·阿拉布兰特有关。需要进一步调查他的过去，包括他与阿拉布兰特家族的关系，以及他被处决和复活的真相。",待处理事件-里提斯·阿拉布兰特背后的故事, 蓝宝石吊坠, 维尼吉亚·阿拉布兰特, 阿拉布兰特家族, 死刑, 复活, 罗兹纳家族的书
XN005,维尼吉亚的真实目的,"女魔鬼维尼吉亚·阿拉布兰特的目的是什么？她复活PC们的动机，以及她与阿斯蒙蒂斯的关系仍是谜团。她提到的糖果屋（斯特罗姆科伦多）的具体位置和用途不明。",待处理事件-女魔鬼维尼吉亚, 女魔鬼, 维吉尼亚·阿拉布兰特, 阿斯蒙蒂斯, 糖果屋, 斯特罗姆科伦多, 童谣传播, 复活动机, 糖果屋用途
XN006,童谣的传播者是谁？,"在深水城平民区传播童谣的神秘“漂亮姐姐”是谁？她传播童谣的目的，以及童谣与蓝焰危机的联系尚不清楚。",待处理事件-女魔鬼维尼吉亚, 童谣, 漂亮姐姐, 糖果屋, 蓝焰危机, 传播目的, 身份不明
XN007,失踪的邦妮,"哈欠门酒馆的女招待邦妮被珊娜萨绑架，她的生死未卜。需要调查她的下落和珊娜萨绑架她的原因。",待处理事件-女魔鬼维尼吉亚, 邦妮, 珊娜萨公会, 绑架, 生死未卜, 绑架原因
XN008,威尔玛的下落和赌博诱因,"福卢恩的父亲威尔玛失踪，他赌博成瘾的诱因尚不明确。可能与散塔林会或其他人有关。",待处理事件-女魔鬼维吉尼亚, 威尔玛, 福卢恩, 赌博, 失踪, 散塔林会？, 幕后黑手？
XN009,格罗之石的下落,"格罗之石在达米拉死后下落不明。珊娜萨公会和达耶特佣兵团都曾觊觎格罗之石，其最终归属和用途仍是谜团。",待处理事件-格罗之石的下落, 格罗之石, 珊娜萨公会, 达耶特佣兵团, 下落不明, 用途未知
XN010,无形之主如何运作？,"无形之主作为一个神秘组织，其运作方式、目的、以及与夺心魔的关系尚不清晰。需要进一步调查其背后的真相。",待处理事件-无形之主, 无形之主, 夺心魔, 运作方式, 组织目的, 幕后主使
XN011,卓尔和夺心魔的关系,"艾凡德家族的卓尔与夺心魔之间存在合作关系，但具体合作内容和目的尚不明确。泽瑞斯·艾梵德与萨尔方提斯的关系也需要进一步调查。",待处理事件-卓尔和夺心魔, 卓尔, 夺心魔, 艾凡德家族, 泽瑞斯·艾梵德, 萨尔方提斯, 合作目的, 合作内容
XN012,泽瑞斯是本体还是克隆体？,"在火山深处遇到的泽瑞斯·艾梵德，其身份是本体还是克隆体尚不确定。这关系到其背后的势力和计划。",待处理事件-卓尔和夺心魔, 泽瑞斯·艾梵德, 克隆体, 本体, 真假难辨,  幕后势力
XN013,丢失的灵魂石,"费尔南斯丢失的灵魂石，以及变成邪魔的影响仍是未知数。灵魂石的下落和丢失原因需要调查。",待办事项-f2-变成邪魔的影响，丢失的灵魂石, 费尔南斯, 灵魂石, 邪魔, 丢失原因, 下落不明, 后续影响
XN014,扁钱包巷的房子,"扁钱包巷的房子仍然空置，其装修和用途尚未决定。",待办事项-f2-扁钱包巷的房子, 扁钱包巷, 房子, 空置, 装修, 用途
XN015,南城的动物园,"南城的动物园情况不明，是否值得一去？",待办事项-南城的动物园, 南城, 动物园, 状况不明, 价值待定
XN016,装修巨魔颅骨大宅,"巨魔颅骨大宅的装修计划尚未启动，酒馆和客房的装修方案和预算需要确定。",待办事项-装修巨魔颅骨大宅，酒馆+客房, 巨魔颅骨大宅, 装修, 酒馆, 客房, 预算, 方案
XN017,萨梅雷扎·萨尔方提斯的真正目的,"萨梅雷扎·萨尔方提斯作为珊娜萨公会的管理者，血拳的主人，其真实目的和与无形之主的关系尚不明确。他涉及的非法或擦边生意也需要调查。",待办事项-萨梅雷扎·萨尔方提斯：珊娜萨公会管理者, 萨梅雷扎·萨尔方提斯, 珊娜萨公会, 无形之主, 真实目的, 非法生意
XN018,贾拉索和达耶特佣兵团的意图,"贾拉索·班瑞和达耶特佣兵团想要什么？水下潜水艇里到底发生了什么？他们与莱拉·银手合作的真正目的是什么？",待办事项-贾拉索和达耶特佣兵团想要什么？, 贾拉索·班瑞, 达耶特佣兵团, 意图不明, 水下潜水艇, 莱拉·银手, 合作目的
XN019,雷纳吊坠的秘密,"雷纳·无烬的吊坠（上面写着布兰达）的秘密，以及其与十二星组织的关系需要进一步探究。",待办事项-t-雷纳吊坠的事，顺便问问十二星组织, 雷纳·无烬, 吊坠, 布兰达, 十二星组织, 秘密, 关联
XN020,背叛者安巴罗萨,"背叛者安巴罗萨的身份和背叛行为的真相尚不清楚。",待办事项-t-背叛者：安巴罗萨, 安巴罗萨, 背叛者, 身份不明, 背叛真相
XN021,丽芙父母的下落,"丽芙父母西尔维娅·罗达和达伦·罗达在骷髅港失踪，需要找到他们的下落和真相。",待办事项-a-寻找丽芙的父母, 丽芙的父母, 西尔维娅·罗达, 达伦·罗达, 骷髅港, 下落不明, 真相
XN022,法术瘟疫或地脉迷城病症,"黑杖塔图书馆可能藏有关于法术瘟疫或地脉迷城病症的信息，需要前往查询。",待办事项-a-去找黑杖问法术瘟疫或者地脉迷城病症的事, 法术瘟疫, 地脉迷城病症, 黑杖塔图书馆, 信息查询, 治疗方法？, 病症根源？
XN023,莫特先生的竖琴手委托,"莫特先生（辛特莱格剧院）的竖琴手委托的具体内容尚不明确，可能与竖琴手联盟的任务有关。",待办事项-f-莫特先生找自己有竖琴手的事, 莫特先生, 竖琴手联盟, 委托内容, 任务细节
XN024,雷纳的竖琴手身份,"雷纳·无烬也是竖琴手联盟的成员，这与寻找弗利西亚有什么关联？",待办事项-f-雷纳也有竖琴手的事寻找弗利西亚, 雷纳·无烬, 竖琴手联盟, 关联, 弗利西亚, 目的
XN025,黑蝰蛇和罗兹纳庄园,"黑蝰蛇艾斯薇乐·罗兹纳和罗兹纳庄园的秘密，以及他们与阿斯蒙蒂斯教团的关系仍需深挖。",待办事项-黑蝰蛇和罗兹纳庄园, 黑蝰蛇, 艾斯薇乐·罗兹纳, 罗兹纳庄园, 阿斯蒙蒂斯教团, 家族秘密, 隐藏势力
XN026,雷纳和十二星组织,"雷纳·无烬和十二星组织到底是什么关系？十二星组织又是什么样的组织？",待办事项-雷纳，十二星组织到底是什么？, 雷纳·无烬, 十二星组织, 关系, 组织性质, 历史背景
XN027,莎奎姆和赫拉文的身份,"莎奎姆和赫拉文的真实身份和目的尚不清楚。他们与夺心魔和无形之主有什么关联？",待办事项-s-莎奎姆、赫拉文是怎么回事, 莎奎姆, 赫拉文, 身份不明, 目的不明, 夺心魔, 无形之主, 关联
XN028,曼松一派？,"曼松一派的具体势力范围、成员构成、以及与珊娜萨公会的关系需要进一步调查。",待办事项-曼松一派？, 曼松, 曼松一派, 势力范围, 成员构成, 珊娜萨公会, 关系
XN029,死者之城调查,"去死者之城寻找安布罗斯·永晓爵士，并调查夺心魔事件。在下水道中救出福卢恩时见到的夺心魔，与珊娜萨公会的徽记有何关联？",待办事项-s-去死者之城找安布罗斯·永晓爵士, 死者之城, 安布罗斯·永晓, 夺心魔, 珊娜萨公会, 关联, 调查方向
XN030,寻找斯诺彼得的鼠人儿子,"斯诺彼得的鼠人儿子达舍尔·斯诺彼得的下落，以及他与珊娜萨公会的关系需要查明。",待办事项-寻找斯诺彼得的鼠人儿子, 斯诺彼得, 达舍尔·斯诺彼得, 鼠人, 珊娜萨公会, 下落不明, 关联
XN031,“无形之主”的真相,"“无形之主”组织的最终目的是什么？他们与蓝焰危机的联系是什么？他们是否与法术瘟疫有关？",待办事项-“无形之主”, 无形之主, 最终目的, 蓝焰危机, 法术瘟疫, 关联, 真相
XN032,格罗之石的真正力量,"格罗之石除了定位龙金外，是否还有其他隐藏的力量或秘密？其与达格特·无烬和珊娜萨公会的关系需要进一步挖掘。",待办事项-格罗之石的下落, 格罗之石, 隐藏力量, 秘密, 达格特·无烬, 珊娜萨公会, 真正用途
""" # 悬念 CSV 数据 

@register(name="DnDInfoPlugin", description="DnD 角色、事件和悬念信息查询插件", version="1.8", author="AI & KirifujiNagisa") # 更新版本号
class DnDInfoPlugin(BasePlugin):

    def __init__(self, host: APIHost):
        self.characters = []
        self.events = []
        self.suspenses = []
        # 初始化 logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.WARNING)
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)


    async def initialize(self):
        """插件初始化时加载角色、事件和悬念数据"""
        try:
            self.characters = self._load_character_data(CSV_DATA)
            if not self.characters:
                self.logger.warning(f"嵌入的角色 CSV 数据为空或未找到角色数据。")
            else:
                self.logger.info(f"成功加载 {len(self.characters)} 个角色数据 from 嵌入的 CSV 数据。")
        except Exception as e:
            self.logger.exception(f"加载嵌入的角色 CSV 数据时发生错误: {e}")

        try:
            self.events = self._load_event_data(EVENT_CSV_DATA)
            if not self.events:
                self.logger.warning(f"嵌入的事件 CSV 数据为空或未找到事件数据。")
            else:
                self.logger.info(f"成功加载 {len(self.events)} 个事件数据 from 嵌入的事件 CSV 数据。")
        except Exception as e:
            self.logger.exception(f"加载嵌入的事件 CSV 数据时发生错误: {e}")

        try: # 加载悬念数据
            self.suspenses = self._load_suspense_data(SUSPENSE_CSV_DATA)
            if not self.suspenses:
                self.logger.warning(f"嵌入的悬念 CSV 数据为空或未找到悬念数据。")
            else:
                self.logger.info(f"成功加载 {len(self.suspenses)} 个悬念数据 from 嵌入的悬念 CSV 数据。")
        except Exception as e:
            self.logger.exception(f"加载嵌入的悬念 CSV 数据时发生错误: {e}")


    def _load_character_data(self, csv_string_data):
        """从 CSV 字符串加载角色数据，返回一个角色字典列表 (位置标识，请保持你的完整函数)"""
        characters = []
        try:
            csv_file = io.StringIO(csv_string_data)
            reader = csv.DictReader(csv_file)
            for row in reader:
                characters.append(row)
        except Exception as e:
            raise Exception(f"读取角色 CSV 字符串数据失败: {e}")
        return characters

    def _load_event_data(self, csv_string_data):
        """从 CSV 字符串加载事件数据，返回一个事件字典列表 (位置标识，请保持你的完整函数)"""
        events = []
        try:
            csv_file = io.StringIO(csv_string_data)
            reader = csv.DictReader(csv_file)
            for row in reader:
                events.append(row)
        except Exception as e:
            raise Exception(f"读取事件 CSV 字符串数据失败: {e}")
        return events

    def _load_suspense_data(self, csv_string_data):
        """从 CSV 字符串加载悬念数据，返回一个悬念字典列表"""
        suspenses = []
        try:
            csv_file = io.StringIO(csv_string_data)
            reader = csv.DictReader(csv_file)
            for row in reader:
                suspenses.append(row)
        except Exception as e:
            raise Exception(f"读取悬念 CSV 字符串数据失败: {e}")
        return suspenses

    def _find_character_by_name(self, character_name):
        """根据角色名称查找角色信息 (位置标识，请保持你的完整函数)"""
        for char_data in self.characters:
            if char_data.get('角色名称', '').strip() == character_name.strip():
                return char_data
        return None

    def _get_random_character(self):
        """随机返回一个角色信息字典 (位置标识，请保持你的完整函数)"""
        if not self.characters:
            return None
        return random.choice(self.characters)

    def _get_random_event(self):
        """随机返回一个事件信息字典 (位置标识，请保持你的完整函数)"""
        if not self.events:
            return None
        return random.choice(self.events)

    def _get_random_suspense(self):
        """随机返回一个悬念信息字典"""
        if not self.suspenses:
            return None
        return random.choice(self.suspenses)

    def _find_suspense_by_name(self, suspense_name):
        """根据悬念名称查找悬念信息，返回悬念字典或 None (位置标识，请保持你的完整函数)"""
        for suspense_data in self.suspenses:
            if suspense_data.get('悬念名称', '').strip() == suspense_name.strip():
                return suspense_data
        return None

    def _find_event_by_name(self, event_name):
        """根据事件名称查找事件信息，返回事件字典或 None (位置标识，请保持你的完整函数)"""
        for event_data in self.events:
            if event_data.get('事件名称', '').strip() == event_name.strip():
                return event_data
        return None


    def _format_character_info(self, char_info):
        """格式化角色信息为易于阅读的字符串 (位置标识，请保持你的完整函数)"""
        if not char_info:
            return "未找到该角色信息。"
        info_lines = [f"**{key}:** {value}" for key, value in char_info.items()]
        return "\n".join(info_lines)

    def _format_event_info(self, event_info):
        """格式化事件信息为易于阅读的字符串 (位置标识，请保持你的完整函数)"""
        if not event_info:
            return "未找到该事件信息。"
        info_lines = [f"**{key}:** {value}" for key, value in event_info.items()]
        return "\n".join(info_lines)

    def _format_suspense_info(self, suspense_info):
        """格式化悬念信息为易于阅读的字符串 (位置标识，请保持你的完整函数)"""
        if not suspense_info:
            return "未找到该悬念信息。"

        info_lines = [f"**{key}:** {value}" for key, value in suspense_info.items()]
        return "\n".join(info_lines)

    def _format_suspense_list(self, page_num=1, page_size=10): # 修改 _format_suspense_list 函数，添加分页参数
        """格式化悬念列表为易于阅读的字符串，支持分页"""
        if not self.suspenses:
            return ["悬念列表为空。"] #  返回列表，即使是单页错误信息

        start_index = (page_num - 1) * page_size # 计算起始索引
        end_index = start_index + page_size # 计算结束索引
        paged_suspenses = self.suspenses[start_index:end_index] #  获取当前页的悬念

        if not paged_suspenses: #  如果当前页没有悬念，说明页码超出范围
            return [f"页码超出范围，总页数 {self._get_suspense_total_pages(page_size)} 页。"]

        suspense_names = [suspense['悬念名称'] for suspense in paged_suspenses]
        page_content = "\n- " + "\n- ".join(suspense_names)
        total_pages = self._get_suspense_total_pages(page_size) # 获取总页数
        header = f"悬念列表 (第 {page_num}/{total_pages} 页):\n" # 添加页码信息
        return [header + page_content] # 返回包含页头和页内容的列表，方便后续发送多页消息

    def _get_suspense_total_pages(self, page_size=10): #  新增函数：计算悬念总页数
        """计算悬念列表的总页数"""
        return (len(self.suspenses) + page_size - 1) // page_size #  向上取整计算总页数


    def _format_character_list(self):
        """格式化角色列表为易于阅读的字符串 (位置标识，请保持你的完整函数)"""
        if not self.characters:
            return "角色列表为空。"
        character_names = [char['角色名称'] for char in self.characters]
        return "\n- " + "\n- ".join(character_names)

    def _format_event_list(self):
        """格式化事件列表为易于阅读的字符串 (位置标识，请保持你的完整函数)"""
        if not self.events:
            return "事件列表为空。"
        event_names = [event['事件名称'] for event in self.events]
        return "\n- " + "\n- ".join(event_names)


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

        elif msg == ".随机角色":
            random_char_info = self._get_random_character()
            if random_char_info:
                reply = "为你推荐一个随机角色:\n" + self._format_character_info(random_char_info)
            else:
                reply = "角色数据为空，无法随机选择角色。"
            ctx.add_return("reply", [reply])
            ctx.prevent_default()

        elif msg == ".随机事件":
            random_event_info = self._get_random_event()
            if random_event_info:
                reply = "为你推荐一个随机事件:\n" + self._format_event_info(random_event_info)
            else:
                reply = "事件数据为空，无法随机选择事件。"
            ctx.add_return("reply", [reply])
            ctx.prevent_default()

        elif msg == ".随机悬念":
            random_suspense_info = self._get_random_suspense()
            if random_suspense_info:
                reply = "为你推荐一个随机悬念:\n" + self._format_suspense_info(random_suspense_info)
            else:
                reply = "悬念数据为空，无法随机选择悬念。"
            ctx.add_return("reply", [reply])
            ctx.prevent_default()

        elif msg.startswith(".查询事件"):
            event_name = msg[len(".查询事件"):].strip()
            if not event_name:
                reply = "请在 `.查询事件` 命令后输入要查询的事件名称，例如：`.查询事件 降龙节遇袭`"
            else:
                event_info = self._find_event_by_name(event_name)
                if event_info:
                    reply = self._format_event_info(event_info)
                else:
                    reply = f"未找到名为 \"{event_name}\" 的事件。"
            ctx.add_return("reply", [reply])
            ctx.prevent_default()
        elif msg == ".列出事件名单": # 可选：添加 .列出事件名单 命令 (如果需要列出所有事件)
            reply = self._format_event_list()
            ctx.add_return("reply", [reply])
            ctx.prevent_default()
        elif msg.startswith(".列出悬念名单"): # 修改 .列出悬念名单 命令，实现分页
            parts = msg.split() #  分割命令，例如 ".列出悬念名单 2"
            page_num = 1 # 默认页码为 1
            if len(parts) > 1 and parts[1].isdigit(): #  如果命令后面有数字，尝试解析页码
                page_num = int(parts[1])
                if page_num <= 0:
                    page_num = 1 # 页码不能小于 1

            page_replies = self._format_suspense_list(page_num) # 调用 _format_suspense_list 获取当前页内容 (返回的是列表)
            ctx.add_return("reply", page_replies) #  直接返回列表，插件平台会自动发送多条消息
            ctx.prevent_default()


        elif msg.startswith(".查询悬念"):
            suspense_name = msg[len(".查询悬念"):].strip()
            if not suspense_name:
                reply = "请在 `.查询悬念` 命令后输入要查询的悬念名称，例如：`.查询悬念 颅骨岛的珊娜萨余党`"
            else:
                suspense_info = self._find_suspense_by_name(suspense_name)
                if suspense_info:
                    reply = self._format_suspense_info(suspense_info)
                else:
                    reply = f"未找到名为 \"{suspense_name}\" 的悬念。"
            ctx.add_return("reply", [reply])
            ctx.prevent_default()


    def __del__(self):
        pass