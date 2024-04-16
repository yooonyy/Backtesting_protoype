import pandas as pd
from typing import Callable, Tuple
import warnings
from strategies import Strategies
from visualize_v3 import visualize

class Base_setting():

    def __init__(self, 
                 data: pd.DataFrame
                 ,investment_period: Tuple[str, str]
                 ,initial_investment: int
                 ) :
        """
        Backtesting 클래스 초기화

        Parameters:
        - data: pd.DataFrame, 백테스팅에 사용될 데이터
        - investment_period: Tuple[str, str], 투자 기간 (시작 날짜, 종료 날짜) 형태
        - initial_investmetn: int, 초기 투자금액
        """

        self.data = data
        self.investment_period = investment_period
        self.start_date = investment_period[0]
        self.end_date = investment_period[1]
        self.initial_investment = initial_investment
        self.strategy = Strategies(data=self.data)

    def check_duplicate_indices(data: pd.DataFrame):
        """
        Check for duplicate indices in the DataFrame.

        Parameters:
        - data: pd.DataFrame, input DataFrame

        Returns:
        - None
        """
        # Check for duplicate indices
        duplicate_indices = data.index.duplicated().any()
        num_of_duplicate = data.index.duplicated().sum()
        if duplicate_indices:
            print(f"{num_of_duplicate} Duplicate indices exist.")
            print("Check out with .index.duplicated() function")
        else:
            print("No duplicate indices.")




    def pointer(self,date):
        '''
        input에 해당하는 특정 날짜의 index
        
        Parameters:
        - date: str, 특정 날짜 예시 '2014-04-25'

        Returns:
        - int: 특정 날짜가 해당하는 데이터 인덱스 숫자 (iloc에 바로 집어넣을)
        '''
        try:
            start_point = len(self.data.loc[:date]) - 1
            return start_point
        except KeyError:
            warnings.warn("The date provided is not a trading day.", UserWarning)
            return None
        
    def inverse_pointer(self,date,days):
        
        '''
        특정 날짜 이전의 데이터 인덱스를 찾고, 해당 인덱스로부터 일정 일수 이후의 날짜를 찾는 메서드

        Parameters:
        - date: str, 특정 날짜 예시 '2014-04-25'
        - days: int, 해당 날짜에서 days 영업일 만큼 뒤를 지칭  

        Returns:
        - str: 특정 날짜에서 days 만큼의 영업일 이후의 날짜 (%Y-%m-%d 형식)
        '''
        
        sp = self.pointer(date)

        try:
            the_date = self.data.iloc[sp + days:sp + days + 1, :].index.strftime('%Y-%m-%d')
            the_date = the_date[0]
            return the_date
        except IndexError:
            warnings.warn("No date found for the given parameters.", UserWarning)
            return None

    def weight_to_num(self,weights):
        '''
        주어진 가중치에 따라 각 주식의 구매가능 수량을 계산하는 메서드

        Parameters:
        - weights: dict, 각 주식에 대한 가중치
        예시 ) weight = {'AAPL' : 0.2,
              'GOOG' : 0.2,
              'PEP' : 0.2,
              'KO' : 0.1,
              'MSFT' : 0.1,
              'NVDA' : 0.1,
              'AMZN' : 0.1  
              }

        Returns:
        - pd.Series: 초기 투자 금액와 주어진 비중에 따라 구매 가능한 주식 수량 (Series)
        '''
        # 해당 날짜의 주식 가격 정보 (Series)
        stock_price = self.data.loc[self.start_date]

        port_weight = pd.Series(index=stock_price.index,data=weights)

       # 보유 수량 계산
        port_num = (port_weight * self.initial_investment) / stock_price
        
        # NaN 값은 0으로 채우기
        port_num = port_num.fillna(0)

        # 에러가 발생할 수 있는 부분에 대한 예외 처리
        try:
            assert not port_num.isnull().values.any()  # NaN 값이 없어야 함
        except AssertionError:
            warnings.warn("NaN values found in the computed portfolio.\
                           Check your input data and weights.", UserWarning)

        return port_num  # 각 주식에 대한 보유 수량 (Series)
        
    def calculate_port_value(self,port_num):
        """
        # 현재는 구매 가능 수량 = 구매 수량으로 가정하여, 주문 체결 여부를 따지지 않음

        주어진 구매 수량을 기반으로 내 포트폴리오의 종목별 보유 금액과, 총 평가손익을 나타내는

        내 포트폴리오 투자 종목에 따른 계좌 dataframe 출력

        Parameters:
        - port_num : pd.series, weigth_to_num 결과값인 구매한 종목의 갯수 
        """
        # Slicing the data for the investment period
        df_period = self.data.loc[self.start_date:self.end_date] #Dataframe now
        
       # Handling potential errors: Check if the indices of df_period and port_num are the same
        if not df_period.columns.equals(port_num.index):
            warnings.warn("The indices of df_period and port_num are not the same.\
                           Check your input data and weights.", UserWarning)
    
        # Calculating the portfolio value by multiplying the holdings with the prices of each stock
        my_port = df_period * port_num 

        ### 여기에 거래 대금을 정의하는 로직 추가 ###

        # Calculating and adding the total value of the portfolio for each date
        my_port['Total_value'] = my_port.sum(axis=1)

        # Comment updated: The total value of the portfolio for each date during the investment period can be used as the overall portfolio value
        
        return my_port  # DataFrame representing the value of the portfolio during the investment period 
       
    def port_return(self, my_port):
        '''
        Method to calculate the total return and cumulative return of the portfolio.
        calculate_port_value를 통해 받은 my_port 데이터의 수익률과 누적 수익률 재가공 메서드

        Parameters:
        - my_port : pd.DataFrame, DataFrame representing the value of the portfolio during the investment period

        Returns:
        - pd.DataFrame: DataFrame containing the total return and cumulative return of the portfolio
        '''

        # 포트폴리오의 총 수익 및 누적 수익을 계산하는 메서드입니다.
        # Method to calculate the total return and cumulative return of the portfolio.

        # 포트폴리오의 가치 변화율을 각 날짜별로 계산합니다.
        # Calculating the percentage change of the portfolio value for each date
        port_return = my_port.pct_change().iloc[1:].fillna(0)
        
        # 'Total_value' 열의 이름을 'Total_return'으로 변경하여 명확하게 표시합니다.
        # Renaming the column 'Total_value' to 'Total_return' for clarity
        port_return = port_return.rename(columns={'Total_value': 'Total_return'})
        
        # 포트폴리오의 누적 수익을 계산합니다.
        # Calculating the cumulative return of the portfolio
        port_return['Cum_return'] = (1 + port_return['Total_return']).cumprod() - 1

        return port_return  # 포트폴리오의 총 수익과 누적 수익을 담고 있는 DataFrame을 반환합니다.
        # DataFrame containing the total return and cumulative return of the portfolio

    def run_all(self, weights):
        '''
        Method to execute all necessary steps for portfolio return analysis.

        Parameters:
        - weights: dict, dictionary containing the weights of each asset in the portfolio

        Returns:
        - pd.DataFrame: DataFrame containing the total return and cumulative return of the portfolio
        '''
        # 포트폴리오 수익률 df 까지 필요한 모든 단계를 실행하는 메서드입니다.

        # 주어진 가중치를 기반으로 포트폴리오 내 각 자산의 보유량을 계산합니다.
        # Calculating the holdings of each asset in the portfolio based on the given weights
        port_num = self.weight_to_num(weights)

        # 포트폴리오의 보유량을 기반으로 포트폴리오의 가치를 계산합니다.
        # Calculating the value of the portfolio based on the holdings
        my_port = self.calculate_port_value(port_num)

        # 포트폴리오의 수익률 및 누적 수익률을 계산합니다.
        # Calculating the return and cumulative return of the portfolio
        port_return = self.port_return(my_port)

        return port_return  # 포트폴리오의 총 수익과 누적 수익을 담고 있는 DataFrame을 반환합니다.
        # DataFrame containing the total return and cumulative return of the portfolio

    def benchmark_return(self,benchmark_data):
        #기간 미 설정 시 self 기간 사용

        bench_return = benchmark_data.loc[self.start_date:self.end_date]
        bench_return = bench_return.pct_change().iloc[1:]
        bench_return['Cum_return'] = (1+bench_return['Close']).cumprod()-1

        return bench_return

    def benchmark_full_return(self,benchmark_data):
        
        start_idx = self.pointer(self.start_date)
        bench_return = benchmark_data.iloc[start_idx:]
        bench_return = bench_return.pct_change().iloc[1:]
        bench_return['Cum_return'] = (1+bench_return['Close']).cumprod()-1

        return bench_return

    def algorithm_rebalancing(self,function=None,window=None):
        '''
        Method to rebalance the portfolio using the specified algorithm 
        지정된 비중 조절 알고리즘의 함수를 호출하고, 입력받은 리밸런싱 주기에 따라 비중을 조절한 포트폴리오를 반환하는 메서드입니다.
        Parameters:
        - function: function, optional, function to generate portfolio weights (default is None)
        - window: int, optional, window size for calculating weights (default is None)

        Returns:
        - pd.DataFrame: DataFrame containing the rebalanced portfolio by given function
        '''
        # 함수가 지정되지 않았을 경우, 기본 리밸런싱 함수인 momentum_vol_weighted를 사용합니다.
        # If no function is specified, use the default rebalancing function momentum_vol_weighted.
        if function is None:
            function = self.strategy.momentum_vol_weighted
        # 리밸런싱 주기가 지정되지 않았을 경우, 기본적으로 1년(=252 영업일)을 활용합니다.
        #If the rebalancing period is not specified, it defaults to one year (252 trading days).
        if window is None:
            n = 252
        else:
            n = window

        #while 구문에서, 계산되기 전 초기 값을 설정해줍니다.
        # Set the initial value before the calculation in the while loop.
        full_port = None
        
        # 리밸런싱은 n 값에 따라 진행하므로, investment_period도 n에 맞게 기간을 수정해야함!
        ip = self.investment_period
        end_date = self.inverse_pointer(ip[0],n)
        ip = (ip[0],end_date)
        # 위 과정이 없을 경우, i_p 구간과 n 값이 같지 않을 때 코드 오류 발생
        inv = self.initial_investment
        start_idx = self.data.index.get_loc(self.start_date)
        final_idx = len(self.data)-1

        while start_idx + 2*n < final_idx:
            
            setting = Base_setting(self.data,ip,inv)

            weights = function(investment_period=setting.investment_period,window=n)
            
            port_part = setting.weight_to_num(weights)
            port_part = setting.calculate_port_value(port_part)

            #리밸런싱 주기에 맞도록 다음 포트폴리오 계산을 위해 parameter 값을 업데이트 합니다.
            # Update the parameter values for the next portfolio calculation according to the rebalancing period.
            next_start_date = setting.inverse_pointer(ip[0],n)
            next_end_date = setting.inverse_pointer(ip[1],n)
            ip = (next_start_date,next_end_date)
            inv = port_part.iloc[-1,-1]
            start_idx = setting.pointer(ip[0])
            
            # 첫 iteration 일 경우, 초기 dataframe을 할당해줍니다.
            # Assign the initial dataframe if it is the first iteration.
            if full_port is None:
                full_port = port_part
            # 이후 iteration이 진행되면서, 누적되는 df 들을 하나의 df에 통합시킵니다.
            # As iterations progress, integrate the accumulating dataframes into one dataframe.
            else:
                full_port = pd.concat([full_port,port_part],join='inner')

        # 백테스팅할 기간이 window_size=n 보다 적게 남아서 iteration이 끝나고 잔여기간에 맞게 parameter를 재설정합니다.
        day_left = final_idx - start_idx
        new_end_date = setting.inverse_pointer(ip[0],day_left)
        ip = (ip[0],new_end_date)
        
        setting = Base_setting(self.data,ip,inv)
        weights = function(investment_period=setting.investment_period,window=n)
        port_part = setting.weight_to_num(weights)
        port_part = setting.calculate_port_value(port_part)
        full_port = pd.concat([full_port,port_part],join='inner')

        return full_port
        
    def by_hand_rebalancing(self, window=None):
        '''
        Method to manually rebalance the portfolio by entering weights directly.
        사용자가 직접 가중치를 입력하여 포트폴리오의 비중을 조절하는 메서드입니다.
        Parameters:
        - window: int, optional, window size for calculating weights (default is 252 trading days)
        
        Returns:
        - pd.DataFrame: DataFrame containing the rebalanced portfolio with manually entered weights
        '''
        if window is None:
            n = 252
        else:
            n = window

        full_port = None

        # 리밸런싱은 n 값에 따라 진행하므로, investment_period도 n에 맞게 기간을 수정해야함!
        ip = self.investment_period
        end_date = self.inverse_pointer(ip[0],n)
        ip = (ip[0],end_date)
        # 위 과정이 없을 경우, i_p 구간과 n 값이 같지 않을 때 코드 오류 발생
        inv = self.initial_investment
        start_idx = self.data.index.get_loc(self.start_date)
        final_idx = len(self.data)-1

        while start_idx + 2*n < final_idx:
            setting = Base_setting(self.data, ip, inv)
            
            # 사용자로부터 포트폴리오 가중치를 직접 입력받습니다. 사용자는 딕셔너리 형태로 가중치를 입력해야 합니다.
            weights = input("Enter weights in dictionary format & UPPER CASE!: ")
            weights = eval(weights)
            
            port_part = setting.weight_to_num(weights)
            port_part = setting.calculate_port_value(port_part)

            # 다음 포트폴리오 계산을 위해 parameter 값을 업데이트 합니다.
            next_start_date = setting.inverse_pointer(ip[0], n)
            next_end_date = setting.inverse_pointer(ip[1], n)
            ip = (next_start_date, next_end_date)
            inv = port_part.iloc[-1, -1]
            start_idx = setting.pointer(ip[0])

            if full_port is None:
                full_port = port_part
            else:
                full_port = pd.concat([full_port, port_part], join='inner')

            full_port_return = setting.port_return(full_port)
            visualize(full_port_return)
            

        # 잔여 기간에 맞게 parameter를 재설정합니다.
        day_left = final_idx - start_idx
        new_end_date = setting.inverse_pointer(ip[0], day_left)
        ip = (ip[0], new_end_date)
        
        setting = Base_setting(self.data, ip, inv)

        weights = input("Enter weights in dictionary format: ")
        weights = eval(weights)
        
        port_part = setting.weight_to_num(weights)
        port_part = setting.calculate_port_value(port_part)
        full_port = pd.concat([full_port, port_part], join='inner')

        return full_port
