class Mapper:
    # 洛谷难度等级名称映射
    luogu_difficulty_names: dict = {
        -1: "暂未评级",
        1: "入门",
        2: "普及-",
        3: "普及/提高-",
        4: "普及+/提高",
        5: "提高+/省选",
        6: "省选/NOI-",
        7: "NOI/CTSC",
    }

    # 洛谷用户名颜色
    luogu_name_color: dict = {
        "Gray": "#bbbbbb",
        "Blue": "#0e90d2",
        "Green": "#5eb95e",
        "Orange": "#e67e22",
        "Red": "#e74c3c",
        "Purple": "#9d3dcf",
        "Cheater": "#ad8b00",
    }

    #题目颜色映射
    luogu_problem_level_color: list[str] = [
        
            "#f44336",  # 1 Red
            "#ff9800",  # 2 Orange
            "#ffeb3b",  # 3 Yellow
            "#4caf50",  # 4 Green
            "#2196f3",  # 5 Blue
            "#9c27b0",  # 6 Purple
            "#212121",  # 7 Black
            "#9e9e9e",  # -1 Gray
        ]

    # 奖项颜色映射
    luogu_prize_color: dict = {
        "first": "#ffd700",    # 一等奖/金牌 - 黄色
        "second": "#ffffff",   # 二等奖/银牌 - 白色
        "third": "#cd7f32",    # 三等奖/铜牌 - 棕色
        "other": "#888888",    # 其他 - 灰色
    }