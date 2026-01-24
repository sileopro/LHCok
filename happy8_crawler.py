import requests
from bs4 import BeautifulSoup
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
import time
import re
import win32com.client as win32
import pythoncom
from openpyxl.styles import Border, Side

class Happy8Crawler:
    def __init__(self):
        self.base_url = ""
        self.data = []
    
    def crawl_data(self, url="https://m.ssqzj.com/kaijiang/fckl8/",All=False,last=False, period=None, start_period=None, end_period=None):
        """爬取开奖数据"""
        self.base_url = url
        print(f"开始爬取{self.base_url}")
        self.data = []
        page = 1
        max_pages = 1  # 防止无限循环
        if All: #获取所有数据
            max_pages = 9
            while page <= max_pages:
                try:
                    url = f"{self.base_url}p{page}/"
                    print(f"请求URL: {url}")
                    sess = requests.session()
                    jsPage = sess.get(url).text
                    soup = BeautifulSoup(jsPage, "html.parser") 
                    # 查找开奖结果列表
                    if page == 1: 
                        #爬取当前最新开奖结果
                        results = soup.find_all("div", class_="kb_num kj_num public_num")
                        if not results:
                            break
                        
                        for result in results:      
                            period_text = result.get_text(strip=True)
                            period_match = re.search(r"第(\d+)期", period_text)
                            if not period_match:
                                continue
                            period_num = period_match.group(1)#提取当前开奖日期期数
                            print("period_num:", period_num)                       
                            
                            # 提取号码
                            number_list = [num.get_text(strip=True) for num in result.find_all("span", class_="qiu_red")]
                            print("number_list:", number_list)
                        
                            # 构建数据字典
                            item = {
                                "期数": period_num,
                                "号码": number_list
                            }
                            
                            self.data.append(item)
                        #提取当前页面其他期开奖结果
                        results = soup.find_all("div", class_="kb_num kj_num kj_erj")
                        print("page:--------------------",page,"--------------------")
                        print("results:", results)
                        if not results:
                            break
                        for index,result in enumerate(results):      
                            period_text = result.get_text(strip=True)
                            period_match = re.search(r"第(\d+)期", period_text)
                            if not period_match:
                                continue
                            period_num = period_match.group(1)#提取当前开奖日期期数
                            print("period_num:", period_num)                       
                            
                            # 提取号码
                            if index == 0 :
                                number_list = [num.get_text(strip=True) for num in result.find_all("span", class_="qiu_red")]
                            else:
                                number_list = [num.get_text(strip=True) for num in result.find_all("span", class_="red_white")]
                            print("number_list:", number_list)
                        
                            # 构建数据字典
                            item = {
                                "期数": period_num,
                                "号码": number_list
                            }
                            
                            self.data.append(item)
                        page += 1
                        time.sleep(1)  # 防止过快请求
                    else:
                        results = soup.find_all("div", class_="kb_num kj_num kj_erj")
                        print("page:--------------------",page,"--------------------")
                        print("results:", results)
                        if not results:
                            break
                        for index,result in enumerate(results):      
                            period_text = result.get_text(strip=True)
                            period_match = re.search(r"第(\d+)期", period_text)
                            if not period_match:
                                continue
                            period_num = period_match.group(1)#提取当前开奖日期期数
                            print("period_num:", period_num)                       
                            
                            # 提取号码
                            if index == 0 :
                                number_list = [num.get_text(strip=True) for num in result.find_all("span", class_="qiu_red")]
                            else:
                                number_list = [num.get_text(strip=True) for num in result.find_all("span", class_="red_white")]
                            print("number_list:", number_list)
                        
                            # 构建数据字典
                            item = {
                                "期数": period_num,
                                "号码": number_list
                            }
                            
                            self.data.append(item)
                        page += 1
                        time.sleep(2)                 
                except Exception as e:
                    print(f"爬取第{page}页时出错: {e}")
                    break      
        if last:#获取最新数据
            try:
                url = f"{self.base_url}p{page}/"
                print(f"请求URL: {url}")
                sess = requests.session()
                jsPage = sess.get(url).text
                soup = BeautifulSoup(jsPage, "html.parser") 
                # 查找开奖结果列表
                    #爬取当前最新开奖结果
                results = soup.find_all("div", class_="kb_num kj_num public_num")                    
                for result in results:      
                    period_text = result.get_text(strip=True)
                    period_match = re.search(r"第(\d+)期", period_text)
                    if not period_match:
                        continue
                    period_num = period_match.group(1)#提取当前开奖日期期数
                    print("period_num:", period_num)                       
                    
                    # 提取号码
                    number_list = [num.get_text(strip=True) for num in result.find_all("span", class_="qiu_red")]
                    print("number_list:", number_list)
                
                    # 构建数据字典
                    item = {
                        "期数": period_num,
                        "号码": number_list
                    }                            
                    self.data.append(item) 
                time.sleep(1)  # 防止过快请求                               
            except Exception as e:
                print(f"爬取第{page}页时出错: {e}")   
        if period!=None:#按照期数获取数据
            max_pages = 9
            finded = False
            while page <= max_pages and not finded:
                try:
                    url = f"{self.base_url}p{page}/"
                    print(f"请求URL: {url}")
                    sess = requests.session()
                    jsPage = sess.get(url).text
                    soup = BeautifulSoup(jsPage, "html.parser") 
                    # 查找开奖结果列表
                    if page == 1: 
                        #爬取当前最新开奖结果
                        results = soup.find_all("div", class_="kb_num kj_num public_num")
                        if not results:
                            break
                        
                        for result in results:      
                            period_text = result.get_text(strip=True)
                            period_match = re.search(r"第(\d+)期", period_text)
                            if not period_match:
                                continue
                            period_num = period_match.group(1)#提取当前开奖日期期数
                            print("period_num:", period_num)                       
                            
                            # 提取号码
                            number_list = [num.get_text(strip=True) for num in result.find_all("span", class_="qiu_red")]
                            print("number_list:", number_list)
                        
                            # 构建数据字典
                            item = {
                                "期数": period_num,
                                "号码": number_list
                            }
                            if period_num == period:
                                self.data.append(item)
                                finded = True
                                break                            
                        #提取当前页面其他期开奖结果
                        results = soup.find_all("div", class_="kb_num kj_num kj_erj")
                        print("page:--------------------",page,"--------------------")
                        print("results:", results)
                        if not results:
                            break
                        for index,result in enumerate(results):      
                            period_text = result.get_text(strip=True)
                            period_match = re.search(r"第(\d+)期", period_text)
                            if not period_match:
                                continue
                            period_num = period_match.group(1)#提取当前开奖日期期数
                            print("period_num:", period_num)                       
                            
                            # 提取号码
                            if index == 0 :
                                number_list = [num.get_text(strip=True) for num in result.find_all("span", class_="qiu_red")]
                            else:
                                number_list = [num.get_text(strip=True) for num in result.find_all("span", class_="red_white")]
                            print("number_list:", number_list)
                        
                            # 构建数据字典
                            item = {
                                "期数": period_num,
                                "号码": number_list
                            }
                            
                            if period_num == period:
                                self.data.append(item)
                                finded = True
                                break   
                        page += 1
                        time.sleep(1)  # 防止过快请求
                    else:
                        results = soup.find_all("div", class_="kb_num kj_num kj_erj")
                        print("page:--------------------",page,"--------------------")
                        print("results:", results)
                        if not results:
                            break
                        for index,result in enumerate(results):      
                            period_text = result.get_text(strip=True)
                            period_match = re.search(r"第(\d+)期", period_text)
                            if not period_match:
                                continue
                            period_num = period_match.group(1)#提取当前开奖日期期数
                            print("period_num:", period_num)                       
                            
                            # 提取号码
                            if index == 0 :
                                number_list = [num.get_text(strip=True) for num in result.find_all("span", class_="qiu_red")]
                            else:
                                number_list = [num.get_text(strip=True) for num in result.find_all("span", class_="red_white")]
                            print("number_list:", number_list)
                        
                            # 构建数据字典
                            item = {
                                "期数": period_num,
                                "号码": number_list
                            }
                            
                            if period_num == period:
                                self.data.append(item)
                                finded = True
                                break   
                        page += 1
                        time.sleep(2)                 
                except Exception as e:
                    print(f"爬取第{page}页时出错: {e}")
                    break  
        if start_period is not None and end_period is not None:#按照期数范围查询
            max_pages = 9
            findfinished = False #区间查找结束标记
            while page <= max_pages and not findfinished:
                try:
                    url = f"{self.base_url}p{page}/"
                    print(f"请求URL: {url}")
                    sess = requests.session()
                    jsPage = sess.get(url).text
                    soup = BeautifulSoup(jsPage, "html.parser") 
                    # 查找开奖结果列表
                    if page == 1: 
                        #爬取当前最新开奖结果
                        results = soup.find_all("div", class_="kb_num kj_num public_num")
                        if not results:
                            break
                        
                        for result in results:      
                            period_text = result.get_text(strip=True)
                            period_match = re.search(r"第(\d+)期", period_text)
                            if not period_match:
                                continue
                            period_num = period_match.group(1)#提取当前开奖日期期数
                            print("period_num:", period_num)                       
                            
                            # 提取号码
                            number_list = [num.get_text(strip=True) for num in result.find_all("span", class_="qiu_red")]
                            print("number_list:", number_list)
                        
                            # 构建数据字典
                            item = {
                                "期数": period_num,
                                "号码": number_list
                            }
                            
                            if int(period_num) >= int(start_period) and int(period_num) <= int(end_period):
                                self.data.append(item)
                            if int(period_num) < int(start_period):
                                findfinished = True
                                break
                        #提取当前页面其他期开奖结果
                        results = soup.find_all("div", class_="kb_num kj_num kj_erj")
                        print("page:--------------------",page,"--------------------")
                        print("results:", results)
                        if not results:
                            break
                        for index,result in enumerate(results):      
                            period_text = result.get_text(strip=True)
                            period_match = re.search(r"第(\d+)期", period_text)
                            if not period_match:
                                continue
                            period_num = period_match.group(1)#提取当前开奖日期期数
                            print("period_num:", period_num)                       
                            
                            # 提取号码
                            if index == 0 :
                                number_list = [num.get_text(strip=True) for num in result.find_all("span", class_="qiu_red")]
                            else:
                                number_list = [num.get_text(strip=True) for num in result.find_all("span", class_="red_white")]
                            print("number_list:", number_list)
                        
                            # 构建数据字典
                            item = {
                                "期数": period_num,
                                "号码": number_list
                            }
                            
                            if int(period_num) >= int(start_period) and int(period_num) <= int(end_period):
                                self.data.append(item)
                            if int(period_num) < int(start_period):
                                findfinished = True
                                break
                        page += 1
                        time.sleep(1)  # 防止过快请求
                    else:
                        results = soup.find_all("div", class_="kb_num kj_num kj_erj")
                        print("page:--------------------",page,"--------------------")
                        print("results:", results)
                        if not results:
                            break
                        for index,result in enumerate(results):      
                            period_text = result.get_text(strip=True)
                            period_match = re.search(r"第(\d+)期", period_text)
                            if not period_match:
                                continue
                            period_num = period_match.group(1)#提取当前开奖日期期数
                            print("period_num:", period_num)                       
                            
                            # 提取号码
                            if index == 0 :
                                number_list = [num.get_text(strip=True) for num in result.find_all("span", class_="qiu_red")]
                            else:
                                number_list = [num.get_text(strip=True) for num in result.find_all("span", class_="red_white")]
                            print("number_list:", number_list)
                        
                            # 构建数据字典
                            item = {
                                "期数": period_num,
                                "号码": number_list
                            }
                            
                            if int(period_num) >= int(start_period) and int(period_num) <= int(end_period):
                                self.data.append(item)
                            if int(period_num) < int(start_period):
                                findfinished = True
                                break
                        page += 1
                        time.sleep(2)                 
                except Exception as e:
                    print(f"爬取第{page}页时出错: {e}")
                    break      
        return self.data
    
    def search_by_period(self,url, period):
        """按期数查询"""
        return self.crawl_data(url=url,period=period)
        

    
    def search_by_last(self,url,last):
        """按最新期数查询"""
        return self.crawl_data(url=url,last=last)
    def search_by_period_range(self,url,start_period, end_period):
        """按期数范围查询"""
        return self.crawl_data(url=url,start_period=start_period, end_period=end_period)
    def save_to_excel(self, data, file_path,first=False):#First是否是获取全部数据，如果First=True，则代表获取全部数据，并将数据按照期数从前往后正序排列，如果是不是获取全部结果，则将查询到的期数结果保存到表格的末尾
        """保存到Excel"""
        pythoncom.CoInitialize()
        if not data:
            return False
        # df = pd.DataFrame(data)
        try:
            # df.to_excel(file_path, index=False, engine="openpyxl")
            sheet_name = "Sheet3"
            row_index = 3
            excel = win32.gencache.EnsureDispatch('Excel.Application')
            excel.Visible = False  # 可选，设置为True可以看到Excel窗口

                # 打开工作簿
            workbook = excel.Workbooks.Open(file_path)
            sheet = workbook.Worksheets(sheet_name)

                # 插入行，row_index是从1开始的行号
            if first:
                print("先清空数据，再保存数据")
                #先清空数据，再倒叙查询数据
                max_row = sheet.UsedRange.Rows.Count
                for i in range(max_row, row_index-1, -1):
                    sheet.Rows(i).Delete()                
                print("开始保存数据")
                print("data:", self.data)
                for index,item in enumerate(self.data):
                    print("item:", item)
                    sheet.Rows(row_index).Insert(Shift=win32.constants.xlDown)
                    sheet.Cells(row_index, 1).Value = item["期数"]
                    sheet.Cells(row_index, 1).Font.Bold = True
                    for col in range(1, 82):
                        sheet.Cells(row_index, col).Borders.LineStyle = 3
                        sheet.Cells(row_index, col).Interior.Color = 0xFFFFFF if (index+1) %2==0 else 0xDEDEDE
                    for num in item["号码"]:
                        sheet.Cells(row_index, int(num)+1).Value = num
                        sheet.Cells(row_index, int(num)+1).Font.Bold = True
                        sheet.Cells(row_index, int(num)+1).Borders.LineStyle = 3
                        sheet.Cells(row_index, int(num)+1).Interior.Color = 0xFFFFFF if (index+1) %2==0 else 0xDEDEDE   
            else:
                print("追加保存数据")
                for index,item in enumerate(data):
                    row_index = sheet.UsedRange.Rows.Count+1
                    print("row_index:", row_index)
                    sheet.Rows(row_index).Insert(Shift=win32.constants.xlDown)
                    sheet.Cells(row_index, 1).Value = item["期数"]
                    sheet.Cells(row_index, 1).Font.Bold = True
                    for col in range(1, 82):
                        sheet.Cells(row_index, col).Borders.LineStyle = 3
                        sheet.Cells(row_index, col).Interior.Color = 0xDEDEDE if row_index %2==0 else 0xFFFFFF
                    for num in item["号码"]:
                        sheet.Cells(row_index, int(num)+1).Value = num
                        sheet.Cells(row_index, int(num)+1).Font.Bold = True
                        sheet.Cells(row_index, int(num)+1).Borders.LineStyle = 3
                        sheet.Cells(row_index, int(num)+1).Interior.Color =  0xDEDEDE if row_index %2==0 else 0xFFFFFF
                # 保存并关闭工作簿
            workbook.Close(SaveChanges=True)
            excel.Quit()            
            return True
        except Exception as e:
            print(f"保存Excel时出错: {e}")
            return False
        finally:
            pythoncom.CoUninitialize()

class Happy8GUI:
    def __init__(self):
        self.crawler = Happy8Crawler()
        self.root = tk.Tk()
        self.root.title("快乐8开奖结果查询工具")
        self.root.geometry("800x600")
        
        self.create_widgets()
    
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="快乐8开奖结果查询", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 查询方式选择
        query_frame = ttk.LabelFrame(main_frame, text="查询方式", padding="10")
        query_frame.pack(fill=tk.X, pady=10)
        
        self.query_type = tk.StringVar(value="all")
        
        ttk.Radiobutton(query_frame, text="爬取全部数据", variable=self.query_type, value="all").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        ttk.Radiobutton(query_frame, text="按期数查询", variable=self.query_type, value="period").grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        ttk.Radiobutton(query_frame, text="按最新期数查询", variable=self.query_type, value="last").grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)
        ttk.Radiobutton(query_frame, text="按期数范围查询", variable=self.query_type, value="range").grid(row=0, column=3, padx=10, pady=5, sticky=tk.W)
        # 查询参数输入
        param_frame = ttk.LabelFrame(main_frame, text="查询参数", padding="10")
        param_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(param_frame, text="期数:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.period_entry = ttk.Entry(param_frame, width=15)
        self.period_entry.grid(row=0, column=1, padx=5, pady=5)        
        
        ttk.Label(param_frame, text="起始期数:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        self.start_period_entry = ttk.Entry(param_frame, width=15)
        self.start_period_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(param_frame, text="结束期数:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.E)
        self.end_period_entry = ttk.Entry(param_frame, width=15)
        self.end_period_entry.grid(row=1, column=3, padx=5, pady=5)
        

        ttk.Label(param_frame, text="查询网址:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        self.url = ttk.Entry(param_frame, width=30)
        self.url.insert(0,"https://m.ssqzj.com/kaijiang/fckl8/")
        self.url.grid(row=2, column=1, padx=5, pady=5)
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="开始爬取", command=self.start_crawl).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="保存到Excel", command=self.save_to_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空数据", command=self.clear_data).pack(side=tk.LEFT, padx=5)
        
        # 结果显示
        result_frame = ttk.LabelFrame(main_frame, text="查询结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 创建表格
        columns = ("期数",  "号码")
        self.tree = ttk.Treeview(result_frame, columns=columns, show="headings")
        
        # 设置列宽
        self.tree.column("期数", width=100, anchor=tk.CENTER)
        self.tree.column("号码", width=300, anchor=tk.CENTER)
        
        # 设置表头
        for col in columns:
            self.tree.heading(col, text=col)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def start_crawl(self):
        """开始爬取数据"""
        query_type = self.query_type.get()
        
        try:
            if query_type == "all":
                data = self.crawler.crawl_data(url=self.url.get().strip(),All=True)
            elif query_type == "period":
                period = self.period_entry.get().strip()
                if not period:
                    messagebox.showerror("错误", "请输入期数")
                    return
                data = self.crawler.search_by_period(url=self.url.get().strip(),period=period)

            elif query_type == "last": #按照最新期数查询
                data = self.crawler.search_by_last(url=self.url.get().strip(),last=True)
            elif query_type == "range":
                start_period = self.start_period_entry.get().strip()
                end_period = self.end_period_entry.get().strip()
                if not (start_period and end_period):
                    messagebox.showerror("错误", "请输入起始和结束期数")
                    return
                if int(start_period) > int(end_period):
                    messagebox.showerror("错误", "起始期数不能大于结束期数")
                    return  
                data = self.crawler.search_by_period_range(url=self.url.get().strip(),start_period=start_period, end_period=end_period)
            else:
                messagebox.showerror("错误", "请选择查询方式")
                return
            
            # 更新表格
            self.update_table(data)
            messagebox.showinfo("成功", f"共获取{len(data)}条记录")
            
        except Exception as e:
            messagebox.showerror("错误", f"爬取过程中出错: {e}")
    
    def update_table(self, data):
        """更新表格显示"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 添加新数据
        for item in data:
            self.tree.insert("", tk.END, values=(item["期数"], item["号码"]))
    
    def save_to_excel(self):
        """保存数据到Excel"""
        print("数据保存到Excel：", self.crawler.data)
        if not self.crawler.data:
            messagebox.showerror("错误", "没有数据可保存")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")],
            title="保存快乐8开奖结果"
        )
        
        if file_path:
            if self.crawler.save_to_excel(self.crawler.data, file_path,first = True if self.query_type.get()=="all" else False):
                messagebox.showinfo("成功", f"数据已保存到 {file_path}")
            else:
                messagebox.showerror("错误", "保存Excel文件失败")


    def clear_data(self):
        """清空数据"""
        self.crawlerdata = []
        self.update_table([])
        messagebox.showinfo("成功", "数据已清空")
    
    def run(self):
        """运行界面"""
        self.root.mainloop()

if __name__ == "__main__":
    app = Happy8GUI()
    app.run()