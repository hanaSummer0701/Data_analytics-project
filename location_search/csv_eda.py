
import pandas as pd

df = pd.read_csv('kakao_crawled_fin.csv')
# 'url' 컬럼이 결측값인 행 삭제
df = df.dropna(subset=['url'])

# 결측값 제거 및 필요한 데이터만 리스트로 변환
data = df.dropna(subset=['address', 'title', 'point'])  # 'address', 'title', 'point' 컬럼에서 결측값 제거

data.to_csv("processed_df.csv")
