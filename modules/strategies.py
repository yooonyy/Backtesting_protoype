import pandas as pd
from typing import Callable, Tuple

class Strategies:

    def __init__(self, data: pd.DataFrame):
        self.data = data

    def momentum_performance_weigthed(self, investment_period: Tuple[str, str], window: int) -> pd.Series:
        try:
            start_date, end_date = investment_period
        except KeyError:
            print("Warning: Not enough past data to backtest")
            return pd.Series()

        try:
            # iloc build up
            start_idx = self.data.index.get_loc(start_date)
        except KeyError:
            print(f"Start date {start_date} not found in data.")
            return pd.Series()

        if start_idx < window:
            at_least = self.data.iloc[window].name
            print("Warning: Not enough past data to calculate momentum weights.")
            print(f"Data must include at least up to {at_least} for the given window size.")
            return pd.Series()

        # 필요한 기간에 대한 데이터 필터링
        filtered_data = self.data.iloc[start_idx-window-1:start_idx-1]

        # 가격 데이터의 변동률 계산
        price_pct_change = filtered_data.pct_change(periods=window-1)

        # 마지막 행(최근 데이터)의 모멘텀 점수 계산
        momentum_score = price_pct_change.iloc[-1] #series 반환

        # 모멘텀 점수를 기반으로 5분위 계산
        quantiles = momentum_score.quantile([0.2, 0.4, 0.6, 0.8])

        # 자산을 5분위로 분류하고 각 분위별 가중치 할당
        weights = dict()
        num = len(momentum_score)/5
        up_80 = momentum_score[momentum_score>quantiles[0.2]]
        min_val = up_80.min()   # 이걸 그냥 더하면 음수일 경우에, 결국 new_score에서 여전히 음수 존재!
        to_add = abs(min_val)   # 패치버젼
        new_score = up_80+to_add
        #new_score = up_80+min_val
        total = new_score.sum()

        for idx, value in momentum_score.items():
            if value <= quantiles[0.2]: # do not buy bottom 20%
                weights[idx] = 0
            else:
                weights[idx] = (value+to_add) / total
                # still has a problem when market is going down
                # we still have to allocate some weights to underperforming stocks
        
        return weights

    def momentum_performance_quantile(self, investment_period: Tuple[str, str], window: int) -> pd.Series:
        try:
            start_date, end_date = investment_period
        except KeyError:
            print("Warning: Not enough past data to backtest")
            return pd.Series()

        try:
            # iloc build up
            start_idx = self.data.index.get_loc(start_date)
        except KeyError:
            print(f"Start date {start_date} not found in data.")
            return pd.Series()

        if start_idx < window:
            at_least = self.data.iloc[window].name
            print("Warning: Not enough past data to calculate momentum weights.")
            print(f"Data must include at least up to {at_least} for the given window size.")
            return pd.Series()

        # 필요한 기간에 대한 데이터 필터링
        filtered_data = self.data.iloc[start_idx-window-1:start_idx-1]

        # 가격 데이터의 변동률 계산
        price_pct_change = filtered_data.pct_change(periods=window-1)

        # 마지막 행(최근 데이터)의 모멘텀 점수 계산
        momentum_score = price_pct_change.iloc[-1]

        # 모멘텀 점수를 기반으로 5분위 계산
        quantiles = momentum_score.quantile([0.2, 0.4, 0.6, 0.8])

        # 자산을 5분위로 분류하고 각 분위별 가중치 할당
        weights = dict()
        num = len(momentum_score)/5

        for idx, value in momentum_score.items():
            if value <= quantiles[0.4]: #임의로 4,5분위는 동일 비중 할당
                weights[idx] = 0.1/(2*num)
            elif value <= quantiles[0.6]:
                weights[idx] = 0.2/num
            elif value <= quantiles[0.8]:
                weights[idx] = 0.3/num
            else:
                weights[idx] = 0.4/num

        return weights

    def momentum_vol_weighted(self, investment_period: Tuple[str, str], window: int) -> pd.Series:
        # momentum_vol_weighted
        try:
            start_date, end_date = investment_period
        except KeyError:
            print(f"Warning: Not enough past data to backtest")
            return pd.Series()

        # investment_period의 시작 날짜 이전 데이터 포인트 수 확인
        try:
            #iloc build up
            start_idx = self.data.index.get_loc(start_date)
        except KeyError:
            print(f"Start date {start_date} not found in data.")
            return pd.Series()
        
        # 필요한 과거 데이터 포인트가 충분한지 확인
        if start_idx < window:
            at_least = self.data.iloc[window].name
            print("Warning: Not enough past data to calculate momentum weights.")
            print(f"Data must include at least up to {at_least} for the given window size.")
            return pd.Series()

        # 필요한 기간에 대한 데이터 필터링
        filtered_data = self.data.iloc[start_idx-window-1:start_idx-1]

        # 가격 데이터의 변동률 계산
        price_pct_change_m = filtered_data.pct_change(periods=window-1)
        price_pct_change = filtered_data.pct_change()

        # 모멘텀 점수 계산
        momentum_score= price_pct_change_m.iloc[-1]
        #momentum_score = price_pct_change.rolling(window=window-1).mean().iloc[-1]
        #위 모멘텀은 기간 평균 수익률

        # 변동성 계산
        volatility = price_pct_change.rolling(window=window-1).std().iloc[-1]

        # 변동성으로 조정된 모멘텀 점수 계산
        adjusted_momentum = momentum_score / volatility

        # 양의 모멘텀만 선택
        positive_momentum = adjusted_momentum[adjusted_momentum > 0]
    
        # 양의 모멘텀을 가진 자산들에 대한 변동성 조정 가중치 계산
        weights_vol_adjusted = positive_momentum / positive_momentum.sum()

        #dictionary로 반환
        weights = weights_vol_adjusted.to_dict()

        return weights