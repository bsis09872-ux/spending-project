import pandas as pd
import numpy as np
import os
import sys

DATA_PATH = "/Users/seoin/Desktop/KANT AI/spending-project/data/spending.csv"
CLEAN_DATA_PATH = "/Users/seoin/Desktop/KANT AI/spending-project/data/spending_clean.csv"

# 과제 1 함수 재사용

def load_data(file_path):
    ## 1. 파일 존재 여부 확인
    if not os.path.exists(file_path):
        print(f"파일을 찾을 수 없습니다: {file_path}")
        sys.exit(1)

    ## 2. CSV 파일 읽기 (한글 인코딩까지 고려)
    df = pd.read_csv(file_path, encoding="utf-8-sig")

    ## 3. 데이터 크기 출력
    print(f"데이터 로드 완료: {df.shape[0]}행 × {df.shape[1]}열")

    ## 4. DataFrame 반환
    return df

# 기능 1

def parse_dates(df):
    df["date"] = pd.to_datetime(
    df["date"],
    format="%Y-%m-%d",
    errors="coerce"
)
    date_NaT = df['date'].isna().sum()
    print(f"날짜 변환 실패: {date_NaT}건")

    df["year"] =  df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day

    print("\n======== 날짜 변환 결과 확인용 ========")
    print(df[["date", "year", "month", "day"]].head(5))
    print(df.columns)

    return df


# 기능 2

def standardize_category(df):
   allowed_categories = ["식비", "교통", "쇼핑", "의료", "문화", "기타"]

   def clean_categories(value):
       if not isinstance(value, str):
           return "기타"
       
       value = value.strip()

       if value in allowed_categories:
           return value
       else: 
           return "기타"
        
   df["category"] = df["category"].apply(clean_categories)

   print("\n===== 카테고리 표준화 결과 ======")
   print(df["category"].value_counts())

   return df


# 기능 3
def add_amount_level(df):
        
        def amount_level_categories(amount):
            if amount < 10000:
                return "소액"
            elif amount < 50000:
                return "중액"
            else:
                return "고액"

        df["amount_level"] = df["amount"].apply(amount_level_categories)

        print("\n===== 금액 구간 분포 =====")
        print(df["amount_level"].value_counts())

        return df


# 기능 4
def clean_values(df):
    before_count = len(df)
    
    df["memo"] = df["memo"].fillna("")

    df = df[df["amount"] > 0]

    df = df.dropna(subset=["date"])

    df = df.reset_index(drop=True)

    after_count = len(df)

    print("\n===== 결측·이상값 처리 결과 =====")
    print(f"처리 전 행 수: {before_count}행")
    print(f"처리 후 행 수: {after_count}행")
    print(f"제거된 행 수: {before_count - after_count}행")
    print(f"memo 결측치 수: {df['memo'].isna().sum()}건")

    return df


# 기능 5
def show_summary(df):
    print("\n===== 월별 총 지출 =====")
    monthly_sum = df.groupby("month")["amount"].sum()
    print(monthly_sum)

    print("\n===== 항목별 총 지출 (많은 순) =====")
    category_sum = df.groupby("category")["amount"].sum()
    category_sum = category_sum.sort_values(ascending=False)
    print(category_sum)
    
    return df


# 기능 6
def main():
    df = load_data(DATA_PATH)

    df = parse_dates(df)
    df = standardize_category(df)
    df = add_amount_level(df)
    df = clean_values(df)
    df = show_summary(df)

    # date를 문자열로 변환
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    # CSV 저장
    df.to_csv(
        CLEAN_DATA_PATH,
        index=False,
        encoding="utf-8-sig"
    )
    print("\n정제 데이터 저장 완료!")

if __name__ == "__main__":
    main()


