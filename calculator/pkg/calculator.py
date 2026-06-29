class Calculator:
    def __init__(self):  #this is basically the constructor 
        self.operators={
            #lambda connects the key to the value : string to the function
            "+": lambda a,b:a+b,
            "-": lambda a,b:a-b,
            "*":lambda a,b:a*b,
            "/": lambda a,b:a/b,
        }

        self.precedence={
            "+":1,
            "-":1,
            "*":2,
            "/":2,
        }

    #in python when it comes to member fucntions we need to pass "self"
    #self is bascially "this" in C++, difference is in C++, &object is automatically passed behind the scenes
    def evaluate(self, expression):  
        if not expression or expression.isspace():
            return None
        tokens=expression.strip().split()  
        #strip removes leading and trailing spaces, \t and \n 
        return self._evaluate_infix(tokens)
    
    
    def _apply_operator(self, operators, values):
        if not operators:
            return
        
        operator=operators.pop()
        if len(values)<2:
            raise ValueError(f"not enough operands for operator {operator}")
        
        b=values.pop()
        a=values.pop()
        
        values.append(self.operators[operator](a,b))  #this is the lambda part
    
    #baiscally we are doing the opeartions 2 by 2 , checking if the opartor exists, the numners are valid and finally the result to be a number
    def _evaluate_infix(self , tokens):
        values=[]
        operators=[]

        for token in tokens:
            if token in self.operators:
                #first we're checking to see if there's any operator and 
                #if there is , if they are valid
                while(
                    operators
                    #In Python, arr[-1] refers to the last element of a sequence 
                    and operators[-1] in self.operators
                    and self.precedence[operators[-1]]>= self.precedence[token]
                ):
                    self._apply_operator(operators, values)
                operators.append(token)
            else:
                try:
                    values.append(float(token))
                except ValueError:
                    raise ValueError(f"invalid token: {token}")
        while operators:
            self._apply_operator(operators,values)
        if len(values) !=1:  #if the result is not exactly one number raise an error
            #we have already popped a and b so teh reuslt has to be one number
            raise ValueError(f"invalid expression")
        return values[0]
    
