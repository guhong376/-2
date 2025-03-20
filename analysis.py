import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pymysql
from config import DB_CONFIG
import numpy as np

class RentalAnalyzer:
    def __init__(self):
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体
        plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题
        self.df = None
        self.conn = None

    def connect_db(self):
        """连接数据库"""
        try:
            self.conn = pymysql.connect(
                host=DB_CONFIG['host'],
                port=DB_CONFIG['port'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database']
            )
            return True
        except Exception as e:
            print(f"数据库连接错误: {e}")
            return False

    def load_data(self):
        """从数据库加载数据"""
        if not self.connect_db():
            return None
            
        try:
            query = """
                SELECT 
                    title,
                    address,
                    house_type,
                    area,
                    direction,
                    follow_info,
                    total_price,
                    unit_price,
                    created_at
                FROM houses
            """
            self.df = pd.read_sql(query, self.conn)
            print(f"成功加载 {len(self.df)} 条数据")
            
            # 数据清洗
            self.df = self.clean_data(self.df)
            print("数据清洗完成")
            
            return self.df
        except Exception as e:
            print(f"加载数据时出错: {e}")
            return None
        finally:
            if self.conn:
                self.conn.close()

    def clean_data(self, df):
        """数据清洗"""
        if df is not None and not df.empty:
            try:
                # 处理面积数据（去除"平米"等单位）
                df['area'] = pd.to_numeric(df['area'].replace('[^\d.]', '', regex=True), errors='coerce')
                
                # 处理价格数据（确保是数值类型）
                df['total_price'] = pd.to_numeric(df['total_price'], errors='coerce')
                df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce')
                
                # 处理关注信息（提取数字）
                df['follow_count'] = pd.to_numeric(df['follow_info'].str.extract('(\d+)', expand=False), errors='coerce')
                
                # 删除缺失值
                df = df.dropna(subset=['area', 'total_price'])
                
                print(f"清洗后的数据量: {len(df)}")
                return df
            except Exception as e:
                print(f"数据清洗时出错: {e}")
                return df
        return df

    def analyze_area_price(self):
        """分析面积与价格的关系"""
        if self.df is None:
            self.df = self.load_data()
            
        if self.df is not None and not self.df.empty:
            plt.figure(figsize=(10, 6))
            sns.scatterplot(data=self.df, x='area', y='total_price')
            plt.title('面积与价格的关系')
            plt.xlabel('面积 (平方米)')
            plt.ylabel('总价 (万元)')
            plt.savefig('data/area_price.png')
            plt.close()
            
            # 计算相关系数
            correlation = self.df['area'].corr(self.df['total_price'])
            print(f"面积与价格的相关系数: {correlation:.2f}")
            
    def analyze_price_distribution(self):
        """分析价格分布"""
        if self.df is None:
            self.df = self.load_data()
            
        if self.df is not None and not self.df.empty:
            plt.figure(figsize=(10, 6))
            sns.histplot(data=self.df, x='total_price', bins=20)
            plt.title('房价分布')
            plt.xlabel('总价 (万元)')
            plt.ylabel('数量')
            plt.savefig('data/price_distribution.png')
            plt.close()
            
    def analyze_direction_price(self):
        """分析朝向与价格的关系"""
        if self.df is None:
            self.df = self.load_data()
            
        if self.df is not None and not self.df.empty:
            direction_price = self.df.groupby('direction')['total_price'].agg(['mean', 'count']).reset_index()
            direction_price = direction_price.sort_values('mean', ascending=False)
            
            plt.figure(figsize=(12, 6))
            sns.barplot(data=direction_price, x='direction', y='mean')
            plt.title('朝向与价格的关系')
            plt.xlabel('朝向')
            plt.ylabel('平均价格 (万元)')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig('data/direction_price.png')
            plt.close()
            
    def analyze_house_type_price(self):
        """分析户型与价格的关系"""
        if self.df is None:
            self.df = self.load_data()
            
        if self.df is not None and not self.df.empty:
            house_type_price = self.df.groupby('house_type')['total_price'].agg(['mean', 'count']).reset_index()
            house_type_price = house_type_price.sort_values('mean', ascending=False)
            
            plt.figure(figsize=(12, 6))
            sns.barplot(data=house_type_price, x='house_type', y='mean')
            plt.title('户型与价格的关系')
            plt.xlabel('户型')
            plt.ylabel('平均价格 (万元)')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig('data/house_type_price.png')
            plt.close()
            
    def analyze_metro_impact(self):
        """分析地铁对房价的影响"""
        if self.df is None:
            self.df = self.load_data()
            
        if self.df is not None and not self.df.empty:
            # 判断是否靠近地铁
            self.df['has_metro'] = self.df['title'].str.contains('地铁', na=False)
            
            # 计算统计信息
            metro_stats = self.df.groupby('has_metro')['total_price'].agg(['mean', 'count']).round(2)
            print("\n地铁对房价的影响统计：")
            print(metro_stats)
            
            plt.figure(figsize=(8, 6))
            sns.boxplot(data=self.df, x='has_metro', y='total_price')
            plt.title('地铁对房价的影响')
            plt.xlabel('是否靠近地铁')
            plt.ylabel('价格 (万元)')
            plt.xticks([0, 1], ['否', '是'])
            plt.savefig('data/metro_impact.png')
            plt.close()
            
    def run_all_analysis(self):
        """运行所有分析"""
        print("开始数据分析...")
        self.load_data()
        
        if self.df is not None and not self.df.empty:
            print("\n1. 分析面积与价格的关系")
            self.analyze_area_price()
            
            print("\n2. 分析价格分布")
            self.analyze_price_distribution()
            
            print("\n3. 分析朝向与价格的关系")
            self.analyze_direction_price()
            
            print("\n4. 分析户型与价格的关系")
            self.analyze_house_type_price()
            
            print("\n5. 分析地铁对房价的影响")
            self.analyze_metro_impact()
            
            print("\n数据分析完成！")
        else:
            print("没有数据可供分析")

if __name__ == "__main__":
    analyzer = RentalAnalyzer()
    analyzer.run_all_analysis() 