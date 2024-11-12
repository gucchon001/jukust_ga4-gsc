# ga4_report.py
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from google.oauth2 import service_account
import pandas as pd
from config import load_config
import os

class GA4Reporter:
    def __init__(self):
        """GA4レポーターの初期化"""
        config = load_config()
        self.property_id = config['GA4']['property_id']
        self.csv_output = config['csv']['output_file']
        credentials_file = config['GA4']['credentials_file']
        
        # JSONファイルのパスを構築（jsonフォルダ内）
        json_path = os.path.join(
            os.path.dirname(__file__),
            'json',
            credentials_file
        )
        
        # 認証情報の設定
        try:
            credentials = service_account.Credentials.from_service_account_file(
                json_path,
                scopes=["https://www.googleapis.com/auth/analytics.readonly"]
            )
        except FileNotFoundError:
            raise FileNotFoundError(f"認証情報ファイルが見つかりません: {json_path}")
        except Exception as e:
            raise Exception(f"認証情報の読み込み中にエラーが発生しました: {str(e)}")
        
        # クライアントの初期化
        self.client = BetaAnalyticsDataClient(credentials=credentials)

    def get_report(self, days_ago=30):
        """
        GA4のレポートを取得する
        
        Args:
            days_ago (int): 何日前からのデータを取得するか
            
        Returns:
            list: レポートデータのリスト
        """
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            date_ranges=[DateRange(
                start_date=f"{days_ago}daysAgo",
                end_date="today"
            )],
            dimensions=[
                Dimension(name="date"),
                Dimension(name="pageTitle"),
            ],
            metrics=[
                Metric(name="screenPageViews"),
                Metric(name="totalUsers"),
                Metric(name="engagementRate"),
            ],
        )
        
        try:
            response = self.client.run_report(request)
            
            report_data = []
            for row in response.rows:
                data = {
                    'date': row.dimension_values[0].value,
                    'page_title': row.dimension_values[1].value,
                    'page_views': int(row.metric_values[0].value),
                    'users': int(row.metric_values[1].value),
                    'engagement_rate': float(row.metric_values[2].value),
                }
                report_data.append(data)
                
            return report_data
        
        except Exception as e:
            print(f"レポート取得中にエラーが発生しました: {str(e)}")
            return None

    def save_to_csv(self, data):
        """
        データをCSVファイルに保存する
        
        Args:
            data (list): 保存するデータ
        """
        if not data:
            print("保存するデータがありません")
            return
        
        try:
            # DataFrameに変換
            df = pd.DataFrame(data)
            
            # engagement_rateを百分率に変換
            df['engagement_rate'] = df['engagement_rate'].apply(lambda x: f"{float(x):.2%}")
            
            # CSVに保存
            output_path = os.path.join(os.path.dirname(__file__), self.csv_output)
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"データを {output_path} に保存しました")
            
        except Exception as e:
            print(f"CSVファイルの保存中にエラーが発生しました: {str(e)}")