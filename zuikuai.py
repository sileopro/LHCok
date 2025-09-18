# 支持2种格式 openCode 和  K  格式获取与解析
# json文件 直接从K格式API原始保存， openCode 解析保存为K格式
# 格式一：{"k":"101,21,33,32,22,28,14,25,102,09,18,四,21:30:00,2022","t":"1000","tool":"#492130#com","url":"","lhc":"","ok":"0"}
# 格式二：[{"expect":"2025101","openTime":"2025-09-16 21:32:32","type":"9","openCode":"21,33,32,22,28,14,25",

import requests
import json
import time
import re
import os
import random
from datetime import datetime, timedelta
import logging
import sys

# 配置日志
log_file = os.path.abspath("lottery.log")
SEPARATOR = "================= 日志内容结束 =================\n"
# 保留最近5次运行日志
if os.path.exists(log_file):
    with open(log_file, "r", encoding="utf-8") as f:
        content = f.read()
    blocks = content.split(SEPARATOR)
    # 去除空块
    blocks = [b for b in blocks if b.strip()]
    # 日志只保留最后5次运行
    if len(blocks) > 5:
        content = SEPARATOR.join(blocks[-5:]) + SEPARATOR
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(content)
else:
    with open(log_file, "w", encoding="utf-8") as f:
        pass

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# API配置
API_CONFIGS = {
    'hk': {  # 港彩
        'main': 'https://mnashd213asdhgask.amsndgbaidu.com/asmdasda/xgkj.json',
        'backup': [
            'https://macaumarksix.com/api/hkjc.com',
            'https://154.198.233.78:6777/kj/caiji/hkkj.js',
            'https://154.81.36.17:8335/kj/caiji/hkkj.js',
            'https://154.81.36.8:5935/kj/caiji/hkkj.js',
            'https://154.81.36.18:8925/kj/caiji/hkkj.js',
            'https://156.225.94.42:7625/kj/caiji/hkkj.js',
            'https://156.225.89.155:6825/kj/caiji/hkkj.js',
            'https://156.225.94.15:5395/kj/caiji/hkkj.js',
            'https://156.225.94.25:7395/kj/caiji/hkkj.js',
            'https://156.225.94.30:2255/kj/caiji/hkkj.js',
            'https://156.225.89.149:2285/kj/caiji/hkkj.js',
            'https://156.225.94.47:6523/kj/caiji/hkkj.js',
            'https://156.225.89.140:8255/kj/caiji/hkkj.js',
            'https://156.225.89.144:5576/kj/caiji/hkkj.js',
            'https://45.221.97.29:8775/kj/caiji/hkkj.js',
            'https://45.221.97.23:6165/kj/caiji/hkkj.js',
            'https://156.225.94.20:3335/kj/caiji/hkkj.js',
            'https://kjkj.kj88889.com/bmjg.js',
            'https://001033.com/kj/js/xgjs.asp'
                 
        ]
    },
    'xam': {  # 新澳
        'main': 'https://macaumarksix.com/api/macaujc2.com',
        'backup': [
            'https://mnashd213asdhgask.amsndgbaidu.com/asmdasda/amksj.json',
            'https://154.198.233.78:6777/kj/caiji/amkj.js',
            'https://154.81.36.17:8335/kj/caiji/amkj.js',
            'https://154.81.36.8:5935/kj/caiji/amkj.js',
            'https://154.81.36.18:8925/kj/caiji/amkj.js',
            'https://156.225.94.42:7625/kj/caiji/amkj.js',
            'https://156.225.89.155:6825/kj/caiji/amkj.js',
            'https://156.225.94.15:5395/kj/caiji/amkj.js',
            'https://156.225.94.25:7395/kj/caiji/amkj.js',
            'https://156.225.94.30:2255/kj/caiji/amkj.js',
            'https://156.225.89.149:2285/kj/caiji/amkj.js',
            'https://156.225.94.47:6523/kj/caiji/amkj.js',
            'https://156.225.89.140:8255/kj/caiji/amkj.js',
            'https://156.225.89.144:5576/kj/caiji/amkj.js',
            'https://45.221.97.29:8775/kj/caiji/amkj.js',
            'https://45.221.97.23:6165/kj/caiji/amkj.js',
            'https://156.225.94.20:3335/kj/caiji/amkj.js', 
            'https://001033.com/kj/js/amjs.asp'
        ]
    },
    'lam': {  # 老澳
        'main': 'https://49xr.cc/data/tw.js',
        'backup': [
            'https://005679.com/2chajian/bmjg.js'
        ]
    },
    'tc': {  # 台彩
        'main': 'https://49xr.cc/data/xjp.js',
        'backup': [
            'https://api.493210.com/am.js'
        ]
    }
}

# 彩票名称映射
LOTTERY_NAMES = {
    'hk': '港彩',
    'xam': '新澳',
    'lam': '老澳',
    'tc': '快乐8'
}

# 生肖映射表（如果API不返回生肖信息）
ZODIAC_MAPPING = {
    '01': '鼠', '02': '牛', '03': '虎', '04': '兔', '05': '龙', '06': '蛇',
    '07': '马', '08': '羊', '09': '猴', '10': '鸡', '11': '狗', '12': '猪',
    '13': '鼠', '14': '牛', '15': '虎', '16': '兔', '17': '龙', '18': '蛇',
    '19': '马', '20': '羊', '21': '猴', '22': '鸡', '23': '狗', '24': '猪',
    '25': '鼠', '26': '牛', '27': '虎', '28': '兔', '29': '龙', '30': '蛇',
    '31': '马', '32': '羊', '33': '猴', '34': '鸡', '35': '狗', '36': '猪',
    '37': '鼠', '38': '牛', '39': '虎', '40': '兔', '41': '龙', '42': '蛇',
    '43': '马', '44': '羊', '45': '猴', '46': '鸡', '47': '狗', '48': '猪',
    '49': '鼠'
}

def random_sleep(min_time=1, max_time=3):
    """随机等待一段时间"""
    time.sleep(random.uniform(min_time, max_time))

def fetch_api_data(lottery_type):
    """从API获取彩票数据"""
    try:
        # 获取API配置
        api_config = API_CONFIGS[lottery_type]
        main_api = api_config['main']
        backup_apis = api_config['backup']
        
        # 尝试主API
        logger.info(f"尝试从主API获取{LOTTERY_NAMES[lottery_type]}数据: {main_api}")
        response = requests.get(main_api, timeout=10)
        if response.status_code == 200 and response.text:
            return response.text
            
        # 如果主API失败，尝试备用API
        for backup_api in backup_apis:
            logger.info(f"尝试从备用API获取{LOTTERY_NAMES[lottery_type]}数据: {backup_api}")
            try:
                response = requests.get(backup_api, timeout=10)
                if response.status_code == 200 and response.text:
                    return response.text
            except Exception as e:
                logger.error(f"备用API请求失败: {str(e)}")
                continue
                
        logger.error(f"所有API请求失败")
        return None
    except Exception as e:
        logger.error(f"获取API数据出错: {str(e)}")
        return None

# openCode 格式 2  新API获取函数

def parse_api_data(data_str, lottery_type):
    """解析API返回的数据字符串，自动适配K格式和新数组格式，支持新API实时保存未开全号码"""
    try:
        # 新API格式（数组）自动识别
        if data_str.strip().startswith('['):
            try:
                data = json.loads(data_str)
                if not isinstance(data, list) or not data:
                    logger.error("新API数据不是数组或为空")
                    return None
                item = data[0]
                # 期号后三位
                issue = item.get('expect', '')[-3:]
                # 开奖号码，允许未开全
                open_code = item.get('openCode', '')
                numbers = [n.strip() for n in open_code.split(',')]
                # 实时保存，号码不足7个补空
                while len(numbers) < 7:
                    numbers.append('')
                normal_numbers = numbers[:6]
                special_number = numbers[6] if len(numbers) > 6 else ''
                # 生肖
                zodiacs = item.get('zodiac', '').split(',')
                zodiac = zodiacs[6].strip() if len(zodiacs) >= 7 else ''
                # 下一期信息（新API无，需推算）
                next_issue = str(int(issue) + 1).zfill(3) if issue.isdigit() else ''
                # 下一期开奖时间（用openTime+1天，时间不变）
                open_time = item.get('openTime', '')
                try:
                    dt = datetime.strptime(open_time, '%Y-%m-%d %H:%M:%S')
                    next_dt = dt + timedelta(days=1)
                    next_time = f"{next_dt.month:02d}月{next_dt.day:02d}日 {dt.hour:02d}点{dt.minute:02d}分"
                except Exception:
                    next_time = ''
                return {
                    'issue': issue,
                    'numbers': normal_numbers,
                    'special_number': special_number,
                    'zodiac': zodiac,
                    'next_issue': next_issue,
                    'next_time': next_time
                }
            except json.JSONDecodeError:
                logger.error(f"解析新API JSON失败: {data_str}")
                return None
        # 旧K格式逻辑
        try:
            json_data = json.loads(data_str)
            if 'k' in json_data:
                k_data = json_data['k']
            else:
                logger.warning(f"JSON数据中没有'k'字段")
                k_data = data_str
        except json.JSONDecodeError:
            match = re.search(r'[{,]"k"\s*:\s*"([^"]+)"', data_str)
            if match:
                k_data = match.group(1)
            else:
                k_data = data_str
        if isinstance(k_data, dict) and 'k' in k_data:
            k_data = k_data['k']
        if isinstance(k_data, str):
            parts = k_data.split(',')
            if len(parts) >= 8:
                issue = parts[0].zfill(3)[-3:]
                numbers = [parts[i].zfill(2) for i in range(1, 7)]
                special_number = parts[7].zfill(2)
                zodiac = None
                if lottery_type == 'hk':
                    if len(parts) > 8 and len(parts[8]) <= 2:
                        zodiac = parts[8]
                    else:
                        zodiac = ZODIAC_MAPPING.get(special_number, '')
                else:
                    zodiac = ZODIAC_MAPPING.get(special_number, '')
                next_issue = None
                next_time = None
                if len(parts) >= 9:
                    next_issue = parts[8].zfill(3)[-3:]
                    default_times = {
                        'hk': '21:30',
                        'xam': '21:30',
                        'lam': '21:30',
                        'tc': '21:30'
                    }
                    default_hour = "21"
                    default_minute = "30"
                    month = None
                    day = None
                    hour = default_hour
                    minute = default_minute
                    if len(parts) >= 11 and parts[9].isdigit() and parts[10].isdigit():
                        month = parts[9].zfill(2)
                        day = parts[10].zfill(2)
                    time_found = False
                    for i in range(11, min(15, len(parts))):
                        part = parts[i]
                        time_match = re.search(r'(\d{1,2}):(\d{1,2})(?::(\d{1,2}))?', part)
                        if time_match:
                            hour = time_match.group(1).zfill(2)
                            minute = time_match.group(2).zfill(2)
                            time_found = True
                            break
                        time_match = re.search(r'(\d+)\u70b9(\d+)\u5206', part)
                        if time_match:
                            hour = time_match.group(1).zfill(2)
                            minute = time_match.group(2).zfill(2)
                            time_found = True
                            break
                    if not month or not day:
                        today = datetime.now()
                        if (int(hour) < today.hour) or (int(hour) == today.hour and int(minute) <= today.minute):
                            next_date = today + timedelta(days=1)
                        else:
                            next_date = today
                        month = f"{next_date.month:02d}"
                        day = f"{next_date.day:02d}"
                    next_time = f"{month}月{day}日 {hour}点{minute}分"
                if not next_issue or not next_time:
                    next_issue = str(int(issue) + 1).zfill(3)
                    today = datetime.now()
                    next_date = today + timedelta(days=1)
                    default_times = {
                        'hk': '21:30',
                        'xam': '21:30',
                        'lam': '21:30',
                        'tc': '21:30'
                    }
                    hour, minute = default_times[lottery_type].split(':')
                    next_time = f"{next_date.month:02d}月{next_date.day:02d}日 {hour}点{minute}分"
                return {
                    'issue': issue,
                    'numbers': numbers,
                    'special_number': special_number,
                    'zodiac': zodiac,
                    'next_issue': next_issue,
                    'next_time': next_time
                }
            else:
                logger.error(f"数据格式不符合预期: {k_data}")
        logger.error(f"无法解析API数据: {data_str}")
        return None
    except Exception as e:
        logger.error(f"解析API数据出错: {str(e)}")
        return None

def save_lottery_result(lottery_info, lottery_type, data_str=None):
    """保存彩票开奖结果到文件，老API也实时保存API原始内容为json文件，无论号码是否完整"""
    try:
        if not lottery_info:
            logger.error(f"没有可保存的{LOTTERY_NAMES[lottery_type]}开奖结果")
            return False
        issue = lottery_info['issue']
        numbers = lottery_info['numbers']
        special_number = lottery_info['special_number']
        # 格式化结果字符串 - 移除生肖显示
        result = f"第{issue}期：{' '.join(numbers)} 特码 {special_number}"
        # 确定文件名
        filename = 'klb.txt' if lottery_type == 'tc' else f'{lottery_type}.txt'
        # 保存结果到txt文件（保持原逻辑）
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(result)
        # 保存API原始内容为json文件（无论号码是否完整都保存）
        json_map = {
            'hk': 'hkkj.json',
            'xam': 'xamkj.json',
            'lam': 'lamkj.json',
            'tc': 'tckj.json'
        }
        json_filename = json_map.get(lottery_type)
        if json_filename and data_str:
            with open(json_filename, 'w', encoding='utf-8') as jf:
                jf.write(data_str)
        logger.info(f"{LOTTERY_NAMES[lottery_type]}开奖结果：{result}")
        logger.info(f"✅ 已保存{LOTTERY_NAMES[lottery_type]}开奖结果到 {filename}")
        # 保存下一期开奖时间信息到 time.txt
        next_issue = lottery_info['next_issue']
        next_time = lottery_info['next_time']
        mode = 'w' if lottery_type == 'hk' else 'a'
        with open('time.txt', mode, encoding='utf-8') as f:
            f.write(f"{LOTTERY_NAMES[lottery_type]}第{next_issue}期：{next_time}\n")
        logger.info(f"✅ 已更新{LOTTERY_NAMES[lottery_type]}下一期开奖时间信息")
        return True
    except Exception as e:
        logger.error(f"保存{LOTTERY_NAMES[lottery_type]}结果失败: {str(e)}")
        return False

# 新API保存函数

# 删除save_new_api_result函数

def get_lottery_results():
    """获取所有彩票的开奖结果"""
    results = {}
    lottery_types = ['hk', 'xam', 'lam', 'tc']
        
    # 确保time.txt是空的或不存在
    try:
        open('time.txt', 'w', encoding='utf-8').close()
    except:
        pass
    
    for lottery_type in lottery_types:
        logger.info("="*80)
        logger.info(f"\n开始获取{LOTTERY_NAMES[lottery_type]}开奖结果...")
        
        # 获取API数据
        data_str = fetch_api_data(lottery_type)
        if not data_str:
            logger.error(f"❌ 获取{LOTTERY_NAMES[lottery_type]}数据失败")
            continue
            
        # 解析API数据
        lottery_info = parse_api_data(data_str, lottery_type)
        if not lottery_info:
            logger.error(f"❌ 解析{LOTTERY_NAMES[lottery_type]}数据失败")
            continue
            
        # 保存结果
        if save_lottery_result(lottery_info, lottery_type, data_str):
            # 将结果添加到返回值
            results[lottery_type] = {
                'issue': lottery_info['issue'],
                'numbers': lottery_info['numbers'],
                'special_number': lottery_info['special_number'],
                'zodiac': lottery_info['zodiac'],
                'next_issue': lottery_info['next_issue'],
                'next_time': lottery_info['next_time']
            }
            
        # 随机等待一小段时间
        random_sleep()
    
    return results

def main():
    try:
        logger.info("="*80)
        logger.info("开始获取彩票开奖结果...")
        
        results = get_lottery_results()
        
        # 删除main函数中对fetch_new_api_data和parse_new_api_data的调用
        
        # 显示time.txt内容
        try:
            logger.info("\n✅ time.txt 读取成功")
            logger.info("=== time.txt 内容 ===")
            with open('time.txt', 'r', encoding='utf-8') as f:
                content = f.read().strip()
                logger.info(content)
            logger.info("=== time.txt 内容结束 ===\n")
        except Exception as e:
            logger.error(f"❌ 读取 time.txt 失败: {str(e)}\n")
            
        # 如果在Vercel环境中运行，返回结果
        if os.environ.get('VERCEL_ENV'):
            return results
            
    except Exception as e:
        logger.error(f"运行出错: {str(e)}")
        if os.environ.get('VERCEL_ENV'):
            return {"error": str(e)}
            #  自动执行时间范围21:25~21:40 修改 1-3
def is_in_drawing_time():
    now = datetime.now()
    start = now.replace(hour=21, minute=25, second=0, microsecond=0)
    end = now.replace(hour=21, minute=40, second=0, microsecond=0)
    return start <= now <= end
        #  自动执行时间开始修改 2-3
def wait_until_next_drawing_time():
    now = datetime.now()
    start = now.replace(hour=21, minute=25, second=0, microsecond=0)
    if now < start:
        wait_seconds = int((start - now).total_seconds())
    else:
        # 已过开奖时间，等到明天，自动执行时间修改 3-3
        #  wait_seconds -= 600 这里3个600是每10分钟输出一次剩余秒数日志

        tomorrow = now + timedelta(days=1)
        next_start = tomorrow.replace(hour=21, minute=25, second=0, microsecond=0)
        wait_seconds = int((next_start - now).total_seconds())
    while wait_seconds > 600:
        logger.info(f"⏳ 距离下一个开奖时间段还有 {wait_seconds} 秒，等待中...")
        time.sleep(600)
        wait_seconds -= 600
    if wait_seconds > 0:
        logger.info(f"⏳ 距离下一个开奖时间段还有 {wait_seconds} 秒，等待中...")
        time.sleep(wait_seconds)
            #  脚本间隔执行时间修改  `time.sleep(3)` 表示3秒
def run_in_drawing_time():
    logger.info("进入开奖时间段自动循环模式（每3秒执行一次）...")
    while True:
        if is_in_drawing_time():
            main()
            for handler in logger.handlers:
                handler.flush()
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(SEPARATOR)
            time.sleep(3)
        else:
            wait_until_next_drawing_time()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--loop':
        run_in_drawing_time()
    else:
        main()
        for handler in logger.handlers:
            handler.flush()
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(SEPARATOR)
