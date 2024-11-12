# main.py
from ga4_report import GA4Reporter

def main():
    reporter = GA4Reporter()
    results = reporter.get_report(days_ago=7)  # 過去7日間のデータを取得
    
    if results:
        print("=== GA4レポート ===")
        for row in results:
            print(f"\n日付: {row['date']}")
            print(f"ページタイトル: {row['page_title']}")
            print(f"ページビュー数: {row['page_views']:,}")
            print(f"ユーザー数: {row['users']:,}")
            print(f"エンゲージメント率: {row['engagement_rate']:.2%}")
        
        # CSVファイルに保存
        reporter.save_to_csv(results)

if __name__ == "__main__":
    main()