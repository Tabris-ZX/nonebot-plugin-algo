import nonebot 

nonebot.init()

app = nonebot.get_asgi()

nonebot.load_plugin("nonebot_plugin_algo")

if __name__ == "__main__":
    nonebot.run()