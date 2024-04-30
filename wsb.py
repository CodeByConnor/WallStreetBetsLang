import requests # for HTTP requests (e.g., for fetching data from the internet)
import threading # multithread I/O calls
import time # timer
import pandas as pd # data analysis and manipulation ( nasdaq tickers )
import os # debug my own directory
from textx import metamodel_from_file
 
try:
    # loading in our grammar and sample hello_world.wsb program     
    hello_meta = metamodel_from_file('wsb.tx')
    hello_model = hello_meta.model_from_file('hello_world.wsb')

    # loading in our grammar and sample yolo_tsla.wsb program     
    yolo_tsla_meta = metamodel_from_file('wsb.tx')
    yolo_tsla_model = yolo_tsla_meta.model_from_file('yolo_tsla.wsb')

     # loading in our grammar and input.wsb program
    input_meta = metamodel_from_file('wsb.tx')
    input_model =input_meta.model_from_file('input.wsb')

    #loading in our grammar and to_the_MF_moon.wsb program
    MF_moon_meta = metamodel_from_file('wsb.tx')
    MF_moon_model  = MF_moon_meta.model_from_file('to_the_MF_moon.wsb')

except FileNotFoundError as e:
    print("Error loading 'wsb.tx':", e)
    exit(1)

class WSBLangInterpreter:
    def __init__(self):
        self.context = {}

    # interpreting sample program line by line
    def interpret(self, program):
        for statement in program.statements:
            self.execute(statement)
        
    # executing a statement depnding on what kind of statement it is 
    def execute(self, statement):
        if statement.__class__.__name__ == "PrintStatement":
            self.handle_print(statement)
        elif statement.__class__.__name__ == "StockOperation":
            self.handle_stockOp(statement)
        elif statement.__class__.__name__ == "InputStatement":
            self.handle_input(statement)
        elif statement.__class__.__name__ == "IfStatement":
            self.handle_if(statement)
        elif statement.__class__.__name__ == "Expression":
            self.handle_expression(statement)
        elif statement.__class__.__name__ == "FunctionDef":
            self.handle_function_def(statement)
        elif statement.__class__.__name__ == "FunctionCall":
            self.handle_function_call(statement)

    # handles input statements
    def handle_input(self, statement):
        user_input = input(statement.prompt.strip('"')) 
        self.context[statement.variable] = user_input
 

    # handles if/else statements   
    def handle_if(self, statement):
        if self.evaluate_expression(statement.condition):
            for stmt in statement.then_block:
                self.execute(stmt)
        else:
            for stmt in statement.else_block:
                self.execute(stmt)
            
    # handles stockOperation, ideally integrated into trading platform. But a printed confirmation works for now. 
    def handle_stockOp(self, statement):
        display = f"Congrats, on {statement.command}'ing {statement.quantity} {statement.stock} contracts. Strike @ {statement.price} with the expiration date of: {statement.time}. Good Luck!"
        print(display)

    # handles expressions, may need to expand for more complicated ones
    def handle_expression(self, expression):
        if isinstance(expression, ArithmeticExpression):
            return self.evaluate_arithmetic_expression(expression)
        else:
            return expression.value  # literal?
    
    # handles math expressions
    def evaluate_arithmetic_expression(self, expression):
        left_hand_side = self.evaluate_expression(expression.left)
        right_hand_side = self.evaluate_expression(expression.right)
        if expression.op == '+':
            return left_hand_side + right_hand_side
        elif expression.op == '-':
            return left_hand_side - right_hand_side
        elif expression.op == '*':
            return left_hand_side * right_hand_side
        elif expression.op == '/':
            return left_hand_side / right_hand_side  # can't divide undefined
        
    # handles defining a function
    def handle_function_def(self,statement):
        self.context[statement.name]=statement

    # handles function
    def handle_function_call(self,statement):
        def_function = self.context.get(statement.name)
        if not def_function:
            raise Exception (f"check SOMETHING WRONG with function definition")
        local_context = dict(zip(def_function.params, statement.arguments))
        for statement in def_function.body:
            self.execute(statement)

    # handles print statement
    def handle_print(self, statement):
        def get_stock_price(ticker):        
            api_key = ''
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={api_key}"
            response = requests.get(url)
            data = response.json()
            price = data["Global Quote"]["05. price"]
            return price

        if isinstance(statement.expression, str):
        # Check if the expression is a variable in the context
            if statement.expression in self.context:
                tickerTestPrint= get_stock_price(self.context[statement.expression])
                print ("Ticker $" + self.context[statement.expression] +" "+ tickerTestPrint)
                return tickerTestPrint
            else:
                print(statement.expression)
        else:
            result = self.evaluate_expression(statement.expression)
            print(result)

    
    # fetchs stock price given a specific ticker
def get_stock_price(ticker):        
    api_key = ''
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    price = data["Global Quote"]["05. price"]
    return price

    # updates stock price every 30 seconds
def update_stock_price(interpreter, ticker_symbols):
    while True:
        for ticker in ticker_symbols:
            interpreter.context[ticker] = get_stock_price(ticker) # type: ignore check back later
        time.sleep(0.5)
        
def main():

    interpreter = WSBLangInterpreter()

    # hello_world.wsb program 
    hello_world_program = hello_model
    interpreter.interpret(hello_world_program)

    # yolo_tsla.wsb program
    yolo_tsla_program = yolo_tsla_model
    interpreter.interpret(yolo_tsla_program)

    # input.wsb program
    input_program = input_model
    interpreter.interpret(input_program)

    # to_the_MF_moon.wsb program
    to_the_MF_moon_program = MF_moon_model  
    interpreter.interpret(to_the_MF_moon_program)

    
    # hard coding: to test and in case my API aint working 
    stock_tickers = [
    'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'FB', 'BRK.B', 'JNJ', 'PG', 'JPM', 'V', 
    'MCD', 'KO', 'GS', 'DIS', 'IBM', 'CVX', 'XOM', 'PFE', 'BA', 'HON',
    'NKE', 'HD', 'UNH', 'TSLA', 'NFLX', 'NVDA', 'ADBE', 'INTC', 'CSCO', 'PEP',
    'T', 'VZ', 'WMT', 'BAC', 'MMM', 'GE', 'DOW', 'LMT', 'F', 'GM',
    'ORCL', 'SAP', 'SCHW', 'GILD', 'FIS', 'BMY', 'SLB', 'ACN', 'TXN', 'QCOM']


    # #implement later 
    # ticker_data_frame = pd.read_csv('tickers.csv') # gets the tickers 
    # stock_tickers = ticker_data_frame['ticker'].to_list() # puts tickers into a list

    # #Start a background thread to update stock prices
    # thread = threading.Thread(target=update_stock_price, args=(interpreter, stock_tickers))
    # thread.start()


if __name__== "__main__":
    main()

    
