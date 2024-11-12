# main_gsc.py
from gsc_report import SearchConsoleReporter
import pandas as pd

def main():
    try:
        reporter = SearchConsoleReporter()
        results = reporter.get_search_analytics(days_ago=7)  # 過去7日間のデータを取得
        
        if results:
            print("=== Search Console レポート ===")
            print(f"データ件数: {len(results):,}件")
            
            # 集計データの表示
            df = pd.DataFrame(results)
            summary = {
                '総クリック数': df['clicks'].sum(),
                '総インプレッション数': df['impressions'].sum(),
                '平均CTR': df['ctr'].mean() * 100,
                '平均表示順位': df['position'].mean()
            }
            
            print("\n=== サマリー ===")
            print(f"総クリック数: {summary['総クリック数']:,}")
            print(f"総インプレッション数: {summary['総インプレッション数']:,}")
            print(f"平均CTR: {summary['平均CTR']:.2f}%")
            print(f"平均表示順位: {summary['平均表示順位']:.2f}")
            
            # CSVファイルに保存
            reporter.save_to_csv(results)
    
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")

if __name__ == "__main__":
    main()