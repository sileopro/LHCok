#!/bin/sh

# 设置图标文件夹路径
ICON_FOLDER="./2"
ZODIAC_FOLDER="./生肖"

# 在文件开头添加以下变量
current_month=""
current_year=""
current_period=""

# 函数：将数字转换为对应的图片文件名
number_to_image() {
    local num=$(echo $1 | sed 's/^0*//')  # 移除前导零
    echo "<img src=\"${ICON_FOLDER}/a${num}.png\" alt=\"$1\" width=\"30\" height=\"30\">"
}

# 函数：将生肖转换为对应的图片文件名
zodiac_to_image() {
    local zodiac=$1
    local image_number
    case $zodiac in
        鼠) image_number=1 ;;
        牛) image_number=2 ;;
        虎) image_number=3 ;;
        兔) image_number=4 ;;
        龙) image_number=5 ;;
        蛇) image_number=6 ;;
        马) image_number=7 ;;
        羊) image_number=8 ;;
        猴) image_number=9 ;;
        鸡) image_number=10 ;;
        狗) image_number=11 ;;
        猪) image_number=12 ;;  # 直接使用中文字符
    esac
    echo "<img src=\"${ZODIAC_FOLDER}/o_a_${image_number}.png\" alt=\"$zodiac\" width=\"30\" height=\"30\">"
}

# 函数：将大小单双转换为对应的图片文件名
attribute_to_image() {
    local attribute=$1
    local image_name
    case $attribute in
        大) image_name="h070" ;;
        小) image_name="h071" ;;
        单) image_name="h122" ;;
        双) image_name="h123" ;;
    esac
    echo "<img src=\"${ZODIAC_FOLDER}/${image_name}.png\" alt=\"$attribute\" width=\"30\" height=\"30\">"
}

# 函数：将波色转换为对应的图片文件名
wave_color_to_image() {
    local color=$1
    local image_name
    case $color in
        红波) image_name="h062" ;;
        蓝波) image_name="h063" ;;
        绿波) image_name="h064" ;;
    esac
    echo "<img src=\"${ZODIAC_FOLDER}/${image_name}.png\" alt=\"$color\" width=\"30\" height=\"30\">"
}

# 定义十二生肖
zodiac_dragon="1 13 25 37 49"
zodiac_rabbit="2 14 26 38"
zodiac_tiger="3 15 27 39"
zodiac_ox="4 16 28 40"
zodiac_rat="5 17 29 41"
zodiac_pig="6 18 30 42"
zodiac_dog="7 19 31 43"
zodiac_rooster="8 20 32 44"
zodiac_monkey="9 21 33 45"
zodiac_sheep="10 22 34 46"
zodiac_horse="11 23 35 47"
zodiac_snake="12 24 36 48"

# 定义波色、合数单双、大小和颜色单双
red_numbers="1 2 7 8 12 13 18 19 23 24 29 30 34 35 40 45 46"
blue_numbers="3 4 9 10 14 15 20 25 26 31 36 37 41 42 47 48"
green_numbers="5 6 11 16 17 21 22 27 28 32 33 38 39 43 44 49"

odd_sum_numbers="1 3 5 7 9 11 13 15 17 19 21 23 25 27 29 31 33 35 37 39 41 43 45 47 49"
even_sum_numbers="2 4 6 8 10 12 14 16 18 20 22 24 26 28 30 32 34 36 38 40 42 44 46 48"

small_numbers="1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24"
big_numbers="25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49"

red_even="2 8 12 18 24 30 34 40 46"
red_odd="1 7 13 19 23 29 35 45"
blue_even="4 10 14 20 26 36 42 48"
blue_odd="3 9 15 25 31 37 41 47"
green_even="6 16 22 28 32 38 44"
green_odd="5 11 17 21 27 33 39 43 49"

# 分析函数
analyze_number() {
    local num=$1
    # 移除前导零
    num=$(echo $num | sed 's/^0*//')
    local attributes=""

    # 生肖
    if echo $zodiac_dragon | grep -wq "$num"; then
        attributes="$attributes $(zodiac_to_image '龙')"
    elif echo $zodiac_rabbit | grep -wq "$num"; then
        attributes="$attributes $(zodiac_to_image '兔')"
    elif echo $zodiac_tiger | grep -wq "$num"; then
        attributes="$attributes $(zodiac_to_image '虎')"
    elif echo $zodiac_ox | grep -wq "$num"; then
        attributes="$attributes $(zodiac_to_image '牛')"
    elif echo $zodiac_rat | grep -wq "$num"; then
        attributes="$attributes $(zodiac_to_image '鼠')"
    elif echo $zodiac_pig | grep -wq "$num"; then
        attributes="$attributes $(zodiac_to_image '猪')"  # 直接使用中文字符
    elif echo $zodiac_dog | grep -wq "$num"; then
        attributes="$attributes $(zodiac_to_image '狗')"
    elif echo $zodiac_rooster | grep -wq "$num"; then
        attributes="$attributes $(zodiac_to_image '鸡')"
    elif echo $zodiac_monkey | grep -wq "$num"; then
        attributes="$attributes $(zodiac_to_image '猴')"
    elif echo $zodiac_sheep | grep -wq "$num"; then
        attributes="$attributes $(zodiac_to_image '羊')"
    elif echo $zodiac_horse | grep -wq "$num"; then
        attributes="$attributes $(zodiac_to_image '马')"
    elif echo $zodiac_snake | grep -wq "$num"; then
        attributes="$attributes $(zodiac_to_image '蛇')"
    fi

    # 波色
    if echo $red_numbers | grep -wq "$num"; then
        attributes="$attributes $(wave_color_to_image '红波')"
    elif echo $blue_numbers | grep -wq "$num"; then
        attributes="$attributes $(wave_color_to_image '蓝波')"
    elif echo $green_numbers | grep -wq "$num"; then
        attributes="$attributes $(wave_color_to_image '绿波')"
    fi

    # 合数单双
    if echo $odd_sum_numbers | grep -wq "$num"; then
        attributes="$attributes $(attribute_to_image '单')"
    elif echo $even_sum_numbers | grep -wq "$num"; then
        attributes="$attributes $(attribute_to_image '双')"
    fi

    # 大小
    if echo $small_numbers | grep -wq "$num"; then
        attributes="$attributes $(attribute_to_image '小')"
    elif echo $big_numbers | grep -wq "$num"; then
        attributes="$attributes $(attribute_to_image '大')"
    fi

    # 颜色单双
    if echo $red_even | grep -wq "$num"; then
        attributes="$attributes 红双"
    elif echo $red_odd | grep -wq "$num"; then
        attributes="$attributes 红单"
    elif echo $blue_even | grep -wq "$num"; then
        attributes="$attributes 蓝双"
    elif echo $blue_odd | grep -wq "$num"; then
        attributes="$attributes 蓝单"
    elif echo $green_even | grep -wq "$num"; then
        attributes="$attributes 绿双"
    elif echo $green_odd | grep -wq "$num"; then
        attributes="$attributes 绿单"
    fi

    echo $attributes
}

# 函数：解析单行格式的开奖记录
parse_single_line() {
    local line="$1"
    local period_date period_number formatted_date numbers special_number

    # 处理月份信息
    if echo "$line" | grep -qE '^[一二三四五六七八九十]+月[[:space:]]+[0-9]{4}$'; then
        current_month=$(echo "$line" | awk '{print $1}')
        current_year=$(echo "$line" | awk '{print $2}')
        return 3  # 返回特殊值表示这是月份信息
    fi

    # 格式1：24/110 08/10/2024 10 16 24 32 37 40 17
    if echo "$line" | grep -qE '^[0-9]+/[0-9]+[[:space:]]+[0-9]{2}/[0-9]{2}/[0-9]{4}[[:space:]]+([0-9]+[[:space:]]+){6}[0-9]+$'; then
        period_date=$(echo "$line" | awk '{print $1}')
        period_number=$(echo "$period_date" | cut -d'/' -f2)
        original_date=$(echo "$line" | awk '{print $2}')
        formatted_date=$(echo "$original_date" | awk -F'/' '{print $2"/"$1"/"$3}')
        numbers=""
        for i in $(seq 3 8); do
            num=$(echo "$line" | awk "{print \$$i}")
            numbers="$numbers$(number_to_image "$num") "
        done
        special_number=$(number_to_image "$(echo "$line" | awk '{print $9}')")
    # 格式2：第112期：10 16 24 32 37 40 特码17
    elif echo "$line" | grep -qE '^第[0-9]+期：([0-9]+[[:space:]]+){6}特码[0-9]+$'; then
        period_number=$(echo "$line" | sed -E 's/第([0-9]+)期：.*/\1/')
        period_date="未知/$period_number"
        formatted_date="未知"
        numbers=""
        for num in $(echo "$line" | sed -E 's/第[0-9]+期：//; s/特码[0-9]+$//' | tr ' ' '\n'); do
            numbers="$numbers$(number_to_image "$num") "
        done
        special_number=$(number_to_image "$(echo "$line" | sed -E 's/.*特码([0-9]+)$/\1/')")
    # 格式3：112期 10,16,24,32,37,40,17
    elif echo "$line" | grep -qE '^[0-9]+期[[:space:]]+[0-9]+(,[0-9]+){6}$'; then
        period_number=$(echo "$line" | sed -E 's/([0-9]+)期.*/\1/')
        period_date="未/$period_number"
        formatted_date="未知"
        numbers=""
        for num in $(echo "$line" | sed -E 's/[0-9]+期[[:space:]]+//; s/,[^,]*$//' | tr ',' '\n'); do
            numbers="$numbers$(number_to_image "$num") "
        done
        special_number=$(number_to_image "$(echo "$line" | sed -E 's/.*,([0-9]+)$/\1/')")
    # 新增格式: 24/049 30/04/2024
    elif echo "$line" | grep -qE '^[0-9]+/[0-9]+[[:space:]]+[0-9]{2}/[0-9]{2}/[0-9]{4}$'; then
        period_date=$(echo "$line" | awk '{print $1}')
        period_number=$(echo "$period_date" | cut -d'/' -f2)
        original_date=$(echo "$line" | awk '{print $2}')
        formatted_date=$(echo "$original_date" | awk -F'/' '{print $2"/"$1"/"$3}')
        return 2  # 返回特殊值表示需要继续读取后续行
    else
        return 1
    fi

    # 在函数末尾，修改输出逻辑
    if [ -n "$special_number" ]; then
        special_attributes=$(analyze_number "$(echo "$special_number" | sed -E 's/.*alt="([0-9]+)".*/\1/')")
        # 如果有月份信息，添加到格式化日期
        if [ -n "$current_month" ] && [ -n "$current_year" ]; then
            formatted_date="$current_month $current_year $formatted_date"
        fi
        echo "$period_number|$period_date|$formatted_date|$numbers|$special_number|$special_attributes"
        return 0
    fi
    return 1
}

# 创建临时文件
temp_file=$(mktemp)

# 修改主循环部分
while IFS= read -r line || [ -n "$line" ]; do
    trimmed_line=$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    
    if [ -z "$trimmed_line" ]; then
        continue
    fi
    
    # 尝试解析单行格式
    result=$(parse_single_line "$trimmed_line")
    parse_result=$?
    
    if [ $parse_result -eq 0 ]; then
        echo "$result" >> "$temp_file"
        continue
    elif [ $parse_result -eq 2 ]; then
        # 新格式,需要读取后续行
        current_period=$(echo "$trimmed_line" | awk '{print $1}')
        period_date="$current_period"
        period_number=$(echo "$period_date" | cut -d'/' -f2)
        original_date=$(echo "$trimmed_line" | awk '{print $2}')
        formatted_date=$(echo "$original_date" | awk -F'/' '{print $2"/"$1"/"$3}')
        numbers=""
        count=0
        continue
    elif [ $parse_result -eq 3 ]; then
        # 更新当前月份和年份
        continue
    fi
    
    # 处理数字行
    if echo "$trimmed_line" | grep -qE '^[0-9]+$'; then
        count=$((count + 1))
        image_html=$(number_to_image "$trimmed_line")
        if [ $count -le 6 ]; then
            numbers="$numbers$image_html "
        else
            special_number="$image_html"
            special_attributes=$(analyze_number "$trimmed_line")
        fi
        
        # 如果已经读取了7个数字,输出结果
        if [ $count -eq 7 ]; then
            # 如果有月份信息，添加到格式化日期
            if [ -n "$current_month" ] && [ -n "$current_year" ]; then
                formatted_date="$current_month $current_year $formatted_date"
            fi
            printf "%s|%s|%s|%s|%s|%s\n" "$period_number" "$period_date" "$formatted_date" "$numbers" "$special_number" "$special_attributes" >> "$temp_file"
            numbers=""
            count=0
        fi
    fi
done < 1.txt

# 输出最后一组数据（如果有）
if [ -n "$period_date" ] && [ $count -eq 7 ]; then
    printf "%s|%s|%s|%s|%s|%s\n" "$period_number" "$period_date" "$formatted_date" "$numbers" "$special_number" "$special_attributes" >> "$temp_file"
fi

# 排��临时文件并生成HTML
{
    echo '<!DOCTYPE html>'
    echo '<html lang="zh-CN">'
    echo '<head>'
    echo '<meta charset="UTF-8">'
    echo '<title>六合彩结果</title>'
    echo '<style>'
    echo 'table {border-collapse: collapse;}'
    echo 'th, td {border: 1px solid black; padding: 5px;}'
    echo 'th {background-color: #f2f2f2;}'
    echo '</style>'
    echo '</head>'
    echo '<body>'
    echo '<table>'
    echo '<tr><th>期数</th><th>日期</th><th>平码</th><th>特码</th><th>属性</th></tr>'
    sort -n -t'|' -k1 "$temp_file" | while IFS='|' read -r period_number period_date formatted_date numbers special_number special_attributes; do
        printf "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n" "$period_number" "$period_date" "$numbers" "特码 $special_number" "$special_attributes"
    done
    echo '</table>'
    echo '</body>'
    echo '</html>'
} > output.html

# 删除临时文件
rm "$temp_file"

echo "处理完成,结果已保存到output.html文件中。"