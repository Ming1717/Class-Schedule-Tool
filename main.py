import csv

def read_from_csv(filename):
    """从 CSV 文件读取课表"""
    courses = []
    try:
        with open(filename, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                courses.append({
                    "name": row["课程名"],
                    "day": row["星期几"],
                    "start": row["开始时间"],
                    "end": row["结束时间"]
                })
    except FileNotFoundError:
        print(f"错误：找不到文件 {filename}")
    return courses

def print_schedule(courses):
    """按周一到周日打印课表"""
    days_order = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    print("\n========== 本周课表 ==========")
    for day in days_order:
        day_courses = [c for c in courses if c["day"] == day]
        if day_courses:
            print(f"\n【{day}】")
            for c in day_courses:
                print(f"  {c['start']}-{c['end']}  {c['name']}")

if __name__ == "__main__":
    print("=== 课表小工具 v0.1 ===")
    courses = read_from_csv("schedule.csv")
    if courses:
        print_schedule(courses)
    else:
        print("没有读取到课程数据。")