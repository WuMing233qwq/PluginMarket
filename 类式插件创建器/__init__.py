import json
import os
from tooldelta import Plugin, plugins, Print, Utils, constants


@plugins.add_plugin
class PluginCreator(Plugin):
    name = "类式插件创建器"

    def __init__(self, frame):
        super().__init__(frame)
        self.make_data_path()

    def on_def(self):
        self.frame.add_console_cmd_trigger(
            ["create", "创建插件"], None, "创建一个类式插件", self.create_plugin
        )

    def create_plugin(self, args: list[str]):
        pname = ""
        if len(args) == 1:
            pname = args[0]
        while 1:
            if pname := (pname or input(Print.fmt_info("请输入插件名: ")).strip()):
                plugin_dir_path = os.path.join(
                    constants.TOOLDELTA_PLUGIN_DIR,
                    constants.TOOLDELTA_CLASSIC_PLUGIN,
                    pname,
                )
                if os.path.isdir(plugin_dir_path):
                    Print.print_war("已有重命名插件")
                    pname = ""
                    continue
                break
            else:
                Print.print_war("插件名不能留空")
                pname = ""
        plugin_id = (
            input(Print.fmt_info("请输入插件的唯一标识ID(回车键则使用名字作为ID): "))
            or pname
        )
        while 1:
            pdesc = input(Print.fmt_info("请输入插件简介: "))
            if pdesc.strip():
                break
            Print.print_war("插件描述不能留空")
        while 1:
            latest_data = Utils.JsonIO.readFileFrom(self.name, "数据信息", {})
            if not latest_data:
                pauthor = input(
                    Print.fmt_info("请输入作者名 (下一次会自动填充): ")
                ).strip()
                if pauthor == "":
                    Print.print_war("作者名不能留空")
                    continue
                latest_data = {"author": pauthor}
                Utils.JsonIO.writeFileTo(self.name, "数据信息", latest_data)
                break
            else:
                pauthor = latest_data["author"]
                break
        ver_1, ver_2, ver_3 = (0, 0, 1)
        while 1:
            try:
                ver_1, ver_2, ver_3 = (
                    int(i)
                    for i in (
                        input(Print.fmt_info("请输入插件版本号(默认 0.0.1): "))
                        or "0.0.1"
                    ).split(".")
                )
                break
            except Exception:
                Print.print_err("错误的版本号格式, 应为 x.x.x")
        modules = {
            "0": ("Config", "配置文件的读取等"),
            "1": ("game_utils", "游戏内信息获取有关"),
            "2": ("Utils", "实用方法合集"),
            "3": ("Print", "格式化彩色输出"),
            "4": ("TYPE_CHECKING", "类型检查常量"),
        }
        Print.print_inf("\n".join(f"{k}: {v[0]} ({v[1]})" for k, v in modules.items()))
        resp = input(
            Print.fmt_info("需要用到以上哪些模块(输入连续数字, 如024, 回车键跳过): ")
        )
        extend_modules = [v[0] for k in resp if (v := modules.get(k))]
        if is_api_plugin := (
            input(
                Print.fmt_info("需要将你的插件作为 API 插件吗(§ay§r=是, §6其他§r=否): ")
            ).strip()
            == "y"
        ):
            api_name = ""
            while 1:
                if api_name := (
                    input(
                        Print.fmt_info("请输入插件的 API 名(回车则默认和插件名相同): ")
                    )
                    or pname
                ).strip():
                    break
        config_block = (
            "        CONFIG_STANDARD = {\n"
            '            "整数示例": int,\n'
            '            "小数示例": float,\n'
            '            "嵌套示例": {\n'
            '                "字符串示例": str,\n'
            "            }\n"
            "        }\n"
            "        CONFIG_DEFAULT = {\n"
            '            "整数示例": int,\n'
            '            "小数示例": float,\n'
            '            "嵌套示例": {\n'
            '                "字符串示例": str,\n'
            "            }\n"
            "        }\n"
        )
        plugin_body = (
            "from tooldelta import Plugin, plugins"
            + (f", {', '.join(i for i in extend_modules)}" if extend_modules else "")
            + "\n\n@plugins.add_plugin"
            + (f'_as_api("{api_name}")' if is_api_plugin else "")
            + "\n"
            "class NewPlugin(Plugin):\n"
            f'    name = "{pname}"\n'
            f'    author = "{pauthor}"\n'
            f"    version = ({ver_1}, {ver_2}, {ver_3})\n\n"
            "    def __init__(self, frame):\n"
            "        super().__init__(frame)\n"
            + (config_block if "Config" in extend_modules else "")
            + "\n"
            "    def on_def(self):\n"
            "        pass\n\n"
            "    def on_player_join(self, playername: str):\n"
            '        self.print(f"{playername} 进入游戏")\n\n'
            "    def on_player_leave(self, playername: str):\n"
            '        self.print(f"{playername} 退出游戏")\n\n'
            "    def on_player_message(self, playername: str, msg: str):\n"
            '        self.print(f"{playername} 说: {msg}")\n\n'
            "    def on_frame_exit(self, status_code: int, reason: str):\n"
            '        self.print(f"系统已退出 状态码={status_code} 原因={reason}")'
        )
        datafile_body = {
            "author": pauthor,
            "version": f"{ver_1}.{ver_2}.{ver_3}",
            "plugin-type": "classic",
            "description": pdesc,
            "pre-plugins": {},
            "plugin-id": plugin_id,
            "enabled": True,
        }
        os.makedirs(plugin_dir_path)
        with open(
            os.path.join(plugin_dir_path, "__init__.py"), "w", encoding="utf-8"
        ) as f:
            f.write(plugin_body)
        with open(
            os.path.join(plugin_dir_path, "datas.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(datafile_body, f, indent=2, ensure_ascii=False)
        Print.print_suc(f"插件创建完成, 位于 {plugin_dir_path}")
        Print.print_suc("输入 §breload §r可使其生效")
