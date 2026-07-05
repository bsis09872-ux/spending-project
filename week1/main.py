import pandas as pd
import numpy as np
import os
import sys

DATA_PATH = "/Users/seoin/Desktop/KANT AI/spending-project/data/spending.csv"

# 기능 1

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

# 기능 2

def explore_structure(df):
    print("\n\n[1] 데이터 구조 확인")

    print("======== 데이터 크기 ========")
    print(df.shape)

    print("\n======== 컬럼 목록 ========")
    for column in df.columns:
        print(column)

    print("\n======== 컬럼별 자료형 ========")
    for column, dtype in df.dtypes.items():
        print(f"{column} : {dtype}")

    print("\n======== 상위 5개 데이터 ========")
    print(df.head(5))

# 기능 3

def show_distribution(df):
    print("\n\n[2] 분포 확인")

    ### 결과를 저장할 딕셔너리
    result = {}

    ## 1. 카테고리별 건수 및 비율
    total_count = len(df)

    category_counts = df["category"].value_counts()
    category_ratio = category_counts / total_count * 100

    print("\n======== 카테고리별 건수 및 비율 ========")
    for category, count in category_counts.items():
        ratio = category_ratio[category]
        print(f"{category}: {count}건 ({ratio:.2f}%)")

    result["category_counts"] = category_counts.to_dict()
    result["category_ratio"] = category_ratio.to_dict()


    ## 2. 결제수단별 건수 및 비율
    payment_counts = df["payment"].value_counts()
    payment_ratio = payment_counts / total_count * 100

    print("\n======== 결제수단별 건수 및 비율 ========")
    for payment, count in payment_counts.items():
        ratio = payment_ratio[payment]
        print(f"{payment}: {count}건 ({ratio:.2f}%)")

    result["payment_counts"] = payment_counts.to_dict()
    result["payment_ratio"] = payment_ratio.to_dict()

    ## 3. 카테고리별 평균 금액
    category_avg_amount = {}

    print("\n======== 카테고리별 평균 금액 ========")

    for cat in df["category"].unique():
        filtered_df = df[df["category"] == cat]
        avg_amount = filtered_df["amount"].mean()
        category_avg_amount[cat] = avg_amount

        print(f"{cat}: {avg_amount:.2f}원")

    result["category_average"] = category_avg_amount

    return result

# 기능 4
def check_missing(df):
    print("\n\n[3] 결측치 현황 파악")
    
    result = {}

    total_count = len(df)
    ### missing_map = df.isnull()
    missing_counts = df.isnull().sum()
    ### missing_counts = missing_map.sum() 과 동일

    missing_columns = {}
    no_missing_columns = []

    print("\n======== 결측치 현황 ========")

    for col in df.columns:
        missing_count = missing_counts[col]
        missing_ratio = missing_count / total_count * 100

        if missing_count > 0:

            if missing_ratio >= 20:
                severity = "높음"
            elif missing_ratio >= 5:
                severity = "주의"
            else:
                severity = "낮음"

            missing_columns[col] = {
                "count" : int(missing_count),
                "ratio" : float(missing_ratio),
                "severity" : severity
            }

            print(f"{col}: {missing_count}개 ({missing_ratio:.2f}%)")
            print(f"심각도: {severity}")

        else:
            no_missing_columns.append(col)
            

    print("\n======== 결측치 없는 컬럼 ========")

    for col in no_missing_columns:
        print(col)
    
    result["missing_columns"] = missing_columns
    result["no_missing_columns"] = no_missing_columns

    return result


# 기능 5
def numpy_amount_stats(df):
    print("\n\n[4] NumPy 통계 분석")

    ## 1. amount 컬럼 선택 및 결측치 제거
    amounts = df["amount"].dropna()

    ## 2. NumPy 배열로 변환
    amounts_arr = np.array(amounts)

    ## 3. NumPy 통계량 계산
    mean_value = np.mean(amounts_arr)
    std_value = np.std(amounts_arr, ddof=1)
    median_value = np.median(amounts_arr)
    min_value = np.min(amounts_arr) 
    max_value = np.max(amounts_arr)

    ## 4. 5만원 초과 지출 추출
    over_amounts = amounts_arr[amounts_arr > 50000]

    ## 5. 결과 출력
    print("\n======== NumPy 통계 분석 ========")
    print(f"평균: {mean_value:.2f}")
    print(f"표준편차: {std_value:.2f}")
    print(f"중앙값: {median_value:.2f}")
    print(f"최솟값: {min_value}")
    print(f"최댓값: {max_value}")

    print("\n======== 5만 원 초과 지출 ========")
    print(over_amounts)

    ## 6. NumPy vs. Pandas
    describe = amounts.describe()

    print("\n======== pandas describe() 결과 ========")
    print(describe)

    print("\n======== NumPy vs. Pandas ========")
    print(
    f"평균    : NumPy = {mean_value:.2f} | Pandas = {describe['mean']:.2f} "
    f"| {'✓ 일치' if round(mean_value, 2) == round(describe['mean'], 2) else '✗ 불일치'}"
    )

    print(
    f"표준편차: NumPy = {std_value:.2f} | Pandas = {describe['std']:.2f} "
    f"| {'✓ 일치' if round(std_value, 2) == round(describe['std'], 2) else '✗ 불일치'}"
    )

    print(
    f"중앙값  : NumPy = {median_value:.2f} | Pandas = {describe['50%']:.2f} "
    f"| {'✓ 일치' if round(median_value, 2) == round(describe['50%'], 2) else '✗ 불일치'}"
    )

    print(
    f"최솟값  : NumPy = {min_value:.2f} | Pandas = {describe['min']:.2f} "
    f"| {'✓ 일치' if min_value == describe['min'] else '✗ 불일치'}"
    )

    print(
    f"최댓값  : NumPy = {max_value:.2f} | Pandas = {describe['max']:.2f} "
    f"| {'✓ 일치' if max_value == describe['max'] else '✗ 불일치'}"
    )
    

# 기능 6
def main():
    df = load_data(DATA_PATH)

    explore_structure(df)
    show_distribution(df)
    check_missing(df)
    numpy_amount_stats(df)

if __name__ == "__main__":
    main()


