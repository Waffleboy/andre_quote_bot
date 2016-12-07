# -*- coding: utf-8 -*-
"""
Created on Mon Oct 31 10:35:54 2016

@author: waffleboy
"""
import logging

def setupLogger():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    return logging