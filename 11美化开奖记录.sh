#!/bin/sh

# 设置图标文件夹路径
ICON_FOLDER="./2"
ZODIAC_FOLDER="./生肖"

# 获取总行数
total_lines=$(wc -l < 1.txt)
current_line=0

# 修改显示进度的函数
show_progress() {
    local progress=$((current_line * 100 / total_lines))
    printf "\r处理进度: %d%%" $progress
}

# 函数：将数字转换为对应的图片文件名
number_to_image() {
    local num=$(echo $1 | sed 's/^0*//')  # 移除前导零
    local color
    if echo "$red_numbers" | grep -qw "$num"; then
        color="red"
    elif echo "$blue_numbers" | grep -qw "$num"; then
        color="blue"
    elif echo "$green_numbers" | grep -qw "$num"; then
        color="green"
    fi
    local special_class=""
    if [ "$2" = "special" ]; then
        special_class=" special"
    fi
    echo "<span class='ball $color$special_class'>$num</span>"
}

# 函数：将生肖转换为对应的图片文件名
zodiac_to_image() {
    local zodiac=$1
    local symbol
    local class_name="zodiac-3d"
    case $zodiac in
        鼠|龙|虎|兔|蛇|猴) class_name="zodiac-3d special" ;;
    esac
    case $zodiac in
        鼠) symbol="鼠" ;;
        牛) symbol="牛" ;;
        虎) symbol="虎" ;;
        兔) symbol="兔" ;;
        龙) symbol="龙" ;;
        蛇) symbol="蛇" ;;
        马) symbol="马" ;;
        羊) symbol="羊" ;;
        猴) symbol="猴" ;;
        鸡) symbol="鸡" ;;
        狗) symbol="狗" ;;
        猪) symbol="猪" ;;
        *) symbol="$zodiac" ;;
    esac
    echo "<span class='$class_name' title='$zodiac'>$symbol</span>"
}

# 函数：将大小单换为对应的图片件名
attribute_to_image() {
    local attribute=$1
    local class_name
    case $attribute in
        大) class_name="big" ;;
        小) class_name="small" ;;
        单) class_name="odd" ;;
        双) class_name="even" ;;
    esac
    echo "<span class='attribute $class_name'>$attribute</span>"
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

# 函数:将波色单双转换为对应的HTML span
wave_color_to_span() {
    local color=$1
    local class_name
    case $color in
        红单|红双) class_name="ball red" ;;
        蓝单|蓝双) class_name="ball blue" ;;
        绿单|绿双) class_name="ball green" ;;
    esac
    echo "<span class='$class_name'>$color</span>"
}

# 定十二生肖
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
    # 移除HTML标签和前导零
    num=$(echo "$num" | sed -E 's/<[^>]+>//g' | sed 's/^0*//')
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
        attributes="$attributes $(zodiac_to_image '猪')"
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

    # 颜色单双
    if echo $red_even | grep -wq "$num"; then
        attributes="$attributes $(wave_color_to_span '红双')"
    elif echo $red_odd | grep -wq "$num"; then
        attributes="$attributes $(wave_color_to_span '红单')"
    elif echo $blue_even | grep -wq "$num"; then
        attributes="$attributes $(wave_color_to_span '蓝双')"
    elif echo $blue_odd | grep -wq "$num"; then
        attributes="$attributes $(wave_color_to_span '蓝单')"
    elif echo $green_even | grep -wq "$num"; then
        attributes="$attributes $(wave_color_to_span '绿双')"
    elif echo $green_odd | grep -wq "$num"; then
        attributes="$attributes $(wave_color_to_span '绿单')"
    fi

    # 大小
    if echo $small_numbers | grep -wq "$num"; then
        attributes="$attributes $(attribute_to_image '小')"
    elif echo $big_numbers | grep -wq "$num"; then
        attributes="$attributes $(attribute_to_image '大')"
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

    # 新增格式1：第113期开奖结果：40-44-48-35-33-10 T06
    # 新增格式2第113期：40-44-48-35-33-10 T06
    if echo "$line" | grep -qE '第[0-9]+期(开奖结果：)?[0-9]+(-[0-9]+){5}[[:space:]]+T[0-9]+'; then
        period_number=$(echo "$line" | sed -E 's/第([0-9]+)期.*/\1/')
        period_date="24/$period_number"
        formatted_date="$period_date"
        numbers=""
        for num in $(echo "$line" | grep -oE '[0-9]+(-[0-9]+){5}' | tr '-' ' '); do
            numbers="$numbers$(number_to_image "$num") "
        done
        special_number_raw=$(echo "$line" | sed -E 's/.*T([0-9]+).*/\1/')
        special_number=$(number_to_image "$special_number_raw" "special")
        special_attributes=$(analyze_number "$special_number_raw")
    # 新增格式：香港110期开奖结果40-44-48-35-33-10 T06
    elif echo "$line" | grep -qE '香港[0-9]+期.*[0-9]+(-[0-9]+){5}.*T[0-9]+'; then
        period_number=$(echo "$line" | sed -E 's/.*港([0-9]+)期.*/\1/')
        period_date="24/$period_number"
        formatted_date="$period_date"
        numbers=""
        for num in $(echo "$line" | grep -oE '[0-9]+(-[0-9]+){5}' | tr '-' ' '); do
            numbers="$numbers$(number_to_image "$num") "
        done
        special_number_raw=$(echo "$line" | sed -E 's/.*T([0-9]+).*/\1/')
        special_number=$(number_to_image "$special_number_raw" "special")
        special_attributes=$(analyze_number "$special_number_raw")
    # 新的通用格式识别
    elif echo "$line" | grep -qE '第[0-9]+期.*[0-9]+([[:space:]]+[0-9]+){5}[[:space:]]+特码[[:space:]]+[0-9]+'; then
        period_number=$(echo "$line" | sed -E 's/.*第([0-9]+)期.*/\1/')
        period_date="24/$period_number"
        formatted_date="$period_date"
        numbers=$(echo "$line" | grep -oE '[0-9]+([[:space:]]+[0-9]+){5}' | tr ' ' '\n' | while read num; do echo -n "$(number_to_image "$num") "; done)
        special_number_raw=$(echo "$line" | sed -E 's/.*特码[[:space:]]+([0-9]+).*/\1/')
        special_number=$(number_to_image "$special_number_raw" "special")
        special_attributes=$(analyze_number "$special_number_raw")
    # 格式1：24/110 08/10/2024 10 16 24 32 37 40 17
    elif echo "$line" | grep -qE '^[0-9]+/[0-9]+[[:space:]]+[0-9]{2}/[0-9]{2}/[0-9]{4}[[:space:]]+([0-9]+[[:space:]]+){6}[0-9]+$'; then
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
        special_number_raw=$(echo "$line" | awk '{print $9}')
        special_attributes=$(analyze_number "$special_number_raw")
    # 格式3：112 10,16,24,32,37,40,17
    elif echo "$line" | grep -qE '^[0-9]+期[[:space:]]+[0-9]+(,[0-9]+){6}$'; then
        period_number=$(echo "$line" | sed -E 's/([0-9]+)期.*/\1/')
        period_date="24/$period_number"
        formatted_date="$period_date"
        numbers=""
        for num in $(echo "$line" | sed -E 's/[0-9]+期[[:space:]]+//; s/,[^,]*$//' | tr ',' '\n'); do
            numbers="$numbers$(number_to_image "$num") "
        done
        special_number=$(number_to_image "$(echo "$line" | sed -E 's/.*,([0-9]+)$/\1/')")
        special_number_raw=$(echo "$line" | sed -E 's/.*,([0-9]+)$/\1/')
        special_attributes=$(analyze_number "$special_number_raw")
    # 新增格式：24/108   02/10/2024
    elif echo "$line" | grep -qE '^[0-9]+/[0-9]+[[:space:]]+[0-9]{2}/[0-9]{2}/[0-9]{4}$'; then
        period_date=$(echo "$line" | awk '{print $1}')
        period_number=$(echo "$period_date" | cut -d'/' -f2)
        original_date=$(echo "$line" | awk '{print $2}')
        formatted_date=$(echo "$original_date" | awk -F'/' '{print $2"/"$1"/"$3}')
        return 2  # 返回特殊值表示需要继续读取后续行
    else
        return 1
    fi

    # 输出逻辑
    if [ -n "$special_number" ]; then
        special_attributes=$(analyze_number "$(echo "$special_number" | sed -E 's/.*>([0-9]+)<.*/\1/')")
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

# 在主循环开始前显示初始进度
printf "处理进度: 0%%"

# 在主循环之前添加这些变量
previous_line=""
is_waiting_for_numbers=false

# 修改主循环
while IFS= read -r line || [ -n "$line" ]; do
    current_line=$((current_line + 1))
    show_progress

    trimmed_line=$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    
    if [ -z "$trimmed_line" ]; then
        continue
    fi
    
    # 检查是否是跨行格式的第一行
    if echo "$trimmed_line" | grep -qE '香港[0-9]+期开奖结果$'; then
        previous_line="$trimmed_line"
        is_waiting_for_numbers=true
        continue
    fi
    
    # 如果是跨行格式的第二行，合并两行
    if $is_waiting_for_numbers; then
        if echo "$trimmed_line" | grep -qE '^[0-9]+(-[0-9]+){5}[[:space:]]+T[0-9]+$'; then
            trimmed_line="$previous_line $trimmed_line"
            is_waiting_for_numbers=false
        else
            is_waiting_for_numbers=false
        fi
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
            special_number_raw=$trimmed_line
            special_attributes=$(analyze_number "$special_number_raw")
        fi
        
        # 如果已经读取了7个数字,输出结果
        if [ $count -eq 7 ]; then
            # 如果有月份信息，添加到格式化日期
            if [ -n "$current_month" ] && [ -n "$current_year" ]; then
                formatted_date="$current_month $current_year $period_date"
            else
                formatted_date="$period_date"
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

# 循环结束后显示100%进度
printf "\r处理进度: 100%%\n"

# 修改 HTML 输出部分
{
    echo '<!DOCTYPE html>'
    echo '<html lang="zh-CN">'
    echo '<head>'
    echo '<meta charset="UTF-8">'
    echo '<title>六合彩结果</title>'
    echo '<style>'
    echo 'table {border-collapse: collapse; width: 100%; max-width: 800px; margin: 0 auto;}'
    echo 'th, td {border: 1px solid #ddd; padding: 4px; text-align: center;}'
    echo 'th {background-color: #f2f2f2;}'
    echo '.period {font-weight: bold;}'  # 期数加粗
    echo '.ball {display: inline-block; width: 28px; height: 28px; border-radius: 50%; text-align: center; line-height: 28px; font-weight: bold; margin: 0 1px;}'
    echo '.red {background-color: #ff0000; color: white;}'
    echo '.blue {background-color: #0000ff; color: white;}'
    echo '.green {background-color: #008000; color: white;}'
    echo '.special {border: 2px solid gold;}'
    echo '.attribute {display: inline-block; width: 28px; height: 28px; border-radius: 6px; text-align: center; line-height: 28px; font-weight: bold; margin: 0 1px; color: white;}'
    echo '.odd {background-color: #ff0000;}'
    echo '.even {background-color: #ffc0cb;}'
    echo '.big {background-color: #FF8C00;}' # 修改为黄丹色 (Dark Orange)
    echo '.small {background-color: #90ee90;}'
    echo '.zodiac-3d {
        display: inline-block;
        width: 32px;
        height: 32px;
        line-height: 32px;
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        color: #FFD700;  /* 金色字体 */
        background: linear-gradient(145deg, #4B0082, #8B008B);
        border-radius: 50%;
        box-shadow: 
            2px 2px 5px rgba(0,0,0,0.3),
            -2px -2px 5px rgba(255,255,255,0.1);
        text-shadow: 
            0 1px 0 #000,
            0 2px 0 #000;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
        margin: 0 4px;
    }
    .zodiac-3d.special {
        background: linear-gradient(145deg, #1E90FF, #4169E1);  /* 蓝色渐变背景 */
        color: #FFFFFF;  /* 白色字体 */
        text-shadow: 
            0 1px 0 #000,
            0 2px 0 #000,
            0 3px 3px rgba(0,0,0,0.3);
        box-shadow: 
            inset 0 0 10px rgba(255,255,255,0.5),
            0 5px 15px rgba(0,0,0,0.3);
        transform: translateY(-2px);
    }
    .zodiac-3d::before {
        content: "";
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, rgba(255,255,255,0) 70%);
        transform: rotate(45deg);
    }
    .zodiac-3d:hover {
        transform: translateY(-3px);
        box-shadow: 
            4px 4px 10px rgba(0,0,0,0.4),
            -4px -4px 10px rgba(255,255,255,0.2);
    }
    .zodiac-3d.special:hover {
        transform: translateY(-4px);
        box-shadow: 
            inset 0 0 15px rgba(255,255,255,0.7),
            0 8px 20px rgba(0,0,0,0.4);
    }
    .attribute {
        display: inline-block;
        width: 28px;
        height: 28px;
        border-radius: 6px;
        text-align: center;
        line-height: 28px;
        font-weight: bold;
        margin: 0 4px;
        color: white;
    }
    .attribute.even {
        background-color: #FF69B4;  /* 亮牡丹色 */
        color: white;  /* 保持字体颜色不变 */
    }
    .attribute-group {
        margin: 0 8px;
    }
    .ball.red, .ball.blue, .ball.green {
        display: inline-block;
        width: 40px;
        height: 28px;
        border-radius: 14px;
        text-align: center;
        line-height: 28px;
        font-weight: bold;
        color: white;
        margin: 0 2px;
    }
    .ball.red { background-color: #ff0000; }
    .ball.blue { background-color: #0000ff; }
    .ball.green { background-color: #008000; }
    '
    echo '</style>'
    echo '</head>'
    echo '<body>'
    echo '<table>'
    echo '<tr><th>期数</th><th>平码</th><th>特码</th><th>属性</th></tr>'
    sort -n -t'|' -k1 "$temp_file" | while IFS='|' read -r period_number period_date formatted_date numbers special_number special_attributes; do
        printf "<tr><td class='period'>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n" \
               "$period_number" "$numbers" "$special_number" "$special_attributes"
    done
    echo '</table>'
    echo '</body>'
    echo '</html>'
} > output.html

# 删除临时文件
rm "$temp_file"

echo "处理完成,结果已保存到output.html文件中。"