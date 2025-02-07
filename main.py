from pkg.plugin.context import register, handler, BasePlugin, APIHost, EventContext
from pkg.plugin.events import PersonNormalMessageReceived, GroupNormalMessageReceived
import csv # 导入 csv 模块

@register(name="CharacterInfoPlugin", description="角色信息查询插件，从 CSV 文件读取角色数据", version="1.0", author="AI & KirifujiNagisa")
class CharacterInfoPlugin(BasePlugin):

    def __init__(self, host: APIHost):
        self.characters = [] # 用于存储从 CSV 文件读取的角色数据，列表 of 字典
        self.csv_file_path = "characters.csv" # CSV 文件路径，你可以根据实际情况修改

    async def initialize(self):
        """插件初始化时加载角色数据"""
        try:
            self.characters = self._load_character_data(self.csv_file_path)
            if not self.characters:
                self.logger.warning(f"CSV 文件 '{self.csv_file_path}' 为空或未找到角色数据。")
            else:
                self.logger.info(f"成功加载 {len(self.characters)} 个角色数据 from '{self.csv_file_path}'。")
        except FileNotFoundError:
            self.logger.error(f"CSV 文件 '{self.csv_file_path}' 未找到，请检查文件路径。角色信息查询功能将不可用。")
        except Exception as e:
            self.logger.exception(f"加载 CSV 文件 '{self.csv_file_path}' 时发生错误: {e}")


    def _load_character_data(self, csv_file_path):
        """从 CSV 文件加载角色数据，返回一个角色字典列表"""
        characters = []
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as csvfile: # 指定 UTF-8 编码，处理中文
                reader = csv.DictReader(csvfile) # 使用 DictReader，将每行数据转换为字典，header 作为 key
                for row in reader:
                    characters.append(row) # 将每行数据 (字典) 添加到角色列表中
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV 文件 '{csv_file_path}' 未找到")
        except Exception as e:
            raise Exception(f"读取 CSV 文件 '{csv_file_path}' 失败: {e}")
        return characters

    def _find_character_by_name(self, character_name):
        """根据角色名称查找角色信息，返回角色字典或 None"""
        for char_data in self.characters:
            if char_data.get('角色名称', '').strip() == character_name.strip(): # 忽略大小写和首尾空格进行匹配
                return char_data
        return None # 如果找不到匹配的角色，返回 None

    def _format_character_info(self, char_info):
        """格式化角色信息为易于阅读的字符串"""
        if not char_info:
            return "未找到该角色信息。"

        info_lines = [f"**{key}:** {value}" for key, value in char_info.items()] # 格式化每一项信息
        return "\n".join(info_lines) # 使用换行符连接所有信息行

    def _format_character_list(self):
        """格式化角色列表为易于阅读的字符串"""
        if not self.characters:
            return "角色列表为空。"
        character_names = [char['角色名称'] for char in self.characters] # 提取所有角色名称
        return "\n- " + "\n- ".join(character_names) # 使用换行符和 "- " 前缀列出角色名

    @handler(PersonNormalMessageReceived)
    async def person_normal_message_received(self, ctx: EventContext):
        await self._handle_message(ctx) # 私聊和群聊消息处理逻辑相同，提取到 _handle_message 方法

    @handler(GroupNormalMessageReceived)
    async def group_normal_message_received(self, ctx: EventContext):
        await self._handle_message(ctx) # 私聊和群聊消息处理逻辑相同，提取到 _handle_message 方法

    async def _handle_message(self, ctx: EventContext):
        """处理私聊和群聊消息的通用逻辑"""
        msg = ctx.event.text_message.strip() # 获取消息并去除首尾空格

        if msg.startswith(".查询角色"):
            character_name = msg[len(".查询角色"):].strip() # 提取角色名称，去除命令前缀和首尾空格
            if not character_name:
                reply = "请在 `.查询角色` 命令后输入要查询的角色名称，例如：`.查询角色 艾尔维·曼维尔`"
            else:
                char_info = self._find_character_by_name(character_name) # 查找角色信息
                reply = self._format_character_info(char_info) # 格式化角色信息
            ctx.add_return("reply", [reply])
            ctx.prevent_default()

        elif msg == ".列出角色名单":
            reply = self._format_character_list() # 获取格式化的角色列表
            ctx.add_return("reply", [reply])
            ctx.prevent_default()

    def __del__(self):
        pass