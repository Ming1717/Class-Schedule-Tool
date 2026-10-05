import csv
from datetime import datetime, timedelta

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

# ========== 需求2 部分 ==========
def time_to_minutes(time_str):
    h, m = map(int, time_str.split(':'))
    return h * 60 + m

def minutes_to_time(minutes):
    h = minutes // 60
    m = minutes % 60
    return f"{h:02d}:{m:02d}"

def merge_time_ranges(ranges):
    if not ranges:
        return []
    sorted_ranges = sorted(ranges, key=lambda x: time_to_minutes(x[0]))
    merged = [sorted_ranges[0]]
    for current in sorted_ranges[1:]:
        last_start, last_end = merged[-1]
        curr_start, curr_end = current
        if time_to_minutes(curr_start) <= time_to_minutes(last_end):
            new_end = max(time_to_minutes(last_end), time_to_minutes(curr_end))
            merged[-1] = (last_start, minutes_to_time(new_end))
        else:
            merged.append(current)
    return merged

def calculate_free_time(courses, day, available_start="08:00", available_end="22:00"):
    day_courses = [c for c in courses if c["day"] == day]
    busy_ranges = [(c["start"], c["end"]) for c in day_courses]
    start_m = time_to_minutes(available_start)
    end_m = time_to_minutes(available_end)
    merged_busy = merge_time_ranges(busy_ranges)
    free_ranges = []
    current = start_m
    for busy_start, busy_end in merged_busy:
        b_start = time_to_minutes(busy_start)
        b_end = time_to_minutes(busy_end)
        if b_start > current:
            free_ranges.append((minutes_to_time(current), minutes_to_time(b_start)))
        current = max(current, b_end)
    if current < end_m:
        free_ranges.append((minutes_to_time(current), minutes_to_time(end_m)))
    return merge_time_ranges(free_ranges)

def print_free_time(courses):
    days_order = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    print("\n========== 本周空闲时段 ==========")
    for day in days_order:
        free_ranges = calculate_free_time(courses, day)
        if free_ranges:
            print(f"\n【{day}】")
            for start, end in free_ranges:
                print(f"  空闲：{start} - {end}")

# ========== 需求3 新增部分：找共同空闲时间 ==========
def intersect_time_ranges(ranges1, ranges2):
    """求两个空闲时间列表的交集"""
    result = []
    i, j = 0, 0
    while i < len(ranges1) and j < len(ranges2):
        start1, end1 = ranges1[i]
        start2, end2 = ranges2[j]
        
        # 求交集的开始和结束时间
        start = max(time_to_minutes(start1), time_to_minutes(start2))
        end = min(time_to_minutes(end1), time_to_minutes(end2))
        
        # 如果交集是有效的（开始时间早于结束时间），就加入结果
        if start < end:
            result.append((minutes_to_time(start), minutes_to_time(end)))
        
        # 谁先结束，就往后移动谁的指针
        if time_to_minutes(end1) < time_to_minutes(end2):
            i += 1
        else:
            j += 1
    return result

def find_common_free_time(courses1, courses2):
    """找两个人的共同空闲时间，按空闲时长从大到小排序"""
    days_order = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    common_times = []
    
    for day in days_order:
        free1 = calculate_free_time(courses1, day)
        free2 = calculate_free_time(courses2, day)
        
        # 求这一天的交集
        day_common = intersect_time_ranges(free1, free2)
        
        # 把这一天共同的空闲时间加上日期，方便排序
        for start, end in day_common:
            duration = time_to_minutes(end) - time_to_minutes(start)
            common_times.append({
                "day": day,
                "start": start,
                "end": end,
                "duration": duration
            })
    
    # 按 duration 从大到小排序
    common_times.sort(key=lambda x: x["duration"], reverse=True)
    return common_times

def print_common_free_time(courses1, courses2):
    """打印共同空闲时间"""
    common_times = find_common_free_time(courses1, courses2)
    print("\n========== 共同空闲时间（越长越靠前） ==========")
    if not common_times:
        print("没有找到共同空闲时间。")
    else:
        for item in common_times:
            print(f"  {item['day']}  {item['start']} - {item['end']}  (共 {item['duration']} 分钟)")

if __name__ == "__main__":
    print("=== 课表小工具 v0.3 ===")
    courses = read_from_csv("schedule.csv")
    if courses:
        print_schedule(courses)
        print_free_time(courses)
        
        # 模拟另一个人（比如小红）的课表，用来测试需求3
        print("\n（系统模拟：小红的课表）")
        courses_other = [
            {"name": "线性代数", "day": "周一", "start": "09:00", "end": "10:45"},
            {"name": "程序设计", "day": "周一", "start": "14:00", "end": "15:45"},
            {"name": "大学物理", "day": "周三", "start": "10:00", "end": "11:45"},
        ]
        print_schedule(courses_other)
        print_free_time(courses_other)
        
        # 计算共同空闲时间
        print_common_free_time(courses, courses_other)
    else:
        print("没有读取到课程数据。")