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

# ========== 需求2 新增部分 ==========

def time_to_minutes(time_str):
    """把 '08:00' 转换成从0点开始的分钟数，比如 480"""
    h, m = map(int, time_str.split(':'))
    return h * 60 + m

def minutes_to_time(minutes):
    """把分钟数转换回 '08:00' 格式"""
    h = minutes // 60
    m = minutes % 60
    return f"{h:02d}:{m:02d}"

def merge_time_ranges(ranges):
    """
    合并连续或重叠的时间段。
    比如输入 [('09:00','09:45'), ('09:55','10:40'), ('10:50','11:30')]
    如果它们有交集或者连续（间隔很小），就合并成一段
    """
    if not ranges:
        return []
    
    # 按开始时间排序
    sorted_ranges = sorted(ranges, key=lambda x: time_to_minutes(x[0]))
    merged = [sorted_ranges[0]]
    
    for current in sorted_ranges[1:]:
        last_start, last_end = merged[-1]
        curr_start, curr_end = current
        
        # 如果当前的时间段的开始时间 <= 上一个时间段的结束时间（说明重叠或连续），就合并
        if time_to_minutes(curr_start) <= time_to_minutes(last_end):
            # 合并：结束时间取更晚的那个
            new_end = max(time_to_minutes(last_end), time_to_minutes(curr_end))
            merged[-1] = (last_start, minutes_to_time(new_end))
        else:
            merged.append(current)
            
    return merged

def calculate_free_time(courses, day, available_start="08:00", available_end="22:00"):
    """计算某一天的空闲时间段"""
    # 1. 找出当天的所有课程
    day_courses = [c for c in courses if c["day"] == day]
    
    # 2. 把课程时间转换成区间列表 [(开始, 结束), ...]
    busy_ranges = [(c["start"], c["end"]) for c in day_courses]
    
    # 3. 加上每天可用时间的边界
    start_m = time_to_minutes(available_start)
    end_m = time_to_minutes(available_end)
    
    # 4. 合并有冲突的课程时间（防止出现上课时间重叠）
    merged_busy = merge_time_ranges(busy_ranges)
    
    # 5. 计算空闲时间
    free_ranges = []
    current = start_m
    
    for busy_start, busy_end in merged_busy:
        b_start = time_to_minutes(busy_start)
        b_end = time_to_minutes(busy_end)
        
        # 如果课程开始时间 晚于 当前空闲开始时间，说明中间有一段空闲
        if b_start > current:
            free_ranges.append((minutes_to_time(current), minutes_to_time(b_start)))
        
        # 更新当前时间到课程结束时间
        current = max(current, b_end)
    
    # 6. 检查最后一段：课程结束后到晚上22:00之间有没有空闲
    if current < end_m:
        free_ranges.append((minutes_to_time(current), minutes_to_time(end_m)))
    
    # 7. 再次合并，确保没有碎片（比如 09:00-09:45 和 09:55-10:40 如果中间只隔了10分钟，根据题目要求要合并）
    return merge_time_ranges(free_ranges)

def print_free_time(courses):
    """打印每天的空闲时间"""
    days_order = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    print("\n========== 本周空闲时段 ==========")
    for day in days_order:
        free_ranges = calculate_free_time(courses, day)
        if free_ranges:
            print(f"\n【{day}】")
            for start, end in free_ranges:
                print(f"  空闲：{start} - {end}")

if __name__ == "__main__":
    print("=== 课表小工具 v0.2 ===")
    courses = read_from_csv("schedule.csv")
    if courses:
        print_schedule(courses)
        print_free_time(courses)
    else:
        print("没有读取到课程数据。")