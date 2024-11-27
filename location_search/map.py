from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    # CSV 파일 읽기
    # df = pd.read_csv('processed_df.csv')
    df = pd.read_excel('handling.xlsx')
    # 결측값 제거 및 필요한 데이터만 리스트로 변환
    data = df.dropna(subset=['address', 'title', 'point', 'url', 'condition', 'contact'])

    # 'keyword' 컬럼에서 지역 이름 추출 (공백으로 구분된 첫 번째 단어)
    data['region'] = data['keyword'].str.split().str[0]

    # 줄바꿈 문자를 <br>로 변환
    data['condition'] = data['condition'].str.replace('\n', '<br>', regex=False)

    # 중복된 지역 이름 제거 후 리스트로 변환
    regions = sorted(data['region'].unique().tolist())

    # 필요한 컬럼을 딕셔너리로 변환
    locations = data[['title', 'address', 'point', 'url', 'region', 'condition', 'contact']].to_dict(orient='records')

    # 템플릿에 데이터 전달
    return render_template('index.html', locations=locations, regions=regions)

if __name__ == '__main__':
    app.run(debug=True)
    