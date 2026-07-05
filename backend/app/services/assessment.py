"""Interest assessment service."""
import math

# Assessment questions
QUESTIONS = [
    {
        "id": 1,
        "question": "你最喜欢的学科类型是？",
        "options": [
            {"label": "数理化生等理科", "scores": {"07": 10, "08": 7, "10": 5}},
            {"label": "语文英语历史等文科", "scores": {"05": 10, "03": 7, "06": 7, "13": 5}},
            {"label": "编程和计算机", "scores": {"08": 10, "07": 5}},
            {"label": "都差不多", "scores": {}},
        ],
    },
    {
        "id": 2,
        "question": "你更倾向于哪种工作方式？",
        "options": [
            {"label": "独立研究和分析", "scores": {"07": 8, "02": 5}},
            {"label": "团队协作和沟通", "scores": {"12": 8, "03": 5, "05": 5}},
            {"label": "动手操作和实践", "scores": {"08": 8, "10": 5, "09": 5}},
            {"label": "创意表达和设计", "scores": {"13": 8, "05": 5}},
        ],
    },
    {
        "id": 3,
        "question": "你理想的职业环境是？",
        "options": [
            {"label": "互联网/科技公司", "scores": {"08": 10, "07": 5}},
            {"label": "医院/医疗机构", "scores": {"10": 10, "07": 5}},
            {"label": "学校/教育机构", "scores": {"04": 10, "05": 5}},
            {"label": "企业/金融机构", "scores": {"02": 10, "12": 5}},
        ],
    },
    {
        "id": 4,
        "question": "面对问题时你习惯于？",
        "options": [
            {"label": "用数据和逻辑分析", "scores": {"07": 8, "08": 5, "02": 5}},
            {"label": "凭经验和直觉判断", "scores": {"12": 5, "03": 5}},
            {"label": "与他人讨论交流", "scores": {"03": 5, "04": 5, "05": 5}},
            {"label": "动手尝试解决", "scores": {"08": 8, "09": 5, "10": 5}},
        ],
    },
    {
        "id": 5,
        "question": "你对哪种活动最感兴趣？",
        "options": [
            {"label": "做实验或研究", "scores": {"07": 8, "09": 5, "10": 5}},
            {"label": "创作或写作", "scores": {"05": 8, "13": 5}},
            {"label": "组织活动或管理", "scores": {"12": 8, "03": 5}},
            {"label": "帮助他人或服务社会", "scores": {"03": 5, "04": 5, "10": 5}},
        ],
    },
    {
        "id": 6,
        "question": "你对哪类新闻最关注？",
        "options": [
            {"label": "科技数码类", "scores": {"08": 10, "07": 5}},
            {"label": "财经商业类", "scores": {"02": 10, "12": 5}},
            {"label": "文化教育类", "scores": {"04": 8, "05": 5, "06": 5}},
            {"label": "社会民生类", "scores": {"03": 5, "12": 5}},
        ],
    },
    {
        "id": 7,
        "question": "你更看重工作的？",
        "options": [
            {"label": "薪资待遇和发展空间", "scores": {"08": 5, "02": 5}},
            {"label": "稳定性和工作生活平衡", "scores": {"04": 5, "12": 5}},
            {"label": "社会价值和意义感", "scores": {"10": 5, "03": 5, "04": 5}},
            {"label": "兴趣匹配和个人成长", "scores": {"13": 5, "05": 5}},
        ],
    },
    {
        "id": 8,
        "question": "高中时你最擅长的科目是？",
        "options": [
            {"label": "数学/物理", "scores": {"08": 8, "07": 8}},
            {"label": "化学/生物", "scores": {"10": 8, "09": 5, "07": 5}},
            {"label": "语文/英语", "scores": {"05": 8, "04": 5, "03": 5}},
            {"label": "政治/历史/地理", "scores": {"03": 8, "06": 5, "02": 5}},
        ],
    },
    {
        "id": 9,
        "question": "如果可以选一个课外学习方向，你会选？",
        "options": [
            {"label": "编程/AI/机器人", "scores": {"08": 10, "07": 5}},
            {"label": "金融投资/商业管理", "scores": {"02": 10, "12": 5}},
            {"label": "心理学/社会学", "scores": {"04": 5, "03": 5}},
            {"label": "设计/影视/音乐", "scores": {"13": 10, "05": 5}},
        ],
    },
    {
        "id": 10,
        "question": "你希望大学期间获得什么？",
        "options": [
            {"label": "扎实的专业技能", "scores": {"08": 5, "10": 5, "07": 5}},
            {"label": "广阔的人脉和视野", "scores": {"02": 5, "12": 5}},
            {"label": "综合素质的提升", "scores": {"03": 5, "05": 5, "04": 5}},
            {"label": "创新创业的能力", "scores": {"08": 5, "02": 5, "12": 5}},
        ],
    },
]

# Map category codes to names
CATEGORY_NAMES = {
    "01": "哲学", "02": "经济学", "03": "法学", "04": "教育学",
    "05": "文学", "06": "历史学", "07": "理学", "08": "工学",
    "09": "农学", "10": "医学", "12": "管理学", "13": "艺术学",
}


def evaluate_assessment(answers: list[int]) -> dict:
    """
    Evaluate the interest assessment answers.
    answers: list of selected option indices (0-3) for each question (1-10).
    Returns sorted category recommendations.
    """
    if len(answers) != len(QUESTIONS):
        return {"error": f"Expected {len(QUESTIONS)} answers, got {len(answers)}"}

    scores = {code: 0.0 for code in CATEGORY_NAMES}

    for q_idx, option_idx in enumerate(answers):
        question = QUESTIONS[q_idx]
        if option_idx < 0 or option_idx >= len(question["options"]):
            continue
        option = question["options"][option_idx]
        for cat_code, pts in option["scores"].items():
            scores[cat_code] += pts

    # Normalize to 0-100 scale
    max_score = max(scores.values()) if scores else 1
    if max_score > 0:
        scores = {k: round(v / max_score * 100, 1) for k, v in scores.items()}

    # Sort by score desc
    sorted_cats = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_categories = [
        {"code": code, "name": CATEGORY_NAMES.get(code, code), "score": sc}
        for code, sc in sorted_cats[:5]
    ]

    return {
        "scores": {CATEGORY_NAMES.get(k, k): v for k, v in scores.items()},
        "top_categories": top_categories,
        "primary_category": top_categories[0] if top_categories else None,
    }
