import os
import sqlite3
import pandas as pd


CLEAN_DATA_PATH = "/Users/seoin/Desktop/KANT AI/spending-project/data/spending_clean.csv"
DB_PATH = "/Users/seoin/Desktop/KANT AI/spending-project/data/spending.db"


# 정제 CSV 불러오기
def load_clean_data(file_path):
    if not os.path.exists(file_path):
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return None

    df = pd.read_csv(file_path, encoding="utf-8-sig")

    print(f"데이터 로드 완료: {df.shape[0]}행 × {df.shape[1]}열")

    return df


# 기능 1: DB 연결 + 테이블 생성
# <핵심 개념>
# Table: 데이터를 행과 열로 저장하는 구조
# Primary Key: 각 행을 고유하게 구분하는 컬럼 (중복과 NULL을 허용하지 않음)
# NOT NULL: 해당 컬럼에 빈 값을 허용하지 않음
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


# 기능 2: 정제 데이터 저장
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


# 기능 3: 기본 조회
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


# 기능 4: 조건 조회
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


# 기능 5: 집계 조회
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


# 기능 6: Python 집계와 SQL 집계 비교
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


# 전체 기능 연결
def main():
    df = load_clean_data(CLEAN_DATA_PATH)

    if df is None:
        return

    conn = init_db(DB_PATH)

    save_to_db(df, conn)
    basic_query(conn)
    conditional_query(conn)
    aggregate_query(conn)
    verify_with_python(df, conn)

    conn.close()
    print("\nDB 연결 종료")


if __name__ == "__main__":
    main()