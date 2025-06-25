import requests
import json
import time
import re
import os
import random
from datetime import datetime, timedelta
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# API配置
API_CONFIGS = {
    'hk': {  # 港彩
        'main': 'https://mnashd213asdhgask.amsndgbaidu.com/asmdasda/xgkj.json',
        'backup': [
            'https://kjkj.kj88889.com/bmjg.js',
            'https://api.493210.com/bmxg.js',
            'https://001033.com/kj/js/xgjs.asp'
        ]
    },
    'xam': {  # 新澳
        'main': 'https://mnashd213asdhgask.amsndgbaidu.com/asmdasda/amksj.json',
        'backup': [
            'https://api.493210.com/bmam.js',
            'https://001033.com/kj/js/amjs.asp'
        ]
    },
    'lam': {  # 老澳
        'main': 'https://49xr.cc/data/tw.js',
        'backup': [
            'https://api.493210.com/bm.js'
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

def parse_api_data(data_str, lottery_type):
    """解析API返回的数据字符串"""
    try:
        # 尝试解析JSON格式
        try:
            json_data = json.loads(data_str)
            if 'k' in json_data:
                k_data = json_data['k']
            else:
                logger.warning(f"JSON数据中没有'k'字段")
                k_data = data_str
        except json.JSONDecodeError:
            # 如果不是标准JSON，尝试从字符串中提取k参数
            match = re.search(r'[{,]"k"\s*:\s*"([^"]+)"', data_str)
            if match:
                k_data = match.group(1)
            else:
                k_data = data_str
        
        # 如果k_data仍然是复杂结构，尝试进一步解析
        if isinstance(k_data, dict) and 'k' in k_data:
            k_data = k_data['k']
        
        # 如果k_data是字符串，按逗号分割
        if isinstance(k_data, str):
            parts = k_data.split(',')
            
            # 检查分割后的长度，确保至少有8个部分(期号+7个数字)
            if len(parts) >= 8:
                issue = parts[0].zfill(3)[-3:]  # 取最后3位作为期号
                numbers = [parts[i].zfill(2) for i in range(1, 7)]  # 前6个号码
                special_number = parts[7].zfill(2)  # 特码
                
                # 获取生肖(如果有)
                zodiac = None
                if lottery_type == 'hk':
                    # 对于港彩，尝试查找生肖字段，或使用映射
                    if len(parts) > 8 and len(parts[8]) <= 2:
                        # 部分API可能直接提供生肖信息
                        zodiac = parts[8]
                    else:
                        # 否则根据特码查找对应的生肖
                        zodiac = ZODIAC_MAPPING.get(special_number, '')
                else:
                    # 对于其他彩种，使用映射表
                    zodiac = ZODIAC_MAPPING.get(special_number, '')
                
                # 获取下一期信息（如果存在）
                next_issue = None
                next_time = None
                
                if len(parts) >= 9:
                    next_issue = parts[8].zfill(3)[-3:]  # 下一期期号
                    
                    # 尝试解析下一期开奖日期和时间
                    if len(parts) >= 12:
                        # 检查是否有月份和日期信息（通常在parts[9]和parts[10]位置）
                        if len(parts) >= 11 and parts[9].isdigit() and parts[10].isdigit():
                            # 这种情况下，parts[9]是月份，parts[10]是日期
                            month = parts[9].zfill(2)
                            day = parts[10].zfill(2)
                            
                            # 如果有时间信息，使用它
                            if len(parts) >= 13 and '\u70b9' in parts[12]:  # 检查是否包含"点"字
                                time_str = parts[12]
                                time_match = re.search(r'(\d+)\u70b9(\d+)\u5206', time_str)  # 匹配"X点X分"
                                if time_match:
                                    hour = time_match.group(1).zfill(2)
                                    minute = time_match.group(2).zfill(2)
                                else:
                                    # 使用默认时间
                                    default_times = {
                                        'hk': '21:32',
                                        'xam': '21:32:30',
                                        'lam': '21:32:30',
                                        'tc': '21:32:00'
                                    }
                                    hour, minute = default_times[lottery_type].split(':')[:2]
                            else:
                                # 使用默认时间
                                default_times = {
                                    'hk': '21:32',
                                    'xam': '21:32:30',
                                    'lam': '21:32:30',
                                    'tc': '21:32:00'
                                }
                                hour, minute = default_times[lottery_type].split(':')[:2]
                                
                            next_time = f"{month}月{day}日 {hour}点{minute}分"
                        else:
                            # 老的方式：检查星期几和时间
                            weekday = parts[10] if len(parts) > 10 else ""  # 星期几
                            time_str = parts[11] if len(parts) > 11 else ""  # 时间字符串
                            
                            # 尝试从Unicode转义的字符串中提取时间信息
                            time_match = None
                            if time_str:
                                # 查找类似"21点32分"的模式
                                time_match = re.search(r'(\d+)\u70b9(\d+)\u5206', time_str)  # Unicode for "点" and "分"
                            
                            if time_match:
                                hour = time_match.group(1).zfill(2)
                                minute = time_match.group(2).zfill(2)
                                
                                # 当前日期
                                today = datetime.now()
                                
                                # 获取下一期的月和日
                                # 如果API没有提供月和日，则假设是明天
                                next_date = today + timedelta(days=1)
                                month = f"{next_date.month:02d}"
                                day = f"{next_date.day:02d}"
                                
                                next_time = f"{month}月{day}日 {hour}点{minute}分"
                            else:
                                # 无法从API解析时间，使用默认时间
                                today = datetime.now()
                                next_date = today + timedelta(days=1)  # 假设是明天
                                default_times = {
                                    'hk': '21:32',
                                    'xam': '21:32:30',
                                    'lam': '21:32:30',
                                    'tc': '21:32:00'
                                }
                                hour, minute = default_times[lottery_type].split(':')[:2]
                                next_time = f"{next_date.month:02d}月{next_date.day:02d}日 {hour}点{minute}分"
                
                # 如果没有从API获取到下一期信息，尝试推算
                if not next_issue or not next_time:
                    # 推算下一期期号
                    next_issue = str(int(issue) + 1).zfill(3)
                    
                    # 推算下一期时间
                    today = datetime.now()
                    next_date = today + timedelta(days=1)  # 假设是明天
                    default_times = {
                        'hk': '21:32',
                        'xam': '21:32:30',
                        'lam': '21:32:30',
                        'tc': '21:32:00'
                    }
                    hour, minute = default_times[lottery_type].split(':')[:2]
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

def save_lottery_result(lottery_info, lottery_type):
    """保存彩票开奖结果到文件"""
    try:
        if not lottery_info:
            logger.error(f"没有可保存的{LOTTERY_NAMES[lottery_type]}开奖结果")
            return False
            
        issue = lottery_info['issue']
        numbers = lottery_info['numbers']
        special_number = lottery_info['special_number']
        zodiac = lottery_info['zodiac']
        
        # 格式化结果字符串
        result = f"第{issue}期：{' '.join(numbers)} 特码 {special_number}"
        if zodiac:
            result += f" {zodiac}"
            
        # 确定文件名
        filename = 'klb.txt' if lottery_type == 'tc' else f'{lottery_type}.txt'
        
        # 保存结果到文件
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(result)
        logger.info(f"✅ 已保存{LOTTERY_NAMES[lottery_type]}开奖结果到 {filename}")
        
        # 保存下一期开奖时间信息到 time.txt
        next_issue = lottery_info['next_issue']
        next_time = lottery_info['next_time']
        
        # 确保time.txt的写入模式（第一个彩种用w，其余用a）
        mode = 'w' if lottery_type == 'lam' else 'a'
        with open('time.txt', mode, encoding='utf-8') as f:
            f.write(f"{LOTTERY_NAMES[lottery_type]}第{next_issue}期：{next_time}\n")
        logger.info(f"✅ 已更新{LOTTERY_NAMES[lottery_type]}下一期开奖时间信息")
        
        return True
    except Exception as e:
        logger.error(f"保存{LOTTERY_NAMES[lottery_type]}结果失败: {str(e)}")
        return False

def get_lottery_results():
    """获取所有彩票的开奖结果"""
    results = {}
    lottery_types = ['lam', 'xam', 'hk', 'tc']
    
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
        if save_lottery_result(lottery_info, lottery_type):
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

if __name__ == '__main__':
    main()
