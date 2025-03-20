from lianjia_spider import LianjiaSpider
from analysis import RentalAnalyzer
from models import init_db
import os

def main():
    # 创建数据目录
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # 初始化数据库表
    print("初始化数据库...")
    init_db()
    
    print("开始爬取链家网房源数据...")
    spider = LianjiaSpider()
    spider.crawl(max_pages=3)  # 爬取3页数据
    
    print("\n开始数据分析...")
    analyzer = RentalAnalyzer()
    stats = analyzer.run_analysis()
    
    print("\n分析完成！统计结果：")
    for key, value in stats.items():
        print(f"{key}: {value:.2f}")
    
    print("\n可视化结果已保存到 data 目录下：")
    print("1. price_distribution.png - 房价分布图")
    print("2. area_price_correlation.png - 面积与价格关系图")
    print("3. house_type_distribution.png - 户型分布图")
    print("4. direction_distribution.png - 朝向分布图")
    print("5. summary_statistics.txt - 统计摘要")

if __name__ == '__main__':
    main() 