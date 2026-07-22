import os
import sys
import sqlite3
import pandas as pd

# 과제 2·3의 함수를 week4/main.py로 복사해 통합
DATA_PATH = "/Users/seoin/Desktop/KANT AI/spending-project/data/spending.csv"
DB_PATH = "/Users/seoin/Desktop/KANT AI/spending-project/data/spending.db"

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

# 과제 2 함수 재사용

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

# 과제 3 함수 재사용
def init_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS spendings")

    cursor.execute("""
        CREATE TABLE spendings (
            record_id TEXT PRIMARY KEY,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            item TEXT NOT NULL,
            amount INTEGER NOT NULL,
            payment TEXT NOT NULL,
            memo TEXT,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            day INTEGER NOT NULL,
            amount_level TEXT NOT NULL
        )
    """)

    conn.commit()

    print("테이블 생성 완료")

    return conn

def save_to_db(df, conn):
    df.to_sql(
        "spendings",
        conn,
        if_exists="append",
        index=False
    )

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM spendings")

    db_count = cursor.fetchone()[0]

    print(f"{len(df)}행 저장 완료 (DB 내 행 수: {db_count})")

# 기본 조회
def basic_query(conn):
    # 전체 데이터 중 상위 5행 조회
    top5_df = pd.read_sql(
        """
        SELECT *
        FROM spendings
        LIMIT 5
        """,
        conn
    )

    # 필요한 컬럼만 선택하여 조회
    selected_columns_df = pd.read_sql(
        """
        SELECT record_id, date, category, amount
        FROM spendings
        LIMIT 5
        """,
        conn
    )

    print("\n===== 전체 데이터 상위 5행 =====")
    print(top5_df)

    print("\n===== 필요한 컬럼만 조회 =====")
    print(selected_columns_df)

    return top5_df, selected_columns_df

# 조건 조회
def conditional_query(conn):
    # 식비 데이터를 금액이 높은 순서로 조회
    category_meal_df = pd.read_sql(
        """
        SELECT *
        FROM spendings
        WHERE category = '식비'
        ORDER BY amount DESC
        """,
        conn
    )

    # 3만 원 이상이면서 카드 결제인 데이터 조회
    payment_card_df = pd.read_sql(
        """
        SELECT *
        FROM spendings
        WHERE amount >= 30000
          AND payment = '카드'
        ORDER BY amount DESC
        """,
        conn
    )

    # print("\n===== 식비 금액 내림차순 =====")
    # print(category_meal_df)

    # print("\n===== 3만 원 이상 카드 결제 =====")
    # print(payment_card_df)

    print(f"\n3만 원 이상 카드 결제 건수: {len(payment_card_df)}건")

    return category_meal_df, payment_card_df

# 집계 조회
def aggregate_query(conn):
    # 카테고리별 집계
    category_summary_df = pd.read_sql(
        """
        SELECT
            category,
            COUNT(*) AS 건수,
            SUM(amount) AS 총지출액,
            CAST(ROUND(AVG(amount)) AS INTEGER) AS 평균지출액,
            MAX(amount) AS 최대지출액
        FROM spendings
        GROUP BY category
        ORDER BY 총지출액 DESC
        """,
        conn
    )

    # 월별 집계
    monthly_summary_df = pd.read_sql(
        """
        SELECT
            month,
            COUNT(*) AS 건수,
            SUM(amount) AS 총지출액
        FROM spendings
        GROUP BY month
        ORDER BY month ASC
        """,
        conn
    )

    print("\n===== 카테고리별 집계 =====")
    print(category_summary_df)

    print("\n===== 월별 총지출 =====")
    print(monthly_summary_df)

    return category_summary_df, monthly_summary_df

def verify_with_python(df, conn):
    # Python의 groupby로 카테고리별 총지출 계산
    python_result = (
        df.groupby("category", as_index=False)["amount"]
        .sum()
        .rename(columns={"amount": "python_total"})
    )

    # SQL의 GROUP BY로 카테고리별 총지출 계산
    sql_result = pd.read_sql(
        """
        SELECT
            category,
            SUM(amount) AS sql_total
        FROM spendings
        GROUP BY category
        """,
        conn
    )

    # category를 기준으로 두 결과 합치기
    comparison_df = pd.merge(
        python_result,
        sql_result,
        on="category",
        how="outer"
    )

    # Python 결과와 SQL 결과가 같은지 비교
    comparison_df["일치"] = (
        comparison_df["python_total"]
        == comparison_df["sql_total"]
    )

    all_match = comparison_df["일치"].all()

    print("\n===== Python vs SQL 검증 =====")
    print(f"\n전체 카테고리 일치: {all_match}")

    return comparison_df


# 과제 4 심화 과제 코드
def advanced_query(conn):
    payment_month_df = pd.read_sql("""
        SELECT 
            month, 
            payment,
            COUNT(*) AS 건수,
            SUM(amount) AS 총지출액
        FROM spendings
        GROUP BY month, payment
        ORDER BY month
    """, conn)


    weekday_df = pd.read_sql("""
        SELECT 
            strftime('%w', date) AS weekday,
            COUNT(*) AS 건수,
            SUM(amount) AS 총지출액,
            CAST(ROUND(AVG(amount)) AS INTEGER) AS 평균지출액
        FROM spendings
        GROUP BY weekday
        ORDER BY weekday
    """, conn)

    print("\n===== 카드/현금 월별 지출 =====")
    print(payment_month_df)

    print("\n===== 요일별 지출 =====")
    print(weekday_df)

    return payment_month_df, weekday_df


# 과제 4 신규 코드
def main():
    df = load_data(DATA_PATH)
    df = parse_dates(df)
    df = standardize_category(df)
    df = add_amount_level(df)
    df = clean_values(df)
    
    conn = init_db(DB_PATH)
    
    try:
        save_to_db(df, conn)

        basic_query(conn)
        conditional_query(conn)
        aggregate_query(conn)

        verify_with_python(df, conn)
    
        advanced_query(conn)

    finally:
        conn.close()
        print("\nDB 연결 종료")


if __name__ == "__main__":
    main()


# ============================================================
# 결제 수단 및 요일별 지출 패턴 분석
# ============================================================

# 현재 데이터는 1월부터 3월까지의 소비 데이터를 포함한다.
# 모든 달에서 카드 결제 금액이 현금 결제 금액보다 크게 나타났으며, 특히 3월의 카드 지출이 가장 높았다.
# 이는 한국에서 카드 결제가 널리 사용되는 소비 문화가 반영된 결과일 가능성이 있다.
# 요일별 지출 패턴에서는 토요일(weekday=6)의 총지출액(288,690원)과 평균지출액(22,207원)이 가장 높게 나타났다.
# 반면 수요일(weekday=3)은 총지출액(135,500원)과 평균지출액(11,292원)으로 가장 낮은 소비 패턴을 보였다.
# 이러한 결과는 주말에는 외식, 쇼핑, 여가 활동 등 비교적 지출 규모가 큰 소비가 집중되는 반면, 
# 평일 중 수요일에는 업무나 학업 중심의 생활로 인해소비가 상대적으로 적기 때문으로 해석할 수 있다.
# 또한 3월의 지출 증가 역시 계절 변화, 새 학기 및 새 시즌 준비, 다양한 할인 행사 등의 영향이 있었을 가능성이 있다.