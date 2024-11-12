# gsc_report.py
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
from config import load_config
import os
from datetime import datetime, timedelta

class SearchConsoleReporter:
    def __init__(self):
        """Search Console レポーターの初期化"""
        config = load_config()
        self.site_url = config['SearchConsole']['site_url']
        self.csv_output = config['csv']['gsc_output_file']
        credentials_file = config['SearchConsole']['credentials_file']
        
        # JSONファイルのパスを構築
        json_path = os.path.join(
            os.path.dirname(__file__),
            'json',
            credentials_file
        )
        
        try:
            # 認証情報の設定
            credentials = service_account.Credentials.from_service_account_file(
                json_path,
                scopes=['https://www.googleapis.com/auth/webmasters.readonly']
            )
            
            # Search Console APIのサービスを構築
            self.service = build('searchconsole', 'v1', credentials=credentials)
            
        except FileNotFoundError:
            raise FileNotFoundError(f"認証情報ファイルが見つかりません: {json_path}")
        except Exception as e:
            raise Exception(f"Search Console APIの初期化中にエラーが発生しました: {str(e)}")

    def get_search_analytics(self, days_ago=7):
        """
        Search Consoleのデータを取得する
        
        Args:
            days_ago (int): 何日前からのデータを取得するか
            
        Returns:
            list: アナリティクスデータのリスト
        """
        try:
            # 日付範囲の設定
            end_date = datetime.now() - timedelta(days=3)  # APIの更新遅延を考慮
            start_date = end_date - timedelta(days=days_ago)
            
            # APIリクエストの作成
            request = {
                'startDate': start_date.strftime('%Y-%m-%d'),
                'endDate': end_date.strftime('%Y-%m-%d'),
                'dimensions': ['date', 'page', 'query'],
                'rowLimit': 25000,  # 最大行数
                'startRow': 0,
                'dimensionFilterGroups': [{
                    'filters': [{
                        'dimension': 'page',
                        'operator': 'contains',
                        'expression': ''  # すべてのページを取得
                    }]
                }],
                'searchType': 'web'  # ウェブ検索のデータ
            }
            
            # データの取得
            response = self.service.searchanalytics().query(
                siteUrl=self.site_url,
                body=request
            ).execute()
            
            # データの整形
            report_data = []
            if 'rows' in response:
                for row in response['rows']:
                    data = {
                        'date': row['keys'][0],
                        'page': row['keys'][1],
                        'query': row['keys'][2],
                        'clicks': row['clicks'],
                        'impressions': row['impressions'],
                        'ctr': row['ctr'],
                        'position': row['position']
                    }
                    report_data.append(data)
            
            return report_data
            
        except Exception as e:
            print(f"データ取得中にエラーが発生しました: {str(e)}")
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
            
            # CTRを百分率に変換
            df['ctr'] = df['ctr'].apply(lambda x: f"{float(x):.2%}")
            
            # 平均表示順位を小数点2桁に丸める
            df['position'] = df['position'].apply(lambda x: f"{float(x):.2f}")
            
            # CSVに保存
            output_path = os.path.join(os.path.dirname(__file__), self.csv_output)
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"データを {output_path} に保存しました")
            
        except Exception as e:
            print(f"CSVファイルの保存中にエラーが発生しました: {str(e)}")