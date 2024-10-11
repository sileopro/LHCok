#!/bin/bash

# 运行Python脚本
python3 << END
import sys
import traceback
import re
from bs4 import BeautifulSoup
from collections import Counter
import random
import statistics
import itertools

def get_image_tag(number):
    return f'<img src="./2/a{number}.png" alt="{number}" width="30" height="30">'

def get_color_image_tag(color):
    color_map = {
        "红波": "h062",
        "蓝波": "h063",
        "绿波": "h064"
    }
    return f'<img src="./生肖/{color_map[color]}.png" alt="{color}" width="30" height="30">'

def get_zodiac_image_tag(zodiac):
    return f'<span class="zodiac-3d" title="{zodiac}">{zodiac}</span>'

def analyze_recent_periods(numbers, periods, zodiac_numbers, analyze_count=50):
    if not numbers:
        return {}, [], ("", 0), ("", 0, 0), (0, 0)
    recent_numbers = numbers[-analyze_count:]
    recent_periods = periods[-analyze_count:]
    recent_zodiac_numbers = zodiac_numbers[-analyze_count:]
    
    zodiac_map = {
        1: "鼠", 2: "牛", 3: "虎", 4: "兔", 5: "龙", 6: "蛇",
        7: "马", 8: "羊", 9: "猴", 10: "鸡", 11: "狗", 12: "猪",
        0: "未知"  # 添加一个 "未知" 类别
    }
    
    zodiac_patterns = {zodiac: [] for zodiac in zodiac_map.values()}
    
    for i, zodiac_num in enumerate(recent_zodiac_numbers):
        zodiac = zodiac_map.get(zodiac_num, "未知")
        zodiac_patterns[zodiac].append(recent_periods[i])
    
    zodiac_rules = {}
    for zodiac, appearances in zodiac_patterns.items():
        if appearances:
            zodiac_rules[zodiac] = f"出现期数: {', '.join(map(str, appearances))}"
    
    zodiac_counts = {zodiac: len(appearances) for zodiac, appearances in zodiac_patterns.items()}
    top_zodiacs = sorted(zodiac_counts.items(), key=lambda x: x[1], reverse=True)
    
    red = [1, 2, 7, 8, 12, 13, 18, 19, 23, 24, 29, 30, 34, 35, 40, 45, 46]
    blue = [3, 4, 9, 10, 14, 15, 20, 25, 26, 31, 36, 37, 41, 42, 47, 48]
    green = [5, 6, 11, 16, 17, 21, 22, 27, 28, 32, 33, 38, 39, 43, 44, 49]
    color_counts = {
        "红波": sum(1 for num in recent_numbers if num in red),
        "蓝波": sum(1 for num in recent_numbers if num in blue),
        "绿波": sum(1 for num in recent_numbers if num in green)
    }
    top_color = max(color_counts.items(), key=lambda x: x[1])
    
    big_count = sum(1 for num in recent_numbers if num > 24)
    small_count = analyze_count - big_count
    size_prediction = "小" if small_count > big_count else "大"
    
    return zodiac_rules, top_zodiacs, top_color, (size_prediction, big_count, small_count), (recent_periods[0], recent_periods[-1])

try:
    with open('output.html', 'r', encoding='utf-8') as file:
        html_content = file.read()

    print("Debug: HTML content:", file=sys.stderr)
    print(html_content[:500], file=sys.stderr)  # 打印前500个字符

    soup = BeautifulSoup(html_content, 'html.parser')

    print("\nDebug: Table rows:", file=sys.stderr)
    for i, row in enumerate(soup.find_all('tr')[:5]):  # 打印前5行
        print(f"Row {i}: {row}", file=sys.stderr)

    special_numbers = []
    periods = []
    zodiac_numbers = []
    for row in soup.find_all('tr')[1:]:
        cells = row.find_all('td')
        if len(cells) >= 5:
            period_cell = cells[0]
            special_number_cell = cells[3]
            zodiac_cell = cells[4]
            
            period = int(period_cell.text.strip().split('/')[-1])
            
            # 提取特码
            special_number_match = re.search(r'alt="(\d+)"', str(special_number_cell))
            if special_number_match:
                special_number = int(special_number_match.group(1))
            else:
                special_number_text = special_number_cell.text.strip()
                if special_number_text.isdigit():
                    special_number = int(special_number_text)
                else:
                    continue  # 如果无法提取特码，跳过这一行
            
            # 提取生肖编号（如果可用）
            zodiac_number = None
            zodiac_match = re.search(r'title="([^"]+)"', str(zodiac_cell))
            if zodiac_match:
                zodiac = zodiac_match.group(1)
                zodiac_map = {"鼠": 1, "牛": 2, "虎": 3, "兔": 4, "龙": 5, "蛇": 6,
                              "马": 7, "羊": 8, "猴": 9, "鸡": 10, "狗": 11, "猪": 12}
                zodiac_number = zodiac_map.get(zodiac)
            
            if special_number is not None:
                special_numbers.append(special_number)
                periods.append(period)
                zodiac_numbers.append(zodiac_number if zodiac_number is not None else 0)

    if not special_numbers:
        print("警告：没有找到有效的特码数据。请检查 output.html 文件的格式。", file=sys.stderr)
        sys.exit(1)

    special_numbers = [x for _, x in sorted(zip(periods, special_numbers))]
    periods.sort()

    number_counts = Counter(special_numbers)

    all_numbers = set(range(1, 50))
    not_appeared = all_numbers - set(special_numbers)
    last_appearance = {num: 0 for num in range(1, 50)}
    for i, num in enumerate(special_numbers):
        last_appearance[num] = i + 1
    
    not_appeared_with_gap = [(num, len(special_numbers) - last_appearance[num]) for num in not_appeared]
    not_appeared_sorted = sorted(not_appeared_with_gap, key=lambda x: x[1], reverse=True)

    average = statistics.mean(special_numbers)

    def predict_next_special_numbers(numbers, counts):
        recent_numbers = numbers[-20:]
        recent_counts = Counter(recent_numbers)
        least_common = sorted(recent_counts, key=recent_counts.get)[:3]
        if len(least_common) < 3:
            all_least_common = sorted(counts, key=counts.get)
            least_common.extend([num for num in all_least_common if num not in least_common])
            least_common = least_common[:3]
        return least_common

    next_predictions = predict_next_special_numbers(special_numbers, number_counts)

    def predict_zodiac(numbers):
        zodiac_map = {
            "龙": [1, 13, 25, 37, 49], 
            "兔": [2, 14, 26, 38], 
            "虎": [3, 15, 27, 39], 
            "牛": [4, 16, 28, 40], 
            "鼠": [5, 17, 29, 41], 
            "猪": [6, 18, 30, 42], 
            "狗": [7, 19, 31, 43], 
            "鸡": [8, 20, 32, 44], 
            "猴": [9, 21, 33, 45], 
            "羊": [10, 22, 34, 46], 
            "马": [11, 23, 35, 47], 
            "蛇": [12, 24, 36, 48]
        }
        zodiac_counts = {zodiac: sum(numbers.count(num) for num in nums) for zodiac, nums in zodiac_map.items()}
        return sorted(zodiac_counts, key=zodiac_counts.get, reverse=True)[:2]

    def predict_color(numbers):
        red = [1, 2, 7, 8, 12, 13, 18, 19, 23, 24, 29, 30, 34, 35, 40, 45, 46]
        blue = [3, 4, 9, 10, 14, 15, 20, 25, 26, 31, 36, 37, 41, 42, 47, 48]
        green = [5, 6, 11, 16, 17, 21, 22, 27, 28, 32, 33, 38, 39, 43, 44, 49]
        colors = {"红波": sum(numbers.count(num) for num in red),
                  "蓝波": sum(numbers.count(num) for num in blue),
                  "绿波": sum(numbers.count(num) for num in green)}
        predicted_color = max(colors, key=colors.get)
        if predicted_color == "红波":
            color_numbers = random.sample(red, min(3, len(red)))
        elif predicted_color == "蓝波":
            color_numbers = random.sample(blue, min(3, len(blue)))
        else:
            color_numbers = random.sample(green, min(3, len(green)))
        return predicted_color, color_numbers

    def predict_odd_even(numbers):
        odd = [1, 3, 5, 7, 9, 10, 12, 14, 16, 18, 21, 23, 25, 27, 29, 30, 32, 34, 36, 38, 41, 43, 45, 47, 49]
        even = [2, 4, 6, 8, 11, 13, 15, 17, 19, 20, 22, 24, 26, 28, 31, 33, 35, 37, 39, 40, 42, 44, 46, 48]
        odd_count = sum(1 for num in numbers if num in odd)
        even_count = len(numbers) - odd_count
        return "合数单" if odd_count > even_count else "合数双"

    def predict_big_small(numbers):
        small = sum(1 for num in numbers if num <= 24)
        big = len(numbers) - small
        return "大" if big > small else "小"

    zodiac_prediction = predict_zodiac(special_numbers)
    color_prediction, color_numbers = predict_color(special_numbers)
    odd_even_prediction = predict_odd_even(special_numbers)
    big_small_prediction = predict_big_small(special_numbers)

    def predict_color_odd_even(numbers, color):
        if color == "红波":
            odd = [1, 7, 13, 19, 23, 29, 35, 45]
            even = [2, 8, 12, 18, 24, 30, 34, 40, 46]
        elif color == "蓝波":
            odd = [3, 9, 15, 25, 31, 37, 41, 47]
            even = [4, 10, 14, 20, 26, 36, 42, 48]
        else:  # 绿波
            odd = [5, 11, 17, 21, 27, 33, 39, 43, 49]
            even = [6, 16, 22, 28, 32, 38, 44]

        odd_count = sum(numbers.count(num) for num in odd)
        even_count = sum(numbers.count(num) for num in even)

        return f"{color}单" if odd_count > even_count else f"{color}双"

    color_odd_even_prediction = predict_color_odd_even(special_numbers, color_prediction)
    color_odd_even_numbers = random.sample(color_numbers, min(3, len(color_numbers)))

    odd_numbers = [1, 3, 5, 7, 9, 10, 12, 14, 16, 18, 21, 23, 25, 27, 29, 30, 32, 34, 36, 38, 41, 43, 45, 47, 49]
    even_numbers = [2, 4, 6, 8, 11, 13, 15, 17, 19, 20, 22, 24, 26, 28, 31, 33, 35, 37, 39, 40, 42, 44, 46, 48]
    odd_even_numbers = random.sample(odd_numbers, 3) if odd_even_prediction == "合数单" else random.sample(even_numbers, 3)
    big_small_numbers = random.sample(range(25, 50), 3) if big_small_prediction == "大" else random.sample(range(1, 25), 3)
    color_odd_even_numbers = random.sample([1, 7, 13, 19, 23, 29, 35, 45], 3)  # 假设为红单

    last_period = soup.find_all('tr')[-1].find_all('td')[0].text.strip()
    next_period_number = int(last_period.split('/')[-1]) + 1
    next_period = f"{last_period.split('/')[0]}/{next_period_number:03d}"

    last_appearance = {num: 0 for num in range(1, 50)}
    for i, num in enumerate(special_numbers):
        last_appearance[num] = i + 1

    current_period = len(special_numbers)

    zodiac_rules_20, top_zodiacs_20, recent_color_20, recent_size_20, period_range_20 = analyze_recent_periods(special_numbers, periods, zodiac_numbers, analyze_count=20)
    zodiac_rules_50, top_zodiacs_50, recent_color_50, recent_size_50, period_range_50 = analyze_recent_periods(special_numbers, periods, zodiac_numbers, analyze_count=50)

    with open('fenxi.html', 'w', encoding='utf-8') as file:
        file.write('''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>六合彩分析结果</title>
    <style>
        body { font-family: Arial, sans-serif; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; vertical-align: top; }
        th { background-color: #f2f2f2; }
        img { vertical-align: middle; }
        .prediction-table td { padding: 10px; }
        .prediction-label { font-weight: bold; width: 100px; }
        .prediction-result { display: flex; align-items: center; flex-wrap: wrap; }
        .prediction-result span { min-width: 60px; }
        .zodiac-icon { width: 30px; }
        .recent-20 { 
            background-color: #87CEFA; 
            display: inline-block; 
            padding: 0 1px; 
            border-radius: 2px;
            margin: 0 1px;
        }
        .recent-50 { 
            background-color: #90EE90; 
            display: inline-block; 
            padding: 0 1px; 
            border-radius: 2px;
            margin: 0 1px;
        }
        .caption-20 {
            background-color: #87CEFA;
            padding: 2px 4px;
            border-radius: 4px;
        }
        .caption-50 {
            background-color: #90EE90;
            padding: 2px 4px;
            border-radius: 4px;
        }
        .analysis-title {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 4px;
            color: black;
        }
        .caption-next {
            background-color: #FFB6C1;
            padding: 2px 4px;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <h1>香港六合彩分析结果</h1>
    ''')
        
        file.write("<h2> 特码出现次数统计未出现的特码</h2>")
        file.write("<p>特码次数 (间隔期数):</p>")
        
        sorted_numbers = sorted(range(1, 50), key=lambda x: last_appearance[x])
        
        count_groups = {}
        for num in sorted_numbers:
            if num in number_counts:
                count = number_counts[num]
                if count not in count_groups:
                    count_groups[count] = []
                count_groups[count].append((num, current_period - last_appearance[num]))
        
        for count, nums in sorted(count_groups.items(), reverse=True):
            nums_sorted = sorted(nums, key=lambda x: x[1], reverse=True)
            file.write(f"<p>{count}次({len(nums)}码): ")
            file.write(' '.join([f"{get_image_tag(num)} ({gap}期)" for num, gap in nums_sorted]))
            file.write("</p>")
        
        file.write(f"<p>未出现的特码 ({len(not_appeared)}个): ")
        file.write(' '.join([f"{get_image_tag(num)}" for num in sorted(not_appeared)]))
        file.write("</p>")
        
        file.write("<p>&nbsp;</p>")
        file.write("<p>&nbsp;</p>")

        file.write("<div class='zodiac-analysis'>")
        file.write(f"<table class='prediction-table'>")
        file.write(f"<tr><th>生肖</th><th>规律<span style='display: inline-block; width: 6em;'></span><span class='caption-50'>近50期：（{period_range_50[0]:03d}期~{period_range_50[1]:03d}期）</span><span style='display: inline-block; width: 3em;'></span><span class='caption-20'>近20期：（{period_range_20[0]:03d}期~{period_range_20[1]:03d}期）</span></th></tr>")
        for zodiac, rule in zodiac_rules_50.items():
            file.write(f"<tr><td class='zodiac-icon'>{get_zodiac_image_tag(zodiac)}</td><td class='prediction-result'>")
            periods = rule.split(': ')[1].split(', ')
            formatted_periods = []
            for period in periods:
                if int(period) >= period_range_20[0]:
                    formatted_periods.append(f"<span class='recent-20'>{period}</span>")
                else:
                    formatted_periods.append(f"<span class='recent-50'>{period}</span>")
            file.write('; '.join(formatted_periods))
            file.write("</td></tr>")
        file.write("</table>")
        file.write("</div>")

        file.write("<p>&nbsp;</p>")
        file.write("<p>&nbsp;</p>")
        file.write("<h2><span class='analysis-title caption-50'>近50期规律分析</span></h2>")
        file.write("<table class='prediction-table'>")
        file.write("<tr><th>类型</th><th>分析结果</th></tr>")
        file.write("<tr><td class='prediction-label'>十二生肖</td><td class='prediction-result'>")
        grouped_zodiacs_50 = {}
        for zodiac, count in top_zodiacs_50:
            if count not in grouped_zodiacs_50:
                grouped_zodiacs_50[count] = []
            grouped_zodiacs_50[count].append(zodiac)

        for count, zodiacs in sorted(grouped_zodiacs_50.items(), reverse=True):
            file.write(f'【 {count}次：')
            file.write(' '.join([get_zodiac_image_tag(zodiac) for zodiac in zodiacs]))
            file.write(' 】 ')

        file.write("</td></tr>")
        file.write(f"<tr><td class='prediction-label'>波色</td><td class='prediction-result'>{get_color_image_tag(recent_color_50[0])} ({recent_color_50[1]}次)</td></tr>")
        file.write(f"<tr><td class='prediction-label'>大小</td><td class='prediction-result'>{recent_size_50[0]} ({recent_size_50[1] if recent_size_50[0] == '大' else recent_size_50[2]}次)</td></tr>")
        file.write("</table>")

        file.write("<p>&nbsp;</p>")
        file.write("<p>&nbsp;</p>")
        file.write("<h2><span class='analysis-title caption-20'>近20期规律分析</span></h2>")
        file.write("<table class='prediction-table'>")
        file.write("<tr><th>类型</th><th>分析结果</th></tr>")
        file.write("<tr><td class='prediction-label'>十二生肖</td><td class='prediction-result'>")
        grouped_zodiacs_20 = {}
        for zodiac, count in top_zodiacs_20:
            if count not in grouped_zodiacs_20:
                grouped_zodiacs_20[count] = []
            grouped_zodiacs_20[count].append(zodiac)

        for count, zodiacs in sorted(grouped_zodiacs_20.items(), reverse=True):
            file.write(f'【 {count}次：')
            file.write(' '.join([get_zodiac_image_tag(zodiac) for zodiac in zodiacs]))
            file.write(' 】 ')

        file.write("</td></tr>")
        file.write(f"<tr><td class='prediction-label'>波色</td><td class='prediction-result'>{get_color_image_tag(recent_color_20[0])} ({recent_color_20[1]}次)</td></tr>")
        file.write(f"<tr><td class='prediction-label'>大小</td><td class='prediction-result'>{recent_size_20[0]} ({recent_size_20[1] if recent_size_20[0] == '大' else recent_size_20[2]}次)</td></tr>")
        file.write("</table>")

        file.write("<p>&nbsp;</p>")
        file.write("<p>&nbsp;</p>")

        file.write(f"<h2><span class='analysis-title caption-next'>下一期：第{next_period_number:03d}期预测（祝君中奖）</span></h2>")
        file.write("<p><em>注意：以下预测基于历史数据和近期20期的开奖规律进行统计分析，仅供参考。</em></p>")
        file.write("<table class='prediction-table'>")
        file.write("<tr><th>类型</th><th>预测结果</th></tr>")
        file.write(f"<tr><td class='prediction-label'>特码</td><td class='prediction-result'>{' '.join([get_image_tag(num) for num in next_predictions])}</td></tr>")
        file.write(f"<tr><td class='prediction-label'>特肖</td><td class='prediction-result'>{' '.join([get_zodiac_image_tag(zodiac) for zodiac in zodiac_prediction[:2]])}</td></tr>")
        file.write(f"<tr><td class='prediction-label'>波色</td><td class='prediction-result'>{get_color_image_tag(color_prediction)} {' '.join([get_image_tag(num) for num in color_numbers])}</td></tr>")
        file.write(f"<tr><td class='prediction-label'>合数单双</td><td class='prediction-result'><span>{odd_even_prediction}:</span> {' '.join([get_image_tag(num) for num in odd_even_numbers])}</td></tr>")
        file.write(f"<tr><td class='prediction-label'>大小</td><td class='prediction-result'><span>{big_small_prediction}:</span> {' '.join([get_image_tag(num) for num in big_small_numbers])}</td></tr>")
        file.write(f"<tr><td class='prediction-label'>波色单双</td><td class='prediction-result'><span>{color_odd_even_prediction}:</span> {' '.join([get_image_tag(num) for num in color_odd_even_numbers])}</td></tr>")
        file.write("</table>")
        
        file.write('''
    <p><strong>免责声明:</strong> 这些预测是基于历史数据和近期开奖规律的简单统计分析,
    不能保证准确性。六合彩的结果是随机的,无法准确预测。请理性对待，切勿沉迷赌博。</p>
</body>
</html>
        ''')

    print("\n分析结果已保存到fenxi.html文件中。")
except Exception as e:
    print(f"发生错误: {e}", file=sys.stderr)
    print("错误详情:", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
END

echo "分析完成,结果已保存到fenxi.html文件中。"