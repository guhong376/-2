import requests
import time
import random
import csv
import os
from bs4 import BeautifulSoup
import json
from models import House, init_db, SessionLocal
import pandas as pd
import re

class LianjiaSpider:
    def __init__(self):
        self.base_url = 'https://bj.lianjia.com/ershoufang/'
        self.session = requests.Session()
        self.session.trust_env = False
        
        # 创建数据保存目录
        self.data_dir = 'data'
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        # User-Agent列表
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
        ]
            
        # 设置请求头
        self.headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0'
        }

    def get_page(self, url, max_retries=3):
        """获取页面内容"""
        for i in range(max_retries):
            try:
                # 随机延时1-3秒
                time.sleep(random.uniform(1, 3))
                # 更新随机User-Agent
                self.headers['User-Agent'] = random.choice(self.user_agents)
                
                response = self.session.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    return response.text
                print(f"请求失败，状态码：{response.status_code}，正在重试...")
            except Exception as e:
                print(f"请求发生错误：{e}，正在重试...")
        return None

    def parse_house_info(self, html):
        """解析房源信息"""
        soup = BeautifulSoup(html, 'lxml')
        house_list = []
        
        # 获取房源列表
        house_items = soup.find_all('div', class_='info clear')
        
        for item in house_items:
            try:
                # 提取房源信息
                title = item.find('div', class_='title').text.strip()
                address = item.find('div', class_='address').text.strip()
                house_info = item.find('div', class_='houseInfo').text.strip()
                follow_info = item.find('div', class_='followInfo').text.strip()
                total_price = item.find('div', class_='totalPrice').text.strip()
                unit_price = item.find('div', class_='unitPrice').text.strip()
                
                # 解析房屋信息
                house_type = house_info.split('|')[0].strip()
                area_str = house_info.split('|')[1].strip()
                direction = house_info.split('|')[2].strip()
                
                # 处理面积数据，提取数字部分
                area = float(re.search(r'(\d+\.?\d*)', area_str).group(1))
                
                # 处理价格数据，提取数字部分
                total_price = float(re.search(r'(\d+\.?\d*)', total_price).group(1))
                unit_price = float(re.search(r'(\d+\.?\d*)', unit_price).group(1))
                
                house_list.append({
                    'title': title,
                    'address': address,
                    'house_type': house_type,
                    'area': area,
                    'direction': direction,
                    'follow_info': follow_info,
                    'total_price': total_price,
                    'unit_price': unit_price
                })
            except Exception as e:
                print(f"解析房源信息时出错：{e}")
                continue
                
        return house_list

    def save_to_database(self, house_list):
        """保存数据到数据库"""
        db = SessionLocal()
        try:
            for house_data in house_list:
                house = House(**house_data)
                db.add(house)
            db.commit()
            print(f"成功保存{len(house_list)}条数据到数据库")
        except Exception as e:
            print(f"保存数据到数据库时出错：{e}")
            db.rollback()
        finally:
            db.close()

    def save_to_csv(self, data, filename):
        """保存数据到CSV文件"""
        if not data:
            return
            
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

    def crawl(self, max_pages=3):
        """爬取主函数"""
        all_houses = []
        
        for page in range(1, max_pages + 1):
            print(f"正在爬取第{page}页...")
            url = f"{self.base_url}pg{page}/"
            html = self.get_page(url)
            
            if not html:
                print(f"获取第{page}页失败")
                continue
                
            houses = self.parse_house_info(html)
            all_houses.extend(houses)
            
            # 每页爬取后随机延时2-5秒
            time.sleep(random.uniform(2, 5))
            
        # 保存数据到数据库
        self.save_to_database(all_houses)
        
        # 保存数据到CSV文件
        self.save_to_csv(all_houses, 'lianjia_houses.csv')
        print(f"爬取完成，共获取{len(all_houses)}条房源信息")

if __name__ == '__main__':
    # 初始化数据库
    init_db()
    
    # 开始爬取
    spider = LianjiaSpider()
    spider.crawl(max_pages=3)  # 默认爬取3页 