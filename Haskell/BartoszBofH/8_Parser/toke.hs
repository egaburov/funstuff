import Data.Char

data Operator = Plus | Minus | Times | Div deriving (Show, Eq)

data Token = TokOp    Operator 
           | TokIdent String
           | TokNum   Int 
           | TokAssign
           | TokLParen
           | TokRParen
           | TokEnd
    deriving (Show, Eq)

operator :: Char -> Operator
operator c | c == '+' = Plus
           | c == '-' = Minus
           | c == '*' = Times
           | c == '/' = Div

tokenize :: String -> [Token]
tokenize [] = TokEnd:[]
tokenize (c:cs) 
  | elem c "+-*/" = TokOp (operator c) : tokenize cs
  | c == '=' = TokAssign : tokenize cs
  | c == '(' = TokLParen : tokenize cs
  | c == ')' = TokRParen : tokenize cs
  | isDigit c = number c cs
  | isAlpha c = identifier c cs
  | isSpace c = tokenize cs
  | otherwise = error $ "Cannot tokenize " ++ [c]

identifier c cs = let (str, cs') = span isAlphaNum cs in
                  TokIdent (c:str) : tokenize cs'
number c cs = let (digs, cs') = span isDigit cs in
              TokNum (read (c:digs)) : tokenize cs'


main = do
  print $ tokenize "x1 = 23/(2+3) "
  print $ tokenize "12 + 24 / x1"
