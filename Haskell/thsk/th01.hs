{-# LANGUAGE TemplateHaskell #-}

import Th01

import Control.Monad
import Language.Haskell.TH

plus42 :: Int -> Int
plus42 x = $static + x

times2 :: Int -> Int
times2 x = $dynamic  + x

main = do
   e<-runQ(curryN 3);
   print $ show e
   print $ plus42 3
   print $ times2 3

-- reification

data Result e a = Err e  | Ok a
data List     a = Nil    | Cons a (List a)
data Tree     a = Leaf a | Node (Tree a) a (Tree a)



