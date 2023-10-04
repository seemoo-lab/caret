from constants import *
import numpy as np
import pandas as pd

class Transformator:
    def __init__(self, df) -> None:
        self.df = df.copy()
        
    def copy(self):
        return Transformator(self.df.copy())
        
    def get(self):
        return self.df
    
    def sum(self, columns):
        # self.df = pd.pivot_table(self.df, index=[c for c in self.df.columns if not c in columns + ['traffic']], columns=columns, values='traffic').aggregate(np.sum, axis=1).reset_index().rename(columns={0: 'traffic'})
        return self.agg(columns, np.sum)

    def mean(self, columns):
        # self.df = pd.pivot_table(self.df, index=[c for c in self.df.columns if not c in columns + ['traffic']], columns=columns, values='traffic').aggregate(np.mean, axis=1).reset_index().rename(columns={0: 'traffic'})
        return self.agg(columns, np.mean)
    
    def agg(self, columns, method):
        self.df = pd.pivot_table(
            self.df,
            index=[c for c in self.df.columns if not c in columns + ['traffic']],
            columns=columns,
            values='traffic'
        ).aggregate(method, axis=1).reset_index().rename(columns={0: 'traffic'})
        return self
    
    def filter(self, column, value):
        self.df = self.df[self.df[column] == value] #[[c for c in self.df.columns if c != column]]
        return self

    def not_filter(self, column, value):
        self.df = self.df[self.df[column] != value]
        return self
    
    def add_column(self, column, base, generator=None):
        if generator:
            self.df[column] = self.df[base].apply(generator)
        else:
            self.df[column] = base
            
        return self
        
    def filter_rows(self, row, value):
        self.df = self.df[self.df[row] == value]
        return self
    
    def filter_columns(self, columns):
        self.df = self.df[columns]
        return self
    
    def groupby_sum(self, column):
        self.df = self.df.groupby(by=column).sum().reset_index(names=column)
        return self
    
    def groupby_mean(self, column):
        self.df = self.df.groupby(by=column).mean().reset_index(names=column)
        return self
    
    def groupby_max(self, column):
        self.df = self.df.groupby(by=column).max().reset_index(names=column)
        return self
    
    def groupby_tail(self, column, n):
        self.df = self.df.groupby(by=column).tail(n)
        return self
    
    def reset_index(self, column=None):
        if column == None:
            self.df = self.df.reset_index(drop=True)
        else:
            self.df = self.df.reset_index(names=column)
        return self
    
    def apply(self, column, func):
        self.df[column] = self.df[column].apply(func)
        return self
    
    def sort(self, column, ascending=True):
        self.df = self.df.sort_values(by=column, ascending=ascending)
        return self
    
    def set_index(self, column):
        self.df = self.df.set_index(column)
        return self
    
    def drop_duplicates(self, columns):
        self.df = self.df.drop_duplicates(columns)
    