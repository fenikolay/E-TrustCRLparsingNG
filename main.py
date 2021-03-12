from PyQt5.QtWidgets import QPushButton, QWidget, QTableWidgetItem, QHeaderView, QFileDialog
from PyQt5.QtCore import pyqtSignal, QThread
from urllib import request, error
from ui_sub_main import *
from lxml import etree
from ui_sub_main_add import *
from ui_main import *
from peewee import *
import OpenSSL
import base64
import configparser
import datetime
import math
import os
import re
import shutil
import sqlite3
import sys
import time

base64_icon = '''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'''
base64_info = '''iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAYAAABV7bNHAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyBpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuMC1jMDYwIDYxLjEzNDc3NywgMjAxMC8wMi8xMi0xNzozMjowMCAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENTNSBXaW5kb3dzIiB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOjczNzI1OUQ2OTk2MTExRTdCNjU2ODA5MjgwQTNGNEVBIiB4bXBNTTpEb2N1bWVudElEPSJ4bXAuZGlkOjczNzI1OUQ3OTk2MTExRTdCNjU2ODA5MjgwQTNGNEVBIj4gPHhtcE1NOkRlcml2ZWRGcm9tIHN0UmVmOmluc3RhbmNlSUQ9InhtcC5paWQ6NzM3MjU5RDQ5OTYxMTFFN0I2NTY4MDkyODBBM0Y0RUEiIHN0UmVmOmRvY3VtZW50SUQ9InhtcC5kaWQ6NzM3MjU5RDU5OTYxMTFFN0I2NTY4MDkyODBBM0Y0RUEiLz4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4gPC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz4vUyHzAAAOeUlEQVR42uxcCXAUVRp+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'''
base64_diskette = '''iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAYAAABV7bNHAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyBpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuMC1jMDYwIDYxLjEzNDc3NywgMjAxMC8wMi8xMi0xNzozMjowMCAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENTNSBXaW5kb3dzIiB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOjQ0OUNBRTk4OTk2MTExRTdBNjA1REY3OEVGNEFERThCIiB4bXBNTTpEb2N1bWVudElEPSJ4bXAuZGlkOjQ0OUNBRTk5OTk2MTExRTdBNjA1REY3OEVGNEFERThCIj4gPHhtcE1NOkRlcml2ZWRGcm9tIHN0UmVmOmluc3RhbmNlSUQ9InhtcC5paWQ6NDQ5Q0FFOTY5OTYxMTFFN0E2MDVERjc4RUY0QURFOEIiIHN0UmVmOmRvY3VtZW50SUQ9InhtcC5kaWQ6NDQ5Q0FFOTc5OTYxMTFFN0E2MDVERjc4RUY0QURFOEIiLz4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4gPC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz5NfXAoAAAGBklEQVR42uybW09cVRTH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'''
base64_file = '''iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAYAAABV7bNHAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyBpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuMC1jMDYwIDYxLjEzNDc3NywgMjAxMC8wMi8xMi0xNzozMjowMCAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENTNSBXaW5kb3dzIiB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOjUwODRBNTk5OTk2MTExRTc5QjM5RDUwNDQzM0VFQTlFIiB4bXBNTTpEb2N1bWVudElEPSJ4bXAuZGlkOjUwODRBNTlBOTk2MTExRTc5QjM5RDUwNDQzM0VFQTlFIj4gPHhtcE1NOkRlcml2ZWRGcm9tIHN0UmVmOmluc3RhbmNlSUQ9InhtcC5paWQ6NTA4NEE1OTc5OTYxMTFFNzlCMzlENTA0NDMzRUVBOUUiIHN0UmVmOmRvY3VtZW50SUQ9InhtcC5kaWQ6NTA4NEE1OTg5OTYxMTFFNzlCMzlENTA0NDMzRUVBOUUiLz4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4gPC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz7hsQiwAAAEmklEQVR42uycXWxTZRjH/+/5KN1cN3C6aXQbCGQL6xjRhGVCSSCRDWcoAW+8QAmaaFB00wuNH4lc+BFi4GpJb0xELxYMiUoIIXphME5JNCQgikZNHdgF3QfaduvX6Xt8XtpIXNrZsq70bM8/OTk7O133vr/3ed7n/+wsFbZtg5VfGiNgQAyIATEgBsSAGBADYjGgG5CR74aU8trZolM8BdRW0UWpuhIBJC060VkXlQFC0GDUURCgUCgEn89Hk5CorwZ2d+GBFzbBT8zWZF8yJ1SaAfOHEE4/cgSvRRI0iAqI476+PgwODhYGyLJSCAaD2NiE6sAuBNobsNuaKN1g0oR3nQe+tzaiZud7GKiEdnl0dLTwPciSAo0eDW/68U773QSH0gF6CQ9DLQKwowv9J5/CYZd+8wGZplk4oKvTwL4N6PJ14Elrev4GZU0BvWvRf/wJHKoyHVTFGjzA+mY8ZMfnv8qpBehZi4GP9uJQtekQQM23Quv1oj2dKM8grBhB6sTAscdx2G04ocxLmLRPN6KMJVhF0jYv+oefRdcfUUTm+ddN6wZOBIZx/OT3GEtYyDvV2dZLlnu1rDhwbwu6y2JfBXZs9SJ46hye3/kuPrZk8YBuiihyy6kVvfdhaN932H4ujs+41ciVJlG4n96AA6tug2v+IqiSH4z8zz6qOqqmpeh+qQNtdHm+dIAUFCv7tXJ6ml5ZYNTjrBTlazo7S212hi316CgdIJl5V7FyC8TyHoi6FeSQl2QGVRmdJ42FyERDsK98A/vXE7Ajk2SX8691Oo0avSQppuC4PNA3H4RYvYvegbpZaV2nVhnhkxkLdcVizaOw1+2HHH4F9i+fzjZjiVIB0rtfhmjfAyTCQDJc4duwgFi2GvqD7yP9ycOwf/sybyTNvYopQ3VnJ8F5jMBEMmFc8bIzLpQiXV//IkV/cTFRdJkX92wDltRl08pBUv3M7bS4DR3Xi0vJAdEuJuq9tKMlnWd4VAExqoDa5UXZkuKNouFeVEZSu6GVYEAsBsSASiMjr3dQXdxMc6y2H83MVAOnSVAsiGwzkc5U5H+lrvPYltyACIBo3pKzfbAvfw57nHo6WzowHlT74YJYtfm/00rFyR91FgFI0Lc9TbkBRUeB8KVMQ+gsI5T1cmRTaptmmMgpwF1fbIqlcjeg1ABeO5wsOePPliq98rRNvElzFWNADIgBMSAGxIAYEIsBMSAGxIAYEANyrkSxgMSiihRNpAsHpImk7tLHsUgegalHfZHp1M8FA7oyEbPP/jT+re42FkFeCcST8veDxy5eKBzQ1RjoBz6QwJgQCzvTNJeGHy//fSQ0EZssGNDSW1z48IuRkfMXx/dry9wx3Vh4e7lGC69Xm5DS/rrn9a/e/vOveM7XGblzUkJ9ZMX9z506uqf3ruAz/tZXWxtrNtGdugVCB+G4NTF8ZmzojaELByajVlSmYrlTMNdnd4TDYQQCASRSaViWRMsdNdi7dWWrLW0v3Vb/3iEdjcfUpoKhyNmjp0cuReMpeKpMtLW1we/3FwaIxUaRATEgBsSAGBADYkAsBsSA5qZ/BBgAJe9tb9K2+5EAAAAASUVORK5CYII='''
base64_import = '''iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAYAAABV7bNHAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyBpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuMC1jMDYwIDYxLjEzNDc3NywgMjAxMC8wMi8xMi0xNzozMjowMCAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENTNSBXaW5kb3dzIiB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOjcyNjQ4RjYzOTk2MTExRTc5QkNCQ0JDOTRBRjI5NjA2IiB4bXBNTTpEb2N1bWVudElEPSJ4bXAuZGlkOjcyNjQ4RjY0OTk2MTExRTc5QkNCQ0JDOTRBRjI5NjA2Ij4gPHhtcE1NOkRlcml2ZWRGcm9tIHN0UmVmOmluc3RhbmNlSUQ9InhtcC5paWQ6NzI2NDhGNjE5OTYxMTFFNzlCQ0JDQkM5NEFGMjk2MDYiIHN0UmVmOmRvY3VtZW50SUQ9InhtcC5kaWQ6NzI2NDhGNjI5OTYxMTFFNzlCQ0JDQkM5NEFGMjk2MDYiLz4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4gPC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz6ibL5zAAAHEElEQVR42uyce2xTVRzH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'''
base64_export = '''iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAYAAABV7bNHAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyBpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuMC1jMDYwIDYxLjEzNDc3NywgMjAxMC8wMi8xMi0xNzozMjowMCAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENTNSBXaW5kb3dzIiB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOjREMjdEOTZFOTk2MTExRTc4MjIwOERBMkQ5NTM5QTREIiB4bXBNTTpEb2N1bWVudElEPSJ4bXAuZGlkOjREMjdEOTZGOTk2MTExRTc4MjIwOERBMkQ5NTM5QTREIj4gPHhtcE1NOkRlcml2ZWRGcm9tIHN0UmVmOmluc3RhbmNlSUQ9InhtcC5paWQ6NEQyN0Q5NkM5OTYxMTFFNzgyMjA4REEyRDk1MzlBNEQiIHN0UmVmOmRvY3VtZW50SUQ9InhtcC5kaWQ6NEQyN0Q5NkQ5OTYxMTFFNzgyMjA4REEyRDk1MzlBNEQiLz4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4gPC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz7TZtbNAAAG2ElEQVR42uyca0wUVxiG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'''
base64_white_list = '''iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAYAAABV7bNHAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyBpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuMC1jMDYwIDYxLjEzNDc3NywgMjAxMC8wMi8xMi0xNzozMjowMCAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENTNSBXaW5kb3dzIiB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOkM3QjRDQzZFOTk2MTExRTdCOTMwOTFFQjY3MDU5QzdFIiB4bXBNTTpEb2N1bWVudElEPSJ4bXAuZGlkOkM3QjRDQzZGOTk2MTExRTdCOTMwOTFFQjY3MDU5QzdFIj4gPHhtcE1NOkRlcml2ZWRGcm9tIHN0UmVmOmluc3RhbmNlSUQ9InhtcC5paWQ6QzdCNENDNkM5OTYxMTFFN0I5MzA5MUVCNjcwNTlDN0UiIHN0UmVmOmRvY3VtZW50SUQ9InhtcC5kaWQ6QzdCNENDNkQ5OTYxMTFFN0I5MzA5MUVCNjcwNTlDN0UiLz4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4gPC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz6+LHxQAAAIEUlEQVR42uycaWwTRxTH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'''
base64_black_list = '''iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAYAAABV7bNHAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyBpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuMC1jMDYwIDYxLjEzNDc3NywgMjAxMC8wMi8xMi0xNzozMjowMCAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENTNSBXaW5kb3dzIiB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOjFDMzYyNDE3OTk2MTExRTc5N0VCQjc5MUJCMjZGREExIiB4bXBNTTpEb2N1bWVudElEPSJ4bXAuZGlkOjFDMzYyNDE4OTk2MTExRTc5N0VCQjc5MUJCMjZGREExIj4gPHhtcE1NOkRlcml2ZWRGcm9tIHN0UmVmOmluc3RhbmNlSUQ9InhtcC5paWQ6MUMzNjI0MTU5OTYxMTFFNzk3RUJCNzkxQkIyNkZEQTEiIHN0UmVmOmRvY3VtZW50SUQ9InhtcC5kaWQ6MUMzNjI0MTY5OTYxMTFFNzk3RUJCNzkxQkIyNkZEQTEiLz4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4gPC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz7le7yQAAAHXUlEQVR42uycW2gcVRiA/3Nm9pI2TXazyabbSm0h1mJpk7SCt0dfNAjig7UGfBIE30QhvVlrQZpapQpaxYd6eyuCgggigj6IVLTk0tK4tRdjk03SZnPPNtvdnRn/f/ZsutnMbLPNzuyFOeGQzeyZOef/zn893S7TNA2cZt64g8AB5AByAJWwyYXeEIlEIJVKATl3VVFAkmVwebwML7jLTDZcopZIxG/hSwZckvSLfr8f6urqVvwQVkgUU1UVWlpaYHBwUAfTsH5jm8e7Zk+tz9+G79XTkDKBw7BpuIHXZyfHf4nH5s/MRG/OM86hu7sburq6rNOgZDKha8/6LVsPIJhDuIi1pFHl2uqbQp31jdqrqAYvI6R+2mTLTIzAyC43BDe37FtX7z+mCDC4W2ULCNWI1rc7tPmB72Nzc0+iDFcsc9IEyNfU3FbrC7yjKOWrNUbrxr5pXXDDcZfHY10Uk9DR+YKhF9RUUoYKa5qmgtvt6ahvDG6zNIrhTLvNdsnEW0Ih44vopY0u1+DEO/F32DpABveQk97d3gpNgQCkMPTrC6QfXOTFcBhGRsd07cuG075zBwQa/KCoxQ98MkbYnr5+GI9OLJn3XmS+F0CakTY0YH5xXygEiSzHTf0qpgQqvp+7zAaEswHHKwJoMZvb5YKLA2HDeY3WX2xApjkSaU9G4AwgM1Oi8UrW+GK2FOY7xTJhp9RwANlci+VzjGT7IKJHxsQ456bjXTje7P3V+qBiJa9yseD09J2HgfAlzFyF7Yv1Tc/MgpwTSWjxFGXIkVoR7hlnMDk1tWzekgEigaMTE+h4tUUwi8kll1BLlu8mhWDVqlxIo02TiqJFRTMxyjcK2TB9vOOkHSddaaVGKU2MwzIHdKeSNjQxy+BQImoyb0kAUS328K42CDY2ZmXG6TB/YWAAIliLyTm1WOuO7dDYEEDHXvxMWpZk+Ku3D25Go6uOZHKxzMvv80GouRmSObXY5WvXDHeSxq9vDlpSalB+5XG7y0eDjGqrUtZi3KnFnDBffWGe1DrTs03MLNxmxloR7um5ZRXmKWSH/7kMQ8ORO7WYiLcTk5NYbvBlOUr40mW4PjS8dHzRADGYnp1dNm/JANGODUdGTPMdo4p9KBKxNFk0m7ektZiV4x0n7QByABVyXGPrfWXhg1ZctwlBWYGTJ8Rucpt31VYNWsC+g2nwtkuDRiR0e4X30Sd8OiQNXpdVfcGpatQgEnI7QjmKcLZyDYKoQweSHKbwuiePSdF9TyOV/QjHT9EPr76fYjokuVo0iIR8CGd616XCJtSgKZT8MYR0DP/2gbEmEZwY9qdw3FsuBbz4eg77i5IKb7jURXOteEAkRBtqzgkU8n6EsyCuk/BPoPDHXWnNuG2oOWSOKtTg66S4Tvd34vUu1KgaZv1H2iwFlHHGnSjMg0Lo7DYPaU3qRgiBLEjZcLzCQS8ek4i/n0ef1I7AE5UMKFMufpTi8LvKYI3BGNKkR8nc3Co04Gsyvw7drFTdN+UCyOTfH+Iz/8BneirdxMiRRlDoAyhQL27/WhMf9QhqwxGE0ilrcFBoTtIADvWP8VlfKmzJJlQsIDIzEvYGvtiflKBHY6aQyNwOyXd8jjEcBp8rac2xI8LYlgcRpDHs+zC0n1ONIaVEVwy0kAtTPa1w/Vl2LdzWRDGjSWRu5zRjn6QZaA4TcL5AzfFCFWfSGUg3CVKSwVnUJNddFpfUHTKDr2w0q5IXqyTov6hBPyEgnsfRkmmN4bgf0Ky0rAhW1YAyGfKz6JBfQ4ecylOlU4jfwtLJJOVJ8WoHlJsh1xo45NxGyePjBslkVQLSq/I8SSA3KUCXJJPMXkjcLs2ZF5pzOE8SSNdGcLA7TzKpF7g2QrIFUEwcWRy5S4b8GUarVxISnM+XTJJPkpcXuBVdzT+HmnNUHFkk8ySBX2O0GgHQz4nMksmYyLhPIOyNzPojD1uq+Z0oUL2J5mQngeSXavXQnj+ZpOdsw2eGUJuUSgbERD+Jwn6jpDWCZcFJa87SJFDLSSZ78Hc2JLfwZweFllV8NZ/JhrsR0rcCkiwAndI1h+tCc4Nk8gZqEBW4veKoxCP80GGE86sNcGxz0rLwRccQyHcomFscWZy+S22Vqd2owO3X0k75TQFnjU1RzLZDe5eAdBIF/Bn9B9VhKyk8dXPDfgg1iXzOnybOu5wA8dVMRibymzCPlR52EaRRjQ7e0lDttJqCATHGo6tdXaFCakVTdaYxxiYto0kfV0nEF34s5//lnK+pmjKcuB0/axkg+sjuxOjQGWD8QqVBkiQZFuZm3puZiE5bBohzCWKz07Gx/668hKY2WCmQOMKJ34qdmh8f/bTQFRds2rHYLViYmeq/dL6no3nTlqN46RkEV6NBeX5Rk6aqVxLx+CeTw9c+0M+YEgnrAJHG7N27F8bHx8kf/e32ePd419a21AWa2lVFoX/WKpfv7gDx3R1XJ2+M9KWSiSkltUtff2tra4Fu3fmKrvI5MHMAOYAcQE7Laf8LMACq9BxYkJqoOAAAAABJRU5ErkJggg=='''

config = configparser.ConfigParser()
if os.path.isfile('settings.ini'):
    config.read('settings.ini')
else:
    open('settings.ini', 'w').close()
    config['Folders'] = {'certs': 'certs/',
                         'crls': 'crls/',
                         'tmp': 'temp/',
                         'logs': 'logs/',
                         'to_uc': 'to_uc/',
                         'uc': 'uc/'}

    config['MainWindow'] = {'width ': '1100',
                            'height ': '650',
                            'saveWidth': 'No',
                            'AllowResize': 'Yes'}
    config['Bd'] = {'type': 'sqlite3',
                    'name': 'cert_crl.db'}
    config['Socket'] = {'timeout ': 'No'}
    config['Listing'] = {'uc': '500',
                         'crl': '500',
                         'cert': '500',
                         'watch': '500'}
    # windowsvista, Windows, Fusion
    config['Style'] = {'window': 'Fusion',
                       'extendetColorInfo': 'No'}
    config['Proxy'] = {'proxyOn': 'No',
                       'ip': '',
                       'port': '',
                       'login': '',
                       'password': ''}
    config['Update'] = {'priority': 'custom',
                        'advancedChecking': 'Yes',
                        'viewingCRLlastNextUpdate': 'Yes'}
    config['Backup'] = {'backUPbyStart': 'Yes'}
    config['Tabs'] = {'ucLimit': '500',
                      'ucAllowDelete': 'No',
                      'crlLimit': '500',
                      'crlAllowDelete': 'No',
                      'certLimit': '500',
                      'certAllowDelete': 'No',
                      'wcLimit': '500',
                      'wcAllowDelete': 'No',
                      'wccLimit': '500',
                      'wccAllowDelete': 'No',
                      'wcdLimit': '500',
                      'wcdAllowDelete': 'No'}
    config['Schedule'] = {'allowSchedule': 'No',
                          'weekUpdate': 'All',
                          'timeUpdate': '10M',
                          'periodUpdate': '9:00; 12:00; 16:00',
                          'allowUpdateTSLbyStart': 'No',
                          'allowUpdateCRLbyStart': 'No',
                          'rangeUpdateCRL': '5day'}
    config['Sec'] = {'allowImportCRL': 'No',
                     'allowExportCRL': 'No',
                     'allowDeleteWatchingCRL': 'No',
                     'allowDownloadButtonCRL': 'Yes',
                     'allowCheckButtonCRL': 'Yes'}
    config['Logs'] = {'dividelogsbyday': 'Yes',
                      'dividelogsbysize': '1024',
                      'loglevel': '9'}
    config['XMPP'] = {'server': '',
                      'login': '',
                      'password': '',
                      'tosend': '',
                      'sendinfoerr': 'No',
                      'sendinfonewcrl': 'No',
                      'sendinfonewtsl': 'No'}
    with open('settings.ini', 'w') as configfile:
        config.write(configfile)

try:
    os.makedirs(config['Folders']['certs'])
except OSError:
    pass
try:
    os.makedirs(config['Folders']['crls'])
except OSError:
    pass
try:
    os.makedirs(config['Folders']['tmp'])
except OSError:
    pass
try:
    os.makedirs(config['Folders']['to_uc'])
except OSError:
    pass
try:
    os.makedirs(config['Folders']['uc'])
except OSError:
    pass
try:
    os.makedirs(config['Folders']['logs'])
except OSError:
    pass

if config['Logs']['dividelogsbyday'] == 'Yes':
    datetime_day = '_' + datetime.datetime.now().strftime('%Y%m%d')
else:
    datetime_day = ''

open(config['Folders']['logs'] + "/error" + datetime_day + ".log", "a").write('')
open(config['Folders']['logs'] + "/log" + datetime_day + ".log", "a").write('')


def logs(body, kind='', log_level=''):
    if int(log_level) <= int(config['Logs']['loglevel']):
        if kind == 'errors':
            with open(config['Folders']['logs'] + "/error" + datetime_day + ".log", "a") as file:
                file.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '    ' + body + '\n')
            file.close()
        else:
            with open(config['Folders']['logs'] + "/log" + datetime_day + ".log", "a") as file:
                file.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '    ' + body + '\n')
            file.close()


bd_backup_name = str('cert_crl.db_') + datetime.datetime.now().strftime('%Y%m%d') + '.bkp'
if os.path.isfile(bd_backup_name):
    print('Info: ' + bd_backup_name + ' exist')
    logs('Info: ' + bd_backup_name + ' exist', 'info', '7')
else:
    try:
        shutil.copy2('cert_crl.db', bd_backup_name)
        print('Info: ' + bd_backup_name + ' created')
        logs('Info: ' + bd_backup_name + ' created', 'info', '6')
    except Exception:
        print('Error: cert_crl.db NOT FOUND')
        logs('Error: cert_crl.db NOT FOUND', 'errors', '2')
try:
    connect = sqlite3.connect(config['Bd']['name'])
    db = SqliteDatabase(config['Bd']['name'])
except Exception:
    print('Error: Connect to BD failed')
    logs('Error: Connect to BD failed', 'errors', '2')


class UC(Model):
    ID = IntegerField(primary_key=True)
    Registration_Number = IntegerField()
    INN = IntegerField()
    OGRN = IntegerField()
    Full_Name = CharField()
    Email = CharField()
    Name = CharField()
    URL = CharField()
    AddresCode = CharField()
    AddresName = CharField()
    AddresIndex = CharField()
    AddresAddres = CharField()
    AddresStreet = CharField()
    AddresTown = CharField()

    class Meta:
        database = db


class CERT(Model):
    ID = IntegerField(primary_key=True)
    Registration_Number = IntegerField()
    Name = CharField()
    KeyId = CharField()
    Stamp = CharField()
    SerialNumber = CharField()
    Data = CharField()

    class Meta:
        database = db


class CRL(Model):
    ID = IntegerField(primary_key=True)
    Registration_Number = IntegerField()
    Name = CharField()
    KeyId = CharField()
    Stamp = CharField()
    SerialNumber = CharField()
    UrlCRL = CharField()

    class Meta:
        database = db


class WatchingCRL(Model):
    ID = IntegerField(primary_key=True)
    Name = CharField()
    INN = IntegerField()
    OGRN = IntegerField()
    KeyId = CharField()
    Stamp = CharField()
    SerialNumber = CharField()
    UrlCRL = CharField()
    status = CharField()
    download_status = CharField()
    download_count = CharField()
    last_download = DateTimeField()
    last_update = DateTimeField()
    next_update = DateTimeField()

    class Meta:
        database = db


class WatchingCustomCRL(Model):
    ID = IntegerField(primary_key=True)
    Name = CharField()
    INN = IntegerField()
    OGRN = IntegerField()
    KeyId = CharField()
    Stamp = CharField()
    SerialNumber = CharField()
    UrlCRL = CharField()
    status = CharField()
    download_status = CharField()
    download_count = CharField()
    last_download = DateTimeField()
    last_update = DateTimeField()
    next_update = DateTimeField()

    class Meta:
        database = db


class WatchingDeletedCRL(Model):
    ID = IntegerField(primary_key=True)
    Name = CharField()
    INN = IntegerField()
    OGRN = IntegerField()
    KeyId = CharField()
    Stamp = CharField()
    SerialNumber = CharField()
    UrlCRL = CharField()
    status = CharField()
    download_status = CharField()
    download_count = CharField()
    last_download = DateTimeField()
    last_update = DateField()
    next_update = DateField()
    moved_from = CharField()

    class Meta:
        database = db


class Settings(Model):
    ID = IntegerField(primary_key=True)
    name = IntegerField()
    value = CharField()

    class Meta:
        database = db


if not UC.table_exists():
    UC.create_table()
if not CERT.table_exists():
    CERT.create_table()
if not CRL.table_exists():
    CRL.create_table()
if not Settings.table_exists():
    Settings.create_table()
    Settings(name='ver', value=0).save()
    Settings(name='data_update', value='1970-01-01 00:00:00').save()
if not WatchingCRL.table_exists():
    WatchingCRL.create_table()
if not WatchingCustomCRL.table_exists():
    WatchingCustomCRL.create_table()
if not WatchingDeletedCRL.table_exists():
    WatchingDeletedCRL.create_table()


def progressbar(cur, total=100):
    percent = '{:.2%}'.format(cur / total)
    sys.stdout.write('\r')
    # sys.stdout.write("[%-50s] %s" % ('=' * int(math.floor(cur * 50 / total)),percent))
    sys.stdout.write("[%-100s] %s\n" % ('=' * int(cur), percent))
    sys.stdout.flush()


def schedule(block_num, block_size, total_size):
    QCoreApplication.processEvents()
    if total_size == 0:
        percent = 0
    else:
        percent = block_num * block_size / total_size
    if percent > 1.0:
        percent = 1.0
    percent = percent * 100
    print("\n download : %.2f%%" % (percent))
    progressbar(percent)


def get_info_xlm(type_data, xml_file='tsl.xml'):
    current_version = 'unknown'
    last_update = 'unknown'
    with open(xml_file, "rt", encoding="utf-8") as obj:
        xml = obj.read().encode()

    root = etree.fromstring(xml)
    for row in root.getchildren():
        if row.text:
            if row.tag == 'Версия':
                current_version = row.text
        if row.text:
            if row.tag == 'Дата':
                last_update = row.text
    if type_data == 'current_version':
        return current_version
    if type_data == 'last_update':
        return last_update


def save_cert(key_id, folder):
    try:
        for certs in CERT.select().where(CERT.KeyId == key_id):
            with open(folder + "/" + certs.KeyId + ".cer", "wb") as file:
                file.write(base64.decodebytes(certs.Data.encode()))
            if folder == config['Folders']['certs']:
                os.startfile(os.path.realpath(config['Folders']['certs']))
                print(os.path.realpath(config['Folders']['certs']))
            elif folder == config['Folders']['to_uc']:
                os.startfile(os.path.realpath(config['Folders']['to_uc']))
                print(os.path.realpath(config['Folders']['to_uc']))
    except Exception:
        print('Error: save_cert(key_id)')


def open_file(file_name, file_type, url='None'):
    # open_file(sn + ".cer", "cer")
    # CryptExtAddCER «файл» Добавляет сертификат безопасности.
    # CryptExtAddCRL «файл» Добавляет список отзыва сертификатов.
    # CryptExtAddCTL «файл» Добавляет список доверия сертификатов.
    # CryptExtAddP7R «файл» Добавляет файл ответа на запрос сертификата.
    # CryptExtAddPFX «файл» Добавляет файл обмена личной информацией.
    # CryptExtAddSPC «файл» Добавляет сертификат PCKS #7.
    type_crypto_dll = ''
    folder = ''
    if file_type == 'cer':  # CryptExtOpenCER «файл» Открывает сертификат безопасности.
        type_crypto_dll = 'CryptExtOpenCER'
        folder = 'certs'
    elif file_type == 'crl':  # CryptExtOpenCRL «файл» Открывает список отзыва сертификатов.
        type_crypto_dll = 'CryptExtOpenCRL'
        folder = 'crls'
    elif file_type == 'cat':  # CryptExtOpenCAT «файл» Открывает каталог безопасности.
        type_crypto_dll = 'CryptExtOpenCAT'
        folder = 'cats'
    elif file_type == 'ctl':  # CryptExtOpenCTL «файл» Открывает список доверия сертификатов.
        type_crypto_dll = 'CryptExtOpenCTL'
        folder = 'ctls'
    elif file_type == 'p10':  # CryptExtOpenP10 «файл» Открывает запрос на сертификат.
        type_crypto_dll = 'CryptExtOpenP10'
        folder = 'p10s'
    elif file_type == 'p7r':  # CryptExtOpenP7R «файл» Открывает файл ответа на запрос сертификата.
        type_crypto_dll = 'CryptExtOpenP7R'
        folder = 'p7rs'
    elif file_type == 'pkcs7':  # CryptExtOpenPKCS7 «файл» Открывает сертификат PCKS #7.
        type_crypto_dll = 'CryptExtOpenPKCS7'
        folder = 'pkcs7s'
    elif file_type == 'str':  # CryptExtOpenSTR «файл» Открывает хранилище сериализированных сертификатов.
        type_crypto_dll = 'CryptExtOpenSTR'
        folder = 'strs'

    run_dll = "%SystemRoot%\\System32\\rundll32.exe cryptext.dll," + type_crypto_dll
    path = os.path.realpath(config['Folders'][folder] + "/" + file_name + "." + file_type)
    print(path)
    if not os.path.exists(path):
        if file_type == 'cer':
            save_cert(file_name)
        elif file_type == 'crl':
            download_file(url, file_name + '.crl', config['Folders']['crls'])
    else:
        open_crl = run_dll + "  " + path
        os.system(open_crl)


def check_custom_crl(id_custom_crl, name, id_key, url_crl=''):
    QCoreApplication.processEvents()
    try:
        QCoreApplication.processEvents()
        issuer = {}
        try:
            if not os.path.isfile(config['Folders']['crls'] + '/' + str(id_key) + '.crl'):
                if not download_file(url_crl,
                                     id_key + '.crl',
                                     config['Folders']['crls'],
                                     'custome',
                                     str(id_custom_crl),
                                     'Yes') == 'down_success':
                    print('Warning: check_custom_crl()::down_error ' + name)
                    logs('Warning: check_custom_crl()::down_error ' + name, 'warn', '4')
                    return 'down_error'
            crl = OpenSSL.crypto.load_crl(OpenSSL.crypto.FILETYPE_ASN1,
                                          open('crls/' + str(id_key) + '.crl', 'rb').read())
            crl_crypto = crl.get_issuer()
            cryptography = crl.to_cryptography()
            try:
                for var, data in crl_crypto.get_components():
                    issuer[var.decode("utf-8")] = data.decode("utf-8")
            except Exception:
                print('Error: check_custom_crl()::get_components()')
                logs('Error: check_custom_crl()::get_components()', 'errors', '2')
            query_uc = UC.select().where(UC.OGRN == issuer['OGRN'], UC.INN == issuer['INN'])
            for uc_data in query_uc:
                name = uc_data.Name
            query_update = WatchingCustomCRL.update(INN=issuer['INN'],
                                                    OGRN=issuer['OGRN'],
                                                    status='Info: Filetype good',
                                                    last_update=cryptography.last_update +
                                                                datetime.timedelta(hours=5),
                                                    next_update=cryptography.next_update +
                                                                datetime.timedelta(hours=5)). \
                where(WatchingCustomCRL.ID == id_custom_crl)
            query_update.execute()
            issuer['INN'] = 'Unknown'
            issuer['OGRN'] = 'Unknown'
            print('Info: check_custom_crl()::success ' + name)
            logs('Info: check_custom_crl()::success ' + name, 'info', '5')
            return 'check_success'

        except Exception:
            query_update = WatchingCustomCRL.update(status='Warning: FILETYPE ERROR',
                                                    last_update='1970-01-01',
                                                    next_update='1970-01-01').where(
                WatchingCustomCRL.ID == id_custom_crl)
            query_update.execute()
            print('Warning: check_custom_crl()::FILETYPE_ERROR')
            logs('Warning: check_custom_crl()::FILETYPE_ERROR', 'warn', '4')
    except Exception:
        print('Error: check_custom_crl()')
        logs('Error: check_custom_crl()', 'errors', '1')


def check_crl(id_wc, name_wc, key_id_wc, url_crl=''):
    try:
        try:
            if not os.path.isfile(config['Folders']['crls'] + '/' + str(key_id_wc) + '.crl'):
                if download_file(url_crl,
                                     key_id_wc + '.crl',
                                     config['Folders']['crls'],
                                     'current',
                                     str(id_wc),
                                     'Yes') == 'down_success':
                    crl = OpenSSL.crypto.load_crl(
                        OpenSSL.crypto.FILETYPE_ASN1,
                        open(config['Folders']['crls'] + '/' + str(key_id_wc) + '.crl', 'rb').read())
                    cryptography = crl.to_cryptography()
                    query_update = WatchingCRL. \
                        update(status='Info: Filetype good',
                               last_update=cryptography.last_update + datetime.timedelta(hours=5),
                               next_update=cryptography.next_update + datetime.timedelta(hours=5)).where(
                        WatchingCRL.ID == id_wc)
                    query_update.execute()
                    print('Info: check_crl()::success ' + name_wc)
                    logs('Info: check_crl()::success ' + name_wc, 'info', '5')
                    return 'check_success'
                else:
                    print('Warning: check_crl()::down_error ' + name_wc)
                    logs('Warning: check_crl()::down_error ' + name_wc, 'warn', '4')
                    return 'down_error'
            else:
                crl = OpenSSL.crypto.load_crl(
                    OpenSSL.crypto.FILETYPE_ASN1,
                    open(config['Folders']['crls'] + '/' + str(key_id_wc) + '.crl', 'rb').read())
                cryptography = crl.to_cryptography()
                query_update = WatchingCRL. \
                    update(status='Info: Filetype good',
                           last_update=cryptography.last_update + datetime.timedelta(hours=5),
                           next_update=cryptography.next_update + datetime.timedelta(hours=5)).where(
                    WatchingCRL.ID == id_wc)
                query_update.execute()
                print('Info: check_crl()::success ' + name_wc)
                logs('Info: check_crl()::success ' + name_wc, 'info', '5')
                return 'check_success'
        except Exception:
            query_update = WatchingCRL.update(status='Warning: FILETYPE ERROR',
                                              last_update='1970-01-01',
                                              next_update='1970-01-01').where(WatchingCRL.ID == id_wc)
            query_update.execute()
            print('Warning: check_crl()::FILETYPE_ERROR')
            logs('Warning: check_crl()::FILETYPE_ERROR', 'warn', '4')
    except Exception:
        print('Error: check_crl()')
        logs('Error: check_crl()', 'errors', '1')


def check_for_import_in_uc():
    try:
        folder = config['Folders']['crls']
        current_datetime = datetime.datetime.now()
        before_current_datetime = datetime.datetime.now() - datetime.timedelta(days=5)
        query_1 = WatchingCRL.select().where(
            WatchingCRL.last_update.between(before_current_datetime, current_datetime)
        )
        query_2 = WatchingCustomCRL.select().where(
            WatchingCustomCRL.last_update.between(before_current_datetime, current_datetime)
        )
        # datetime.datetime.strptime(last_date_copy, '%Y-%m-%d %H:%M:%S')
        count = 0
        for wc in query_1:
            if current_datetime > wc.next_update:
                print('1 Need to download', wc.Name, current_datetime, wc.last_download, wc.last_update, wc.next_update)
                download_file(wc.UrlCRL, wc.KeyId + '.crl', folder, 'current', wc.ID, 'Yes')
                try:
                    shutil.copy2(config['Folders']['crls'] + '/' + wc.KeyId + '.crl',
                                 config['Folders']['to_uc'] + 'current_' + wc.KeyId + '.crl')
                    check_crl(wc.ID, wc.Name, wc.KeyId)
                except Exception:
                    print('Error: check_for_import_in_uc()::error_copy_current')
                    logs('Error: check_for_import_in_uc()::error_copy_current', 'errors', '2')
                count = count + 1
        for wcc in query_2:
            if current_datetime > wcc.next_update:
                print('2 Need to download', wcc.Name, current_datetime, wcc.last_download, wcc.last_update,
                      wcc.next_update)
                download_file(wcc.UrlCRL, wcc.KeyId + '.crl', folder, 'custome', wcc.ID, 'Yes')
                try:
                    shutil.copy2(config['Folders']['crls'] + '/' + wcc.KeyId + '.crl',
                                 config['Folders']['to_uc'] + 'custom_' + wcc.KeyId + '.crl')
                    check_custom_crl(wcc.ID, wcc.Name, wcc.KeyId)
                except Exception:
                    print('Error: check_for_import_in_uc()::error_copy_custom')
                    logs('Error: check_for_import_in_uc()::error_copy_custom', 'errors', '2')
                count = count + 1
        if count > 0:
            print('Info: Copied ' + str(count) + ' count\'s CRL')
            logs('Info: Copied ' + str(count) + ' count\'s CRL', 'info', '5')
        else:
            print('Info: Needed CRL not found')
            logs('Info: Needed CRL not found', 'info', '5')
    except Exception:
        print('Error: check_for_import_in_uc()')
        logs('Error: check_for_import_in_uc()', 'errors', '1')


def download_file(file_url, file_name, folder, type_download='', w_id='', set_dd='No'):
    try:
        path = folder + '/' + file_name  # + '.' + type_file
        try:
            if config['Proxy']['proxyon'] == 'Yes':
                proxy = request.ProxyHandler(
                    {'https': 'https://' + config['Proxy']['ip'] + ':' + config['Proxy']['port'],
                     'http': 'http://' + config['Proxy']['ip'] + ':' + config['Proxy']['port']})
                # if file_url.split('/')[0] == 'https:':
                #     proxy = request.ProxyHandler(
                #         {'https': 'https://' + config['Proxy']['ip'] + ':' + config['Proxy']['port']})
                # else:
                #     proxy = request.ProxyHandler(
                #         {'http': 'http://' + config['Proxy']['ip'] + ':' + config['Proxy']['port']})
                opener = request.build_opener(proxy)
                request.install_opener(opener)
                logs('Info: Used proxy', 'info', '6')
            request.urlretrieve(file_url, path, schedule)
        except Exception:
            if set_dd == 'Yes':
                if type_download == 'current':
                    query_update = WatchingCRL.update(download_status='Error: Download failed',
                                                      last_download=datetime.datetime.now()
                                                      .strftime('%Y-%m-%d %H:%M:%S')
                                                      ).where(WatchingCRL.ID == w_id)
                    query_update.execute()
                elif type_download == 'custome':
                    query_update = WatchingCustomCRL.update(download_status='Error: Download failed',
                                                            last_download=datetime.datetime.now()
                                                            .strftime('%Y-%m-%d %H:%M:%S')
                                                            ).where(WatchingCustomCRL.ID == w_id)
                    query_update.execute()
            else:
                if type_download == 'current':
                    query_update = WatchingCRL.update(download_status='Error: Download failed'
                                                      ).where(WatchingCRL.ID == w_id)
                    query_update.execute()
                elif type_download == 'custome':
                    query_update = WatchingCustomCRL.update(download_status='Error: Download failed'
                                                            ).where(WatchingCustomCRL.ID == w_id)
                    query_update.execute()
            print('Info: Download failed ' + file_url)
            logs('Info: Download failed ' + file_url, 'info', '4')
            return 'down_error'
        else:
            if set_dd == 'Yes':
                if type_download == 'current':
                    query_update = WatchingCRL.update(download_status='Info: Download successfully',
                                                      last_download=datetime.datetime.now()
                                                      .strftime('%Y-%m-%d %H:%M:%S')
                                                      ).where(WatchingCRL.ID == w_id)
                    query_update.execute()
                elif type_download == 'custome':
                    query_update = WatchingCustomCRL.update(download_status='Info: Download successfully',
                                                            last_download=datetime.datetime.now()
                                                            .strftime('%Y-%m-%d %H:%M:%S')
                                                            ).where(WatchingCustomCRL.ID == w_id)
                    query_update.execute()
                    print('Info: Download successfully', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') )
                # os.startfile(os.path.realpath(config['Folders']['crls'] + "/"))
            else:
                if type_download == 'current':
                    query_update = WatchingCRL.update(download_status='Info: Download successfully'
                                                      ).where(WatchingCRL.ID == w_id)
                    query_update.execute()
                elif type_download == 'custome':
                    query_update = WatchingCustomCRL.update(download_status='Info: Download successfully'
                                                            ).where(WatchingCustomCRL.ID == w_id)
                    query_update.execute()
            print('Info: Download successfully ' + file_url)
            logs('Info: Download successfully ' + file_url, 'info', '5')
            return 'down_success'
    except Exception:
        print('Error: download_file()')
        logs('Error: download_file()', 'errors', '1')


def export_all_watching_crl():
    query = WatchingCRL.select()
    query_2 = WatchingCustomCRL.select()
    with open(r"crl_list.txt", "w") as file:
        for url in query:
            file.write(url.UrlCRL + '\n')
    file.close()
    with open(r"crl_list.txt", "a") as file:
        for url in query_2:
            file.write(url.UrlCRL + '\n')
    file.close()


def exist_crl_in_custom_watch():
    query = WatchingCRL.select()
    for row in query:
        if WatchingCustomCRL.select().where(WatchingCustomCRL.KeyId == row.KeyId).count() > 0:
            print(row.KeyId, ' exist')


def set_value_in_property_file(file_path, section, key, value):
    set_config = configparser.ConfigParser()
    set_config.read(file_path)
    set_config.set(section, key, value)
    configfile = open(file_path, 'w')
    set_config.write(configfile, space_around_delimiters=False)  # use flag in case case you need to avoid white space.
    configfile.close()


class MainWorker(QObject):
    try:
        threadTimerSender = pyqtSignal(str)
        threadButtonStartE = pyqtSignal(str)
        threadButtonStopE = pyqtSignal(str)
        threadButtonStartD = pyqtSignal(str)
        threadButtonStopD = pyqtSignal(str)
        threadInfoMessage = pyqtSignal(str)
        threadBefore = pyqtSignal(str)
        threadAfter = pyqtSignal(str)

        def __init__(self):
            try:
                super(MainWorker, self).__init__()
                self._step = 0
                self._seconds = 0
                self._minutes = 0
                self._hour = 0
                self._day = 0
                self._isRunning = True
            except Exception:
                print('Error: Worker(QObject)::__init__')
                logs('Error: Worker(QObject)::__init__', 'errors', '1')

        def task(self):
            try:
                timer_getting = config['Schedule']['timeUpdate']
                r = re.compile(r"([0-9]+)([a-zA-Z]+)")
                m = r.match(timer_getting)

                if m.group(2) == 'S':
                    sec_to_get = int(m.group(1))
                elif m.group(2) == 'M':
                    sec_to_get = int(m.group(1)) * 60
                elif m.group(2) == 'H':
                    sec_to_get = int(m.group(1)) * 60 * 60
                elif m.group(2) == 'D':
                    sec_to_get = int(m.group(1)) * 60 * 60 * 24
                else:
                    print('error')
                    sec_to_get = 0

                day_get = math.floor(sec_to_get / 60 / 60 / 24)
                hour_get = math.floor(sec_to_get / 60 / 60)
                minutes_get = math.floor(sec_to_get / 60)
                sec_get = math.floor(sec_to_get)

                day_start = 0
                hour_start = 0
                minutes_start = 0
                sec_start = 0
                if day_get > 0:
                    day_start = day_get
                else:
                    if hour_get > 0:
                        hour_start = hour_get
                    else:
                        if minutes_get > 0:
                            minutes_start = minutes_get
                        else:
                            if sec_get > 0:
                                sec_start = sec_get
                            else:
                                print('error')

                print('Info: Start monitoring CRL')
                logs('Info: Start monitoring CRL', 'info', '6')
                self.threadInfoMessage.emit('Info: Start monitoring CRL')
                self.threadButtonStartD.emit('True')
                self.threadButtonStopE.emit('True')
                timer_b = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                timer_a = datetime.datetime.now() + datetime.timedelta(seconds=sec_to_get)
                timer_a = datetime.datetime.strftime(timer_a, '%Y-%m-%d %H:%M:%S')
                self.threadBefore.emit(timer_b)
                self.threadAfter.emit(timer_a)
                if not self._isRunning:
                    self._isRunning = True
                    self._step = 0
                    self._seconds = 0
                    self._minutes = 0
                    self._hour = 0
                    self._day = 0
                while self._isRunning:
                    self._step += 1
                    self._seconds += 1

                    # ---------------------------------------------------
                    if day_start == 0:
                        hour_start -= 1
                    if hour_start == 0:
                        hour_start = 60
                        day_start -= 1
                    if minutes_start == 0:
                        minutes_start = 60
                        hour_start -= 1
                    if sec_start == 0:
                        sec_start = 60
                        minutes_start -= 1
                    # ---------------------------------------------------
                    if self._seconds == 60:
                        self._minutes += 1
                        self._seconds = 0
                    if self._minutes == 60:
                        self._hour += 1
                        self._minutes = 0
                    if self._hour == 24:
                        self._day += 1
                        self._hour = 0
                    sec_c = str(self._seconds)
                    min_c = str(self._minutes)
                    hou_c = str(self._hour)
                    day_c = str(self._day)
                    if self._seconds < 10:
                        sec_c = '0' + sec_c
                    if self._minutes < 10:
                        min_c = '0' + min_c
                    if self._hour < 10:
                        hou_c = '0' + hou_c
                    if self._day < 10:
                        day_c = '0' + day_c
                    # ---------------------------------------------------
                    timer = day_c + ' ' + hou_c + ':' + min_c + ':' + sec_c

                    # print('Дне ', day_start)
                    # print('Час ', hour_start)
                    # print('Мин ', minutes_start)
                    # print('Сек ', sec_start)
                    self.threadTimerSender.emit(timer)
                    if self._step == int(sec_to_get) - 1:
                        check_for_import_in_uc()
                        timer_b = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        timer_a = datetime.datetime.now() + datetime.timedelta(seconds=sec_to_get)
                        timer_a = datetime.datetime.strftime(timer_a, '%Y-%m-%d %H:%M:%S')
                        self.threadBefore.emit(timer_b)
                        self.threadAfter.emit(timer_a)
                        self._step = 0
                    sec_start -= 1
                    time.sleep(1)
                print('Info: Monitoring is stopped')
                logs('Info: Monitoring is stopped', 'info', '6')
                self.threadInfoMessage.emit('Info: Monitoring is stopped')
                self.threadButtonStartE.emit('True')
                self.threadButtonStopD.emit('True')
            except Exception:
                print('Error: Worker(QObject)::task()')
                logs('Error: Worker(QObject)::task()', 'errors', '2')

        def stop(self):
            try:
                self._isRunning = False
            except Exception:
                print('Error: Worker()::top()')
                logs('Error: Worker()::top()', 'errors', '2')
    except Exception:
        print('Error: Worker()')
        logs('Error: Worker()', 'errors', '1')


class Downloader(QThread):
    try:
        pre_progress = pyqtSignal(int)
        progress = pyqtSignal(int)
        done = pyqtSignal(str)
        downloading = pyqtSignal(str)

        def __init__(self, file_url, file_name):
            QThread.__init__(self)
            # Флаг инициализации
            self._init = False
            self.fileUrl = file_url
            self.fileName = file_name
            print('Info: Downloading starting, ' + self.fileUrl)
            logs('Info: Downloading starting, ' + self.fileUrl, 'info', '5')

        def run(self):
            try:
                logs('Info: Downloading TSL', 'info', '5')
                if config['Proxy']['proxyon'] == 'Yes':
                    proxy = request.ProxyHandler(
                        {'https': 'https://' + config['Proxy']['ip'] + ':' + config['Proxy']['port'],
                         'http': 'http://' + config['Proxy']['ip'] + ':' + config['Proxy']['port']})
                    # print(self.fileUrl.split('/')[0])
                    # if self.fileUrl.split('/')[0] == 'https:':
                    #     proxy = request.ProxyHandler(
                    #         {'https': 'https://' + config['Proxy']['ip'] + ':' + config['Proxy']['port']})
                    # else:
                    #     proxy = request.ProxyHandler(
                    #         {'http': 'http://' + config['Proxy']['ip'] + ':' + config['Proxy']['port']})
                    opener = request.build_opener(proxy)
                    request.install_opener(opener)
                    logs('Info: Used proxy', 'info', '7')
                request.urlretrieve(self.fileUrl, self.fileName, self._progress)
            except Exception:
                self.done.emit('Ошибка загрузки')
                logs('Warning: download failed', 'warn', '4')
            else:
                print('Загрузка завершена')
                logs('Info: Downloading successfully', 'info', '5')

                query_get_settings = Settings.select()
                ver_from_tsl = get_info_xlm('current_version')
                ver = 0
                for settings in query_get_settings:
                    ver = settings.value
                    break
                if int(ver) == int(ver_from_tsl):
                    print('Info: update not need')
                    logs('Info: update not need', 'info', '6')
                    self.done.emit('Загрузка завершена, обновление не требуется')
                else:
                    print('Info: Need update')
                    logs('Info: Need update, new version ' + ver_from_tsl + ', old ' + ver, 'info', '6')
                    self.done.emit('Загрузка завершена, требуются обновления Базы УЦ и сертификатов. Новая версия '
                                   + ver_from_tsl + ' текущая версия ' + ver)

                # get_info_xlm('last_update')
                size_tls = os.path.getsize("tsl.xml")
                self.pre_progress.emit(size_tls)
                self.progress.emit(size_tls)

        def _progress(self, block_num, block_size, total_size=int('15000000')):
            total_size = int('15000000')
            print(block_num, block_size, total_size)
            self.downloading.emit('Загрузка.')
            if not self._init:
                self.pre_progress.emit(total_size)
                self._init = True
            # Расчет текущего количества данных
            downloaded = block_num * block_size
            if downloaded < total_size:
                # Отправляем промежуток
                self.progress.emit(downloaded)
            else:
                # Чтобы было 100%
                self.progress.emit(total_size)
    except Exception:
        print('Error: Downloader()')
        logs('Error: Downloader()', 'errors', '1')


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        ico = QIcon()
        pm = QPixmap()
        pm.loadFromData(base64.b64decode(base64_icon))
        ico.addPixmap(pm)
        self.setWindowIcon(QIcon(ico))
        self.window_uc = None
        self.window_add_crl = None
        self.init_settings()
        self.tab_info()
        self.tab_uc()
        self.ui.lineEdit.textChanged[str].connect(self.tab_uc)
        self.tab_cert()
        self.ui.lineEdit_2.textChanged[str].connect(self.tab_cert)
        self.tab_crl()
        self.ui.lineEdit_3.textChanged[str].connect(self.tab_crl)
        self.tab_watching_crl()
        self.sub_tab_watching_crl()
        self.ui.lineEdit_4.textChanged[str].connect(self.sub_tab_watching_crl)
        self.sub_tab_watching_custom_crl()
        self.ui.lineEdit_5.textChanged[str].connect(self.sub_tab_watching_custom_crl)
        self.sub_tab_watching_disabled_crl()
        self.ui.lineEdit_6.textChanged[str].connect(self.sub_tab_watching_disabled_crl)
        self.init_schedule()

    def init_schedule(self):
        if config['Schedule']['allowupdatetslbystart'] == 'Yes':
            self.download_xml()
        if config['Schedule']['allowupdatecrlbystart'] == 'Yes':
            self.check_all_crl()
        #if config['Schedule']['allowschedule'] == 'Yes':
        #    self.worker.task()

    def tab_info(self):
        try:
            ucs = UC.select()
            certs = CERT.select()
            crls = CRL.select()
            watching_crl = WatchingCRL.select()
            watching_custom_crl = WatchingCustomCRL.select()
            settings_ver = '0'
            settings_update_date = '0'
            query = Settings.select()
            for data in query:
                if data.name == 'ver':
                    settings_ver = data.value
                if data.name == 'data_update':
                    settings_update_date = data.value

            self.ui.label_3.setText(" Версия базы: " + settings_ver)
            self.ui.label_2.setText(" Дата выпуска базы: " + settings_update_date.replace('T', ' ').split('.')[0])
            self.ui.label.setText(" Всего УЦ: " + str(ucs.count()))
            self.ui.label_4.setText(" Всего Сертификатов: " + str(certs.count()))
            self.ui.label_5.setText(" Всего CRL: " + str(crls.count()))
            self.ui.label_6.setText(" Мониторится CRL: "
                                    + str(int(watching_crl.count())
                                          + int(watching_custom_crl.count())))
            self.ui.pushButton.clicked.connect(self.download_xml)
            self.ui.pushButton_2.clicked.connect(self.init_xml)
            self.ui.pushButton_13.clicked.connect(self.export_crl)
            self.ui.pushButton_6.pressed.connect(self.import_crl_list)

            watching_crl = WatchingCRL.select().order_by(WatchingCRL.next_update).where(
                WatchingCRL.OGRN == config['Custom']['main_uc_ogrn'])
            self.ui.tableWidget_7.resizeColumnsToContents()
            self.ui.tableWidget_7.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            count = 0
            self.ui.tableWidget_7.setRowCount(watching_crl.count())
            for guc in watching_crl:
                self.ui.tableWidget_7.setItem(count, 0, QTableWidgetItem(str(guc.KeyId)))
                self.ui.tableWidget_7.setItem(count, 1, QTableWidgetItem(str(guc.last_download)))
                self.ui.tableWidget_7.setItem(count, 2, QTableWidgetItem(str(guc.last_update)))
                self.ui.tableWidget_7.setItem(count, 3, QTableWidgetItem(str(guc.next_update)))
                count = count + 1
            self.ui.tableWidget_7.setColumnWidth(1, 180)
            self.ui.tableWidget_7.setColumnWidth(2, 180)
            self.ui.tableWidget_7.setColumnWidth(3, 180)
            self.ui.tableWidget_7.resizeColumnsToContents()
            self.ui.tableWidget_7.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

            watching_crl = WatchingCRL.select().order_by(WatchingCRL.next_update).where(
                WatchingCRL.OGRN == config['Custom']['self_uc_ogrn'])
            self.ui.tableWidget_8.resizeColumnsToContents()
            self.ui.tableWidget_8.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            count = 0
            self.ui.tableWidget_8.setRowCount(watching_crl.count())
            for you_self in watching_crl:
                self.ui.tableWidget_8.setItem(count, 0, QTableWidgetItem(str(you_self.KeyId)))
                self.ui.tableWidget_8.setItem(count, 1, QTableWidgetItem(str(you_self.last_download)))
                self.ui.tableWidget_8.setItem(count, 2, QTableWidgetItem(str(you_self.last_update)))
                self.ui.tableWidget_8.setItem(count, 3, QTableWidgetItem(str(you_self.next_update)))
                count = count + 1
            self.ui.tableWidget_8.setColumnWidth(1, 180)
            self.ui.tableWidget_8.setColumnWidth(2, 180)
            self.ui.tableWidget_8.setColumnWidth(3, 180)
            self.ui.tableWidget_8.resizeColumnsToContents()
            self.ui.tableWidget_8.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

            self.thread = QThread()
            self.thread.start()
            self.worker = MainWorker()
            self.worker.moveToThread(self.thread)

            self.worker.threadTimerSender.connect(lambda y: self.ui.label_36.setText('Время в работе: ' + str(y)))
            self.worker.threadBefore.connect(
                lambda msg: self.ui.label_37.setText('Предыдущее обновление: : ' + str(msg)))
            self.worker.threadAfter.connect(lambda msg: self.ui.label_38.setText('Следующее обновление: ' + str(msg)))
            self.worker.threadButtonStartD.connect(lambda x: self.ui.pushButton_19.setDisabled(True))
            self.worker.threadButtonStopD.connect(lambda z: self.ui.pushButton_20.setDisabled(True))
            self.worker.threadButtonStartE.connect(lambda r: self.ui.pushButton_19.setEnabled(True))
            self.worker.threadButtonStopE.connect(lambda t: self.ui.pushButton_20.setEnabled(True))
            self.worker.threadInfoMessage.connect(lambda msg: self.ui.label_7.setText(msg))
            self.worker.threadInfoMessage.connect(lambda msg: self.ui.label_7.setText(msg))
            self.worker.threadInfoMessage.connect(lambda msg: self.ui.label_7.setText(msg))
            self.ui.pushButton_20.clicked.connect(lambda: self.worker.stop() and self.stop_thread)
            self.ui.pushButton_19.clicked.connect(self.worker.task)
        except Exception:
            print('Error: tab_info()')
            logs('Error: tab_info()', 'errors', '1')

    def tab_uc(self, text=''):
        try:
            self.ui.pushButton_7.pressed.connect(lambda: self.ui.lineEdit.setText(''))
            # .order_by(MyModel.something.desc(nulls='LAST'))
            query = UC.select().order_by(UC.Name).where(UC.Registration_Number.contains(text)
                                                        | UC.INN.contains(text)
                                                        | UC.OGRN.contains(text)
                                                        | UC.Name.contains(text)
                                                        | UC.Full_Name.contains(text)).limit(config['Listing']['uc'])
            count_all = UC.select().where(UC.Registration_Number.contains(text)
                                          | UC.INN.contains(text)
                                          | UC.OGRN.contains(text)
                                          | UC.Name.contains(text)
                                          | UC.Full_Name.contains(text)).limit(config['Listing']['uc']).count()
            self.ui.tableWidget.setRowCount(count_all)
            count = 0

            for row in query:
                self.ui.tableWidget.setItem(count, 0, QTableWidgetItem(str(row.Full_Name)))
                self.ui.tableWidget.setItem(count, 1, QTableWidgetItem(str(row.INN)))
                self.ui.tableWidget.setItem(count, 2, QTableWidgetItem(str(row.OGRN)))

                button_info = QPushButton()
                button_info.setFixedSize(30, 30)
                icon3 = QIcon()
                pm = QPixmap()
                pm.loadFromData(base64.b64decode(base64_info))
                icon3.addPixmap(pm)
                button_info.setIcon(icon3)
                button_info.setFlat(True)
                reg_num = row.Registration_Number
                button_info.pressed.connect(lambda rg=reg_num: self.open_sub_window_info_uc(rg))
                self.ui.tableWidget.setCellWidget(count, 3, button_info)
                count = count + 1
            self.ui.tableWidget.resizeColumnsToContents()
            self.ui.tableWidget.setColumnWidth(3, 30)
            self.ui.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        except Exception:
            print('Error: tab_uc()')
            logs('Error: tab_uc()', 'errors', '1')

    def tab_cert(self, text=''):
        try:
            self.ui.pushButton_8.pressed.connect(lambda: self.ui.lineEdit_2.setText(''))

            icon0 = QIcon()
            pm = QPixmap()
            pm.loadFromData(base64.b64decode(base64_file))
            icon0.addPixmap(pm)
            self.ui.pushButton_22.setIcon(icon0)
            self.ui.pushButton_22.setFlat(True)
            self.ui.pushButton_22.pressed.connect(lambda: os.startfile(os.path.realpath(config['Folders']['certs'])))

            query = CERT.select().where(CERT.Registration_Number.contains(text)
                                        | CERT.Name.contains(text)
                                        | CERT.KeyId.contains(text)
                                        | CERT.Stamp.contains(text)
                                        | CERT.SerialNumber.contains(text)).limit(config['Listing']['cert'])
            count_all = CERT.select().where(CERT.Registration_Number.contains(text)
                                            | CERT.Name.contains(text)
                                            | CERT.KeyId.contains(text)
                                            | CERT.Stamp.contains(text)
                                            | CERT.SerialNumber.contains(text)).limit(config['Listing']['cert']).count()
            self.ui.tableWidget_2.setRowCount(count_all)
            count = 0
            for row in query:
                self.ui.tableWidget_2.setItem(count, 0, QTableWidgetItem(str(row.Name)))
                self.ui.tableWidget_2.setItem(count, 1, QTableWidgetItem(str(row.KeyId)))
                self.ui.tableWidget_2.setItem(count, 2, QTableWidgetItem(str(row.Stamp)))
                self.ui.tableWidget_2.setItem(count, 3, QTableWidgetItem(str(row.SerialNumber)))

                button_cert = QPushButton()
                button_cert.setFixedSize(30, 30)
                icon2 = QIcon()
                pm = QPixmap()
                pm.loadFromData(base64.b64decode(base64_diskette))
                icon2.addPixmap(pm)
                button_cert.setIcon(icon2)
                button_cert.setFlat(True)
                ki = row.KeyId
                # button_cert.pressed.connect(lambda key_id=ki: open_file(key_id, "cer"))
                button_cert.pressed.connect(lambda key_id=ki: save_cert(key_id, config['Folders']['to_uc']))
                self.ui.tableWidget_2.setCellWidget(count, 4, button_cert)

                button_cert_save = QPushButton()
                button_cert_save.setFixedSize(30, 30)
                icon1 = QIcon()
                pm = QPixmap()
                pm.loadFromData(base64.b64decode(base64_diskette))
                icon1.addPixmap(pm)
                button_cert_save.setIcon(icon1)
                button_cert_save.setFlat(True)
                ki = row.KeyId
                button_cert_save.pressed.connect(lambda key_id=ki: save_cert(key_id, config['Folders']['certs']))
                self.ui.tableWidget_2.setCellWidget(count, 5, button_cert_save)
                count = count + 1
            self.ui.tableWidget_2.setColumnWidth(1, 150)
            self.ui.tableWidget_2.setColumnWidth(2, 150)
            self.ui.tableWidget_2.setColumnWidth(3, 150)
            self.ui.tableWidget_2.setColumnWidth(4, 30)
            self.ui.tableWidget_2.setColumnWidth(5, 30)
            self.ui.tableWidget_2.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        except Exception:
            print('Error: tab_cert()')
            logs('Error: tab_cert()', 'errors', '1')

    def tab_crl(self, text=''):
        try:
            self.ui.pushButton_9.pressed.connect(lambda: self.ui.lineEdit_3.setText(''))
            icon9 = QIcon()
            pm = QPixmap()
            pm.loadFromData(base64.b64decode(base64_file))
            icon9.addPixmap(pm)
            self.ui.pushButton_26.setIcon(icon9)
            self.ui.pushButton_26.setFlat(True)
            self.ui.pushButton_26.pressed.connect(lambda: os.startfile(os.path.realpath(config['Folders']['crls'])))

            query = CRL.select().where(CRL.Registration_Number.contains(text)
                                       | CRL.Name.contains(text)
                                       | CRL.KeyId.contains(text)
                                       | CRL.Stamp.contains(text)
                                       | CRL.SerialNumber.contains(text)
                                       | CRL.UrlCRL.contains(text)).limit(config['Listing']['crl'])
            count_all = CRL.select().where(CRL.Registration_Number.contains(text)
                                           | CRL.Name.contains(text)
                                           | CRL.KeyId.contains(text)
                                           | CRL.Stamp.contains(text)
                                           | CRL.SerialNumber.contains(text)
                                           | CRL.UrlCRL.contains(text)).limit(config['Listing']['crl']).count()
            self.ui.tableWidget_3.setRowCount(count_all)
            count = 0
            for row in query:
                self.ui.tableWidget_3.setItem(count, 0, QTableWidgetItem(str(row.Name)))
                self.ui.tableWidget_3.setItem(count, 1, QTableWidgetItem(str(row.KeyId)))
                self.ui.tableWidget_3.setItem(count, 2, QTableWidgetItem(str(row.Stamp)))
                self.ui.tableWidget_3.setItem(count, 3, QTableWidgetItem(str(row.SerialNumber)))
                self.ui.tableWidget_3.setItem(count, 4, QTableWidgetItem(str(row.UrlCRL)))
                button_crl_save = QPushButton()
                button_crl_save.setFixedSize(30, 30)
                icon4 = QIcon()
                pm = QPixmap()
                pm.loadFromData(base64.b64decode(base64_diskette))
                icon4.addPixmap(pm)
                button_crl_save.setIcon(icon4)
                button_crl_save.setFlat(True)
                button_crl_save.pressed.connect(
                    lambda u=row.UrlCRL, s=row.KeyId: download_file(u, s + '.crl', config['Folders']['crls']))
                self.ui.tableWidget_3.setCellWidget(count, 5, button_crl_save)

                button_crl_save = QPushButton()
                button_crl_save.setFixedSize(30, 30)
                icon4 = QIcon()
                pm = QPixmap()
                pm.loadFromData(base64.b64decode(base64_diskette))
                icon4.addPixmap(pm)
                button_crl_save.setIcon(icon4)
                button_crl_save.setFlat(True)
                button_crl_save.pressed.connect(
                    lambda u=row.UrlCRL, s=row.KeyId: download_file(u, s + '.crl', config['Folders']['to_uc']))
                self.ui.tableWidget_3.setCellWidget(count, 6, button_crl_save)

                button_add_to_watch = QPushButton()
                button_add_to_watch.setFixedSize(30, 30)
                icon5 = QIcon()
                pm = QPixmap()
                pm.loadFromData(base64.b64decode(base64_import))
                icon5.addPixmap(pm)
                button_add_to_watch.setIcon(icon5)
                button_add_to_watch.setFlat(True)
                rb = row.Registration_Number
                ki = row.KeyId
                st = row.Stamp
                sn = row.SerialNumber
                uc = row.UrlCRL
                button_add_to_watch.pressed.connect(lambda registration_number=rb,
                                                           keyid=ki,
                                                           stamp=st,
                                                           serial_number=sn,
                                                           url_crl=uc: self.add_watch_current_crl(registration_number,
                                                                                                  keyid,
                                                                                                  stamp,
                                                                                                  serial_number,
                                                                                                  url_crl))
                self.ui.tableWidget_3.setCellWidget(count, 7, button_add_to_watch)

                count = count + 1
            self.ui.tableWidget_3.resizeColumnToContents(0)
            self.ui.tableWidget_3.setColumnWidth(1, 150)
            self.ui.tableWidget_3.setColumnWidth(2, 150)
            self.ui.tableWidget_3.setColumnWidth(3, 150)
            self.ui.tableWidget_3.setColumnWidth(4, 150)
            self.ui.tableWidget_3.setColumnWidth(5, 30)
            self.ui.tableWidget_3.setColumnWidth(6, 30)
            self.ui.tableWidget_3.setColumnWidth(7, 30)
            self.ui.tableWidget_3.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        except Exception:
            print('Error: tab_crl()')
            logs('Error: tab_crl()', 'errors', '1')

    def tab_watching_crl(self):
        self.ui.pushButton_4.pressed.connect(self.download_all_crls)
        self.ui.pushButton_5.clicked.connect(self.check_all_crl)
        self.ui.pushButton_3.clicked.connect(self.export_crl_to_uc)

    def sub_tab_watching_crl(self, text=''):
        try:
            self.ui.label_8.setText('Ищем: ' + text)
            self.ui.label_8.adjustSize()

            self.ui.pushButton_10.pressed.connect(lambda: self.ui.lineEdit_4.setText(''))

            query = WatchingCRL.select().order_by(WatchingCRL.Name).where(WatchingCRL.Name.contains(text)
                                                                          | WatchingCRL.INN.contains(text)
                                                                          | WatchingCRL.OGRN.contains(text)
                                                                          | WatchingCRL.KeyId.contains(text)
                                                                          | WatchingCRL.Stamp.contains(text)
                                                                          | WatchingCRL.SerialNumber.contains(text)
                                                                          | WatchingCRL.UrlCRL.contains(text)).\
                limit(config['Listing']['watch'])
            count_all = WatchingCRL.select().where(WatchingCRL.Name.contains(text)
                                                   | WatchingCRL.INN.contains(text)
                                                   | WatchingCRL.OGRN.contains(text)
                                                   | WatchingCRL.KeyId.contains(text)
                                                   | WatchingCRL.Stamp.contains(text)
                                                   | WatchingCRL.SerialNumber.contains(text)
                                                   | WatchingCRL.UrlCRL.contains(text)).limit(
                config['Listing']['watch']).count()
            self.ui.tableWidget_4.setRowCount(count_all)
            count = 0
            brush = QBrush(QColor(0, 255, 0, 255))
            brush.setStyle(Qt.SolidPattern)
            for row in query:
                self.ui.tableWidget_4.setItem(count, 0, QTableWidgetItem(str(row.Name)))
                self.ui.tableWidget_4.setItem(count, 1, QTableWidgetItem(str(row.OGRN)))
                self.ui.tableWidget_4.setItem(count, 2, QTableWidgetItem(str(row.KeyId)))
                self.ui.tableWidget_4.setItem(count, 3, QTableWidgetItem(str(row.UrlCRL)))
                self.ui.tableWidget_4.setItem(count, 4, QTableWidgetItem(str(row.last_download)))
                self.ui.tableWidget_4.setItem(count, 5, QTableWidgetItem(str(row.next_update)))

                if row.status == 'Info: Filetype good':
                    status_item = QTableWidgetItem()
                    status_icon = QIcon()
                    pm = QPixmap()
                    pm.loadFromData(base64.b64decode(base64_white_list))
                    status_icon.addPixmap(pm)
                    status_item.setIcon(status_icon)
                    self.ui.tableWidget_4.setItem(count, 6, status_item)
                else:
                    status_item_2 = QTableWidgetItem()
                    status_icon_2 = QIcon()
                    pm = QPixmap()
                    pm.loadFromData(base64.b64decode(base64_black_list))
                    status_icon_2.addPixmap(pm)
                    status_item_2.setIcon(status_icon_2)
                    self.ui.tableWidget_4.setItem(count, 6, status_item_2)

                button_crl_to_uc = QPushButton()
                button_crl_to_uc.setFixedSize(30, 30)
                icon6 = QIcon()
                pm = QPixmap()
                pm.loadFromData(base64.b64decode(base64_diskette))
                icon6.addPixmap(pm)
                button_crl_to_uc.setIcon(icon6)
                button_crl_to_uc.setFlat(True)
                row_key_id = row.KeyId
                button_crl_to_uc.pressed.connect(
                    lambda rki=row_key_id: shutil.copy2(config['Folders']['crls'] + '/' + rki + '.crl',
                                                        config['Folders']['to_uc'] + '/' + rki + '.crl'))
                self.ui.tableWidget_4.setCellWidget(count, 7, button_crl_to_uc)

                button_delete_watch = QPushButton()
                button_delete_watch.setFixedSize(30, 30)
                icon6 = QIcon()
                pm = QPixmap()
                pm.loadFromData(base64.b64decode(base64_export))
                icon6.addPixmap(pm)
                button_delete_watch.setIcon(icon6)
                button_delete_watch.setFlat(True)
                id_row = row.ID
                button_delete_watch.pressed.connect(lambda o=id_row: self.move_watching_to_passed(o, 'current'))
                self.ui.tableWidget_4.setCellWidget(count, 8, button_delete_watch)
                count = count + 1
            self.ui.tableWidget_4.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            self.ui.tableWidget_4.setColumnWidth(1, 100)
            self.ui.tableWidget_4.setColumnWidth(2, 150)
            self.ui.tableWidget_4.setColumnWidth(3, 150)
            self.ui.tableWidget_4.setColumnWidth(4, 150)
            self.ui.tableWidget_4.setColumnWidth(5, 150)
            self.ui.tableWidget_4.setColumnWidth(6, 30)
            self.ui.tableWidget_4.setColumnWidth(7, 30)
            self.ui.tableWidget_4.setColumnWidth(8, 30)
        except Exception:
            print('Error: sub_tab_watching_crl()')
            logs('Error: sub_tab_watching_crl()', 'errors', '1')

    def sub_tab_watching_custom_crl(self, text=''):
        try:
            self.ui.label_8.setText('Ищем: ' + text)
            self.ui.label_8.adjustSize()

            self.ui.pushButton_11.pressed.connect(lambda: self.ui.lineEdit_5.setText(''))
            self.ui.pushButton_25.pressed.connect(lambda: self.open_sub_window_add())

            query = WatchingCustomCRL.select().order_by(WatchingCustomCRL.Name)\
                .where(WatchingCustomCRL.Name.contains(text)
                       | WatchingCustomCRL.INN.contains(text)
                       | WatchingCustomCRL.OGRN.contains(text)
                       | WatchingCustomCRL.KeyId.contains(text)
                       | WatchingCustomCRL.Stamp.contains(text)
                       | WatchingCustomCRL.SerialNumber.contains(text)
                       | WatchingCustomCRL.UrlCRL.contains(text)). \
                limit(config['Listing']['watch'])
            count_all = WatchingCustomCRL.select().where(WatchingCustomCRL.Name.contains(text)
                                                         | WatchingCustomCRL.INN.contains(text)
                                                         | WatchingCustomCRL.OGRN.contains(text)
                                                         | WatchingCustomCRL.KeyId.contains(text)
                                                         | WatchingCustomCRL.Stamp.contains(text)
                                                         | WatchingCustomCRL.SerialNumber.contains(text)
                                                         | WatchingCustomCRL.UrlCRL.contains(text)). \
                limit(config['Listing']['watch']).count()
            self.ui.tableWidget_5.setRowCount(count_all)
            count = 0
            for row in query:
                self.ui.tableWidget_5.setItem(count, 0, QTableWidgetItem(str(row.Name)))
                self.ui.tableWidget_5.setItem(count, 1, QTableWidgetItem(str(row.OGRN)))
                self.ui.tableWidget_5.setItem(count, 2, QTableWidgetItem(str(row.KeyId)))
                self.ui.tableWidget_5.setItem(count, 3, QTableWidgetItem(str(row.UrlCRL)))
                self.ui.tableWidget_5.setItem(count, 4, QTableWidgetItem(str(row.last_download)))
                self.ui.tableWidget_5.setItem(count, 5, QTableWidgetItem(str(row.next_update)))

                if row.status == 'Info: Filetype good':
                    status_item = QTableWidgetItem()
                    status_icon = QIcon()
                    pm = QPixmap()
                    pm.loadFromData(base64.b64decode(base64_white_list))
                    status_icon.addPixmap(pm)
                    status_item.setIcon(status_icon)
                    self.ui.tableWidget_5.setItem(count, 6, status_item)
                else:
                    status_item_2 = QTableWidgetItem()
                    status_icon_2 = QIcon()
                    pm = QPixmap()
                    pm.loadFromData(base64.b64decode(base64_black_list))
                    status_icon_2.addPixmap(pm)
                    status_item_2.setIcon(status_icon_2)
                    self.ui.tableWidget_5.setItem(count, 6, status_item_2)

                button_crl_to_uc = QPushButton()
                button_crl_to_uc.setFixedSize(30, 30)
                icon6 = QIcon()
                pm = QPixmap()
                pm.loadFromData(base64.b64decode(base64_diskette))
                icon6.addPixmap(pm)
                button_crl_to_uc.setIcon(icon6)
                button_crl_to_uc.setFlat(True)
                row_key_id = row.KeyId
                button_crl_to_uc.pressed.connect(
                    lambda rki=row_key_id: shutil.copy2(config['Folders']['crls'] + '/' + rki + '.crl',
                                                        config['Folders']['to_uc'] + '/' + rki + '.crl'))
                self.ui.tableWidget_5.setCellWidget(count, 7, button_crl_to_uc)

                button_delete_watch = QPushButton()
                button_delete_watch.setFixedSize(30, 30)
                icon7 = QIcon()
                pm = QPixmap()
                pm.loadFromData(base64.b64decode(base64_export))
                icon7.addPixmap(pm)
                button_delete_watch.setIcon(icon7)
                button_delete_watch.setFlat(True)
                id_row = row.ID
                button_delete_watch.pressed.connect(lambda o=id_row: self.move_watching_to_passed(o, 'custom'))
                self.ui.tableWidget_5.setCellWidget(count, 8, button_delete_watch)

                count = count + 1

            self.ui.tableWidget_5.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            self.ui.tableWidget_5.setColumnWidth(1, 100)
            self.ui.tableWidget_5.setColumnWidth(2, 150)
            self.ui.tableWidget_5.setColumnWidth(3, 150)
            self.ui.tableWidget_5.setColumnWidth(4, 150)
            self.ui.tableWidget_5.setColumnWidth(4, 150)
            self.ui.tableWidget_5.setColumnWidth(5, 150)
            self.ui.tableWidget_5.setColumnWidth(6, 30)
            self.ui.tableWidget_5.setColumnWidth(7, 30)
            self.ui.tableWidget_5.setColumnWidth(8, 30)
        except Exception:
            print('Error: sub_tab_watching_custom_crl()')
            logs('Error: sub_tab_watching_custom_crl()', 'errors', '1')

    def sub_tab_watching_disabled_crl(self, text=''):
        try:
            self.ui.label_8.setText('Ищем: ' + text)
            self.ui.label_8.adjustSize()

            self.ui.pushButton_12.pressed.connect(lambda: self.ui.lineEdit_6.setText(''))

            query = WatchingDeletedCRL.select().order_by(WatchingDeletedCRL.Name).\
                where(WatchingDeletedCRL.Name.contains(text)
                      | WatchingDeletedCRL.INN.contains(text)
                      | WatchingDeletedCRL.OGRN.contains(text)
                      | WatchingDeletedCRL.KeyId.contains(text)
                      | WatchingDeletedCRL.Stamp.contains(text)
                      | WatchingDeletedCRL.SerialNumber.contains(text)
                      | WatchingDeletedCRL.UrlCRL.contains(text)). \
                limit(config['Listing']['watch'])
            count_all = WatchingDeletedCRL.select().where(WatchingDeletedCRL.Name.contains(text)
                                                          | WatchingDeletedCRL.INN.contains(text)
                                                          | WatchingDeletedCRL.OGRN.contains(text)
                                                          | WatchingDeletedCRL.KeyId.contains(text)
                                                          | WatchingDeletedCRL.Stamp.contains(text)
                                                          | WatchingDeletedCRL.SerialNumber.contains(text)
                                                          | WatchingDeletedCRL.UrlCRL.contains(text)). \
                limit(config['Listing']['watch']).count()
            self.ui.tableWidget_6.setRowCount(count_all)
            count = 0
            for row in query:
                self.ui.tableWidget_6.setItem(count, 0, QTableWidgetItem(str(row.Name)))
                self.ui.tableWidget_6.setItem(count, 1, QTableWidgetItem(str(row.OGRN)))
                self.ui.tableWidget_6.setItem(count, 2, QTableWidgetItem(str(row.KeyId)))
                self.ui.tableWidget_6.setItem(count, 3, QTableWidgetItem(str(row.Stamp)))
                self.ui.tableWidget_6.setItem(count, 4, QTableWidgetItem(str(row.SerialNumber)))
                self.ui.tableWidget_6.setItem(count, 5, QTableWidgetItem(str(row.UrlCRL)))

                buttonReturnWatch = QPushButton()
                buttonReturnWatch.setFixedSize(30, 30)
                icon8 = QIcon()
                pm = QPixmap()
                pm.loadFromData(base64.b64decode(base64_import))
                icon8.addPixmap(pm)
                buttonReturnWatch.setIcon(icon8)
                buttonReturnWatch.setFlat(True)
                id_row = row.ID
                buttonReturnWatch.pressed.connect(lambda o=id_row: self.move_passed_to_watching(o))
                self.ui.tableWidget_6.setCellWidget(count, 6, buttonReturnWatch)
                count = count + 1

            self.ui.tableWidget_6.setColumnWidth(1, 100)
            self.ui.tableWidget_6.setColumnWidth(2, 150)
            self.ui.tableWidget_6.setColumnWidth(3, 150)
            self.ui.tableWidget_6.setColumnWidth(4, 150)
            self.ui.tableWidget_6.setColumnWidth(5, 150)
            self.ui.tableWidget_6.setColumnWidth(6, 30)
            self.ui.tableWidget_6.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        except Exception:
            print('Error: sub_tab_watching_off_crl()')
            logs('Error: sub_tab_watching_off_crl()', 'errors', '1')

    def init_settings(self):
        try:
            # main config
            self.ui.lineEdit_13.setText(config['Tabs']['ucLimit'])
            self.ui.lineEdit_18.setText(config['Tabs']['certLimit'])
            self.ui.lineEdit_17.setText(config['Tabs']['crlLimit'])
            self.ui.lineEdit_16.setText(config['Tabs']['wcLimit'])
            self.ui.lineEdit_15.setText(config['Tabs']['wccLimit'])
            self.ui.lineEdit_14.setText(config['Tabs']['wcdLimit'])
            self.ui.lineEdit_19.setText(config['XMPP']['server'])
            self.ui.lineEdit_20.setText(config['XMPP']['login'])
            self.ui.lineEdit_21.setText(config['XMPP']['password'])
            self.ui.lineEdit_22.setText(config['XMPP']['tosend'])

            if config['XMPP']['sendinfoerr'] == 'Yes':
                self.ui.checkBox_10.setChecked(True)
            if config['XMPP']['sendinfonewcrl'] == 'Yes':
                self.ui.checkBox_9.setChecked(True)
            if config['XMPP']['sendinfonewtsl'] == 'Yes':
                self.ui.checkBox_11.setChecked(True)

            if config['Sec']['allowImportCRL'] == 'Yes':
                self.ui.checkBox_4.setChecked(True)
            else:
                self.ui.pushButton_6.setDisabled(True)
            if config['Sec']['allowExportCRL'] == 'Yes':
                self.ui.checkBox_5.setChecked(True)
            else:
                self.ui.pushButton_13.setDisabled(True)
            if config['Sec']['allowDeleteWatchingCRL'] == 'Yes':
                self.ui.checkBox_6.setChecked(True)
                # self.ui.pushButton_X.setDisabled(True)
            if config['Sec']['allowDownloadButtonCRL'] == 'Yes':
                self.ui.checkBox_7.setChecked(True)
            else:
                self.ui.pushButton_4.setDisabled(True)
            if config['Sec']['allowCheckButtonCRL'] == 'Yes':
                self.ui.checkBox_8.setChecked(True)
            else:
                self.ui.pushButton_5.setDisabled(True)

            # Sub  config
            self.ui.lineEdit_12.setText(config['MainWindow']['height'])
            self.ui.lineEdit_11.setText(config['MainWindow']['width'])
            self.resize(int(config['MainWindow']['width']), int(config['MainWindow']['height']))
            if config['MainWindow']['saveWidth'] == 'No':
                self.ui.checkBox_3.setChecked(True)
            if config['MainWindow']['AllowResize'] == 'No':
                self.ui.checkBox_2.setChecked(True)
                self.setMinimumSize(int(config['MainWindow']['width']), int(config['MainWindow']['height']))
                self.setMaximumSize(int(config['MainWindow']['width']), int(config['MainWindow']['height']))

            self.ui.comboBox.setCurrentText(config['Logs']['loglevel'])
            self.ui.spinBox.setValue(int(config['Logs']['dividelogsbysize']))
            if config['Logs']['dividelogsbyday'] == 'Yes':
                self.ui.checkBox_14.setChecked(True)

            if config['Schedule']['allowupdatecrlbystart'] == 'Yes':
                self.ui.checkBox_12.setChecked(True)
            else:
                self.ui.pushButton_12.setDisabled(True)
            if config['Schedule']['allowupdatetslbystart'] == 'Yes':
                self.ui.checkBox_13.setChecked(True)
            else:
                self.ui.pushButton_13.setDisabled(True)
            # download config
            self.ui.label_13.setText(config['Folders']['crls'])
            self.ui.label_12.setText(config['Folders']['certs'])
            self.ui.label_11.setText(config['Folders']['uc'])
            self.ui.label_10.setText(config['Folders']['tmp'])
            self.ui.label_9.setText(config['Folders']['to_uc'])

            self.ui.pushButton_18.clicked.connect(lambda: self.choose_directory('crl'))
            self.ui.pushButton_17.clicked.connect(lambda: self.choose_directory('cert'))
            self.ui.pushButton_16.clicked.connect(lambda: self.choose_directory('uc'))
            self.ui.pushButton_15.clicked.connect(lambda: self.choose_directory('tmp'))
            self.ui.pushButton_14.clicked.connect(lambda: self.choose_directory('to_uc'))

            self.ui.lineEdit_7.setText(config['Proxy']['ip'])
            self.ui.lineEdit_8.setText(config['Proxy']['port'])
            self.ui.lineEdit_9.setText(config['Proxy']['login'])
            self.ui.lineEdit_10.setText(config['Proxy']['password'])

            if config['Proxy']['proxyon'] == 'No':
                self.ui.checkBox.setChecked(False)
                self.ui.lineEdit_7.setDisabled(True)
                self.ui.lineEdit_8.setDisabled(True)
                self.ui.lineEdit_9.setDisabled(True)
                self.ui.lineEdit_10.setDisabled(True)
            elif config['Proxy']['proxyon'] == 'Yes':
                self.ui.checkBox.setChecked(True)
                self.ui.lineEdit_7.setEnabled(True)
                self.ui.lineEdit_8.setEnabled(True)
                self.ui.lineEdit_9.setEnabled(True)
                self.ui.lineEdit_10.setEnabled(True)

            # Logs
            if config['Logs']['dividelogsbyday'] == 'Yes':
                datetime_day = '_' + datetime.datetime.now().strftime('%Y%m%d')
            else:
                datetime_day = ''

            try:
                self.ui.textBrowser.setText(
                    open(config['Folders']['logs'] + '/log' + datetime_day + '.log', 'r').read())
            except Exception:
                print('Error: init_settings()::Filed_open_log::logs/log' + datetime_day + '.log')
                logs('Error: init_settings()::Filed_open_log::logs/log' + datetime_day + '.log', 'errors', '2')
            try:
                self.ui.textBrowser_2.setText(
                    open(config['Folders']['logs'] + '/error' + datetime_day + '.log', 'r').read())
            except Exception:
                print('Error: init_settings()::Filed_open_log::logs/error' + datetime_day + '.log')
                logs('Error: init_settings()::Filed_open_log::logs/error' + datetime_day + '.log', 'errors', '2')

            self.ui.pushButton_21.pressed.connect(lambda: self.save_settings_main())
            self.ui.pushButton_23.pressed.connect(lambda: self.save_settings_sub())
            self.ui.pushButton_24.pressed.connect(lambda: self.save_settings_logs())
        except Exception:
            print('Error: init_settings()')
            logs('Error: init_settings()', 'errors', '1')

    def save_settings_main(self):
        try:
            set_value_in_property_file('settings.ini', 'Tabs', 'ucLimit', self.ui.lineEdit_13.text())
            set_value_in_property_file('settings.ini', 'Tabs', 'certLimit', self.ui.lineEdit_18.text())
            set_value_in_property_file('settings.ini', 'Tabs', 'crlLimit', self.ui.lineEdit_17.text())
            set_value_in_property_file('settings.ini', 'Tabs', 'wcLimit', self.ui.lineEdit_16.text())
            set_value_in_property_file('settings.ini', 'Tabs', 'wccLimit', self.ui.lineEdit_15.text())
            set_value_in_property_file('settings.ini', 'Tabs', 'wcdLimit', self.ui.lineEdit_14.text())
            set_value_in_property_file('settings.ini', 'MainWindow', 'height', self.ui.lineEdit_12.text())
            set_value_in_property_file('settings.ini', 'MainWindow', 'width', self.ui.lineEdit_11.text())
            set_value_in_property_file('settings.ini', 'XMPP', 'server', self.ui.lineEdit_19.text())
            set_value_in_property_file('settings.ini', 'XMPP', 'login', self.ui.lineEdit_20.text())
            set_value_in_property_file('settings.ini', 'XMPP', 'password', self.ui.lineEdit_21.text())
            set_value_in_property_file('settings.ini', 'XMPP', 'tosend', self.ui.lineEdit_22.text())

            if self.ui.checkBox_10.checkState() == 0:
                set_value_in_property_file('settings.ini', 'XMPP', 'sendinfoerr', 'No')
            elif self.ui.checkBox_10.checkState() == 2:
                set_value_in_property_file('settings.ini', 'XMPP', 'sendinfoerr', 'Yes')
            if self.ui.checkBox_9.checkState() == 0:
                set_value_in_property_file('settings.ini', 'XMPP', 'sendinfonewcrl', 'No')
            elif self.ui.checkBox_9.checkState() == 2:
                set_value_in_property_file('settings.ini', 'XMPP', 'sendinfonewcrl', 'Yes')
            if self.ui.checkBox_11.checkState() == 0:
                set_value_in_property_file('settings.ini', 'XMPP', 'sendinfonewtsl', 'No')
            elif self.ui.checkBox_11.checkState() == 2:
                set_value_in_property_file('settings.ini', 'XMPP', 'sendinfonewtsl', 'Yes')

            if self.ui.checkBox_3.checkState() == 0:
                set_value_in_property_file('settings.ini', 'MainWindow', 'allowresize', 'Yes')
                self.resize(int(config['MainWindow']['width']), int(config['MainWindow']['height']))
                self.setMinimumSize(0, 0)
                self.setMaximumSize(16777215, 16777215)
            elif self.ui.checkBox_3.checkState() == 2:
                set_value_in_property_file('settings.ini', 'MainWindow', 'allowresize', 'No')
                self.resize(int(config['MainWindow']['width']), int(config['MainWindow']['height']))
                self.setMinimumSize(int(config['MainWindow']['width']), int(config['MainWindow']['height']))
                self.setMaximumSize(int(config['MainWindow']['width']), int(config['MainWindow']['height']))

            if self.ui.checkBox_2.checkState() == 0:
                set_value_in_property_file('settings.ini', 'MainWindow', 'savewidth', 'No')
            elif self.ui.checkBox_2.checkState() == 2:
                set_value_in_property_file('settings.ini', 'MainWindow', 'savewidth', 'Yes')

            if self.ui.checkBox_4.checkState() == 0:
                set_value_in_property_file('settings.ini', 'Sec', 'allowImportCRL', 'No')
                self.ui.pushButton_6.setDisabled(True)
            elif self.ui.checkBox_4.checkState() == 2:
                set_value_in_property_file('settings.ini', 'Sec', 'allowImportCRL', 'Yes')
                self.ui.pushButton_6.setEnabled(True)
            if self.ui.checkBox_5.checkState() == 0:
                set_value_in_property_file('settings.ini', 'Sec', 'allowExportCRL', 'No')
                self.ui.pushButton_13.setDisabled(True)
            elif self.ui.checkBox_5.checkState() == 2:
                set_value_in_property_file('settings.ini', 'Sec', 'allowExportCRL', 'Yes')
                self.ui.pushButton_13.setEnabled(True)
            if self.ui.checkBox_6.checkState() == 0:
                set_value_in_property_file('settings.ini', 'Sec', 'allowDeleteWatchingCRL', 'No')
            elif self.ui.checkBox_6.checkState() == 2:
                set_value_in_property_file('settings.ini', 'Sec', 'allowDeleteWatchingCRL', 'Yes')
            if self.ui.checkBox_7.checkState() == 0:
                set_value_in_property_file('settings.ini', 'Sec', 'allowDownloadButtonCRL', 'No')
                self.ui.pushButton_4.setDisabled(True)
            elif self.ui.checkBox_7.checkState() == 2:
                set_value_in_property_file('settings.ini', 'Sec', 'allowDownloadButtonCRL', 'Yes')
                self.ui.pushButton_4.setEnabled(True)
            if self.ui.checkBox_8.checkState() == 0:
                set_value_in_property_file('settings.ini', 'Sec', 'allowCheckButtonCRL', 'No')
                self.ui.pushButton_5.setDisabled(True)
            elif self.ui.checkBox_8.checkState() == 2:
                set_value_in_property_file('settings.ini', 'Sec', 'allowCheckButtonCRL', 'Yes')
                self.ui.pushButton_5.setEnabled(True)
            self.ui.label_27.setText('Настройки сохранены')
            print('Info: save_settings_main()::Saved')
            logs('Info: save_settings_main()::Saved', 'info', '6')
        except Exception:
            print('Error: save_settings_main()')
            logs('Error: save_settings_main()', 'errors', '1')

    def save_settings_sub(self):
        try:
            set_value_in_property_file('settings.ini', 'Folders', 'certs', self.ui.label_12.text())
            set_value_in_property_file('settings.ini', 'Folders', 'crls', self.ui.label_13.text())
            set_value_in_property_file('settings.ini', 'Folders', 'tmp', self.ui.label_10.text())
            set_value_in_property_file('settings.ini', 'Folders', 'uc', self.ui.label_11.text())
            set_value_in_property_file('settings.ini', 'Folders', 'to_uc', self.ui.label_9.text())

            set_value_in_property_file('settings.ini', 'Proxy', 'ip', self.ui.lineEdit_7.text())
            set_value_in_property_file('settings.ini', 'Proxy', 'port', self.ui.lineEdit_8.text())
            set_value_in_property_file('settings.ini', 'Proxy', 'login', self.ui.lineEdit_9.text())
            set_value_in_property_file('settings.ini', 'Proxy', 'password', self.ui.lineEdit_10.text())

            if self.ui.checkBox_12.checkState() == 0:
                set_value_in_property_file('settings.ini', 'Schedule', 'allowupdatecrlbystart', 'No')
            elif self.ui.checkBox_12.checkState() == 2:
                set_value_in_property_file('settings.ini', 'Schedule', 'allowupdatecrlbystart', 'Yes')
            if self.ui.checkBox_13.checkState() == 0:
                set_value_in_property_file('settings.ini', 'Schedule', 'allowupdatetslbystart', 'No')
            elif self.ui.checkBox_13.checkState() == 2:
                set_value_in_property_file('settings.ini', 'Schedule', 'allowupdatetslbystart', 'Yes')

            if self.ui.checkBox.checkState() == 0:
                set_value_in_property_file('settings.ini', 'Proxy', 'proxyon', 'No')
                self.ui.lineEdit_7.setDisabled(True)
                self.ui.lineEdit_8.setDisabled(True)
                self.ui.lineEdit_9.setDisabled(True)
                self.ui.lineEdit_10.setDisabled(True)
            elif self.ui.checkBox.checkState() == 2:
                set_value_in_property_file('settings.ini', 'Proxy', 'proxyon', 'Yes')
                self.ui.lineEdit_7.setEnabled(True)
                self.ui.lineEdit_8.setEnabled(True)
                self.ui.lineEdit_9.setEnabled(True)
                self.ui.lineEdit_10.setEnabled(True)

            set_value_in_property_file('settings.ini', 'Logs', 'loglevel', self.ui.comboBox.currentText())
            set_value_in_property_file('settings.ini', 'Logs', 'dividelogsbysize', str(self.ui.spinBox.value()))
            if self.ui.checkBox_14.checkState() == 0:
                set_value_in_property_file('settings.ini', 'Logs', 'dividelogsbyday', 'No')
            elif self.ui.checkBox_14.checkState() == 2:
                set_value_in_property_file('settings.ini', 'Logs', 'dividelogsbyday', 'Yes')

            self.ui.label_28.setText('Настройки сохранены')
            print('Info: save_settings_sub()::Saved')
            logs('Info: save_settings_sub()::Saved', 'info', '6')
        except Exception:
            print('Error: save_settings_sub()')
            logs('Error: save_settings_sub()', 'errors', '1')

    def init_xml(self):
        try:
            self.ui.pushButton_2.setEnabled(False)
            self.ui.pushButton.setEnabled(False)
            UC.drop_table()
            CRL.drop_table()
            CERT.drop_table()
            UC.create_table()
            CERT.create_table()
            CRL.create_table()
            self.ui.label_7.setText('Обрабатываем данные.')
            logs('Info: Init TLS started', 'info', '5')
            with open('tsl.xml', "rt", encoding="utf-8") as obj:
                xml = obj.read().encode()

            root = etree.fromstring(xml)
            uc_count = 0
            cert_count = 0
            crl_count = 0
            crl_count_all = 3267
            current_version = 'Unknown'
            last_update = 'Unknown'
            for appt in root.getchildren():
                QCoreApplication.processEvents()
                address_code = ''
                address_name = ''
                address_index = ''
                address_address = ''
                address_street = ''
                address_town = ''
                registration_number = ''
                inn = ''
                ogrn = ''
                full_name = ''
                email = ''
                name = ''
                url = ''
                key_id = ''
                stamp = ''
                serial_number = ''
                cert_base64 = ''
                cert_data = []
                if appt.text:
                    if appt.tag == 'Версия':
                        current_version = appt.text
                if appt.text:
                    if appt.tag == 'Дата':
                        last_update = appt.text
                for elem in appt.getchildren():
                    if not elem.text:
                        for sub_elem in elem.getchildren():
                            if not sub_elem.text:
                                for two_elem in sub_elem.getchildren():
                                    if not two_elem.text:
                                        for tree_elem in two_elem.getchildren():
                                            if not tree_elem.text:
                                                if tree_elem.tag == 'Ключ':
                                                    data_cert = {}
                                                    adr_crl = []
                                                    key_ident = {}
                                                    for four_elem in tree_elem.getchildren():
                                                        if not four_elem.text:
                                                            for five_elem in four_elem.getchildren():
                                                                if not five_elem.text:
                                                                    for six_elem in five_elem.getchildren():
                                                                        if six_elem.text:
                                                                            if six_elem.tag == 'Отпечаток':
                                                                                data_cert['stamp'] = six_elem.text
                                                                            if six_elem.tag == 'СерийныйНомер':
                                                                                cert_count = cert_count + 1
                                                                                data_cert['serrial'] = six_elem.text
                                                                            if six_elem.tag == 'Данные':
                                                                                data_cert['data'] = six_elem.text
                                                                else:
                                                                    if five_elem.tag == 'Адрес':
                                                                        five_text = five_elem.text
                                                                        adr_crl.append(five_text)
                                                                        crl_count = crl_count + 1
                                                        else:
                                                            four_text = four_elem.text
                                                            if four_elem.tag == 'ИдентификаторКлюча':
                                                                key_ident['keyid'] = four_text
                                                    cert_data.append([key_ident, data_cert, adr_crl])
                                    else:
                                        two_text = two_elem.text
                                        if two_elem.tag == 'Код':
                                            address_code = two_text
                                        if two_elem.tag == 'Название':
                                            address_name = two_text
                            else:
                                sub_text = sub_elem.text
                                if sub_elem.tag == 'Индекс':
                                    address_index = sub_text
                                if sub_elem.tag == 'УлицаДом':
                                    address_street = sub_text
                                if sub_elem.tag == 'Город':
                                    address_town = sub_text
                                if sub_elem.tag == 'Страна':
                                    address_address = sub_text
                    else:
                        text = elem.text
                        if elem.tag == 'Название':
                            full_name = text
                        if elem.tag == 'ЭлектроннаяПочта':
                            email = text
                        if elem.tag == 'КраткоеНазвание':
                            name = text
                        if elem.tag == 'АдресСИнформациейПоУЦ':
                            url = text
                        if elem.tag == 'ИНН':
                            inn = text
                        if elem.tag == 'ОГРН':
                            ogrn = text
                        if elem.tag == 'РеестровыйНомер':
                            registration_number = text
                            uc_count = uc_count + 1
                if registration_number != '':
                    self.ui.label_7.setText('Обрабатываем данные:\n УЦ: ' + name)
                    logs('Info: Processing - UC:' + name, 'info', '6')
                    uc = UC(Registration_Number=registration_number,
                            INN=inn,
                            OGRN=ogrn,
                            Full_Name=full_name,
                            Email=email,
                            Name=name,
                            URL=url,
                            AddresCode=address_code,
                            AddresName=address_name,
                            AddresIndex=address_index,
                            AddresAddres=address_address,
                            AddresStreet=address_street,
                            AddresTown=address_town)
                    uc.save()
                    for cert in cert_data:
                        if type(cert_data) == list:
                            for data in cert:
                                if type(data) == dict:
                                    for var, dats in data.items():
                                        if var == 'keyid':
                                            key_id = dats
                                        if var == 'stamp':
                                            stamp = dats
                                        if var == 'serrial':
                                            serial_number = dats
                                        if var == 'data':
                                            cert_base64 = dats

                                if type(data) == list:
                                    for dats in data:
                                        url_crl = dats
                                        crl = CRL(Registration_Number=registration_number,
                                                  Name=name,
                                                  KeyId=key_id,
                                                  Stamp=stamp,
                                                  SerialNumber=serial_number,
                                                  UrlCRL=url_crl)
                                        crl.save()
                        cert = CERT(Registration_Number=registration_number,
                                    Name=name,
                                    KeyId=key_id,
                                    Stamp=stamp,
                                    SerialNumber=serial_number,
                                    Data=cert_base64)
                        cert.save()

                        # uc_percent_step = int(math.floor(100 / (uc_count_all / uc_count)))
                        # cert_percent_step = int(math.floor(100 / (cert_count_all / cert_count)))
                        crl_percent_step = int(math.floor(100 / (crl_count_all / crl_count)))
                        self.ui.progressBar_2.setValue(crl_percent_step)
            self.ui.label_3.setText(" Версия базы: " + current_version)
            self.ui.label_2.setText(" Дата выпуска базы: " + last_update.replace('T', ' ').split('.')[0])
            self.ui.label.setText(" Всего УЦ: " + str(uc_count))
            self.ui.label_4.setText(" Всего Сертификатов: " + str(cert_count))
            self.ui.label_5.setText(" Всего CRL: " + str(crl_count))

            query_ver = Settings.update(value=current_version).where(Settings.name == 'ver')
            query_ver.execute()
            query_data_update = Settings.update(value=last_update).where(Settings.name == 'data_update')
            query_data_update.execute()
            self.ui.pushButton.setEnabled(True)
            self.ui.pushButton_2.setEnabled(True)
            self.ui.label_7.setText('Готово.')
            logs('Info: Processing successful done', 'info', '6')
        except Exception:
            print('Error: init_xml()')
            logs('Error: init_xml()', 'errors', '1')

    def open_sub_window_info_uc(self, reg_number):
        try:
            if self.window_uc is None:
                self.window_uc = UcWindow(reg_number)
                self.window_uc.show()
            else:
                self.window_uc.close()  # Close window.
                self.window_uc = None  # Discard reference.
        except Exception:
            print('Error: open_sub_window_info_uc()')
            logs('Error: open_sub_window_info_uc()', 'errors', '1')

    def open_sub_window_add(self):
        try:
            if self.window_add_crl is None:
                self.window_add_crl = AddCRLWindow()
                self.window_add_crl.show()
            else:
                self.window_add_crl.close()  # Close window.
                self.window_add_crl = None  # Discard reference.
        except Exception:
            print('Error: open_sub_window_info_uc()')
            logs('Error: open_sub_window_info_uc()', 'errors', '1')

    def choose_directory(self, type):
        try:
            input_dir = QFileDialog.getExistingDirectory(None, 'Выбор директории:', os.path.expanduser("~"))
            if type == 'crl':
                self.ui.label_13.setText(input_dir)
            if type == 'cert':
                self.ui.label_12.setText(input_dir)
            if type == 'uc':
                self.ui.label_11.setText(input_dir)
            if type == 'tmp':
                self.ui.label_10.setText(input_dir)
            if type == 'to_uc':
                self.ui.label_9.setText(input_dir)
        except Exception:
            print('Error: choose_directory()')
            logs('Error: choose_directory()', 'errors', '1')

    def check_all_crl(self):
        try:
            query_1 = WatchingCRL.select()
            query_2 = WatchingCustomCRL.select()
            self.ui.pushButton_5.setEnabled(False)
            self.ui.label_8.setText('Проверяем основной список CRL')
            for wc in query_1:
                check_crl(wc.ID, wc.Name, wc.KeyId, wc.UrlCRL)
            self.ui.label_8.setText('Проверяем свой список CRL')
            for wcc in query_2:
                check_custom_crl(wcc.ID, wcc.Name, wcc.KeyId, wcc.UrlCRL)
            self.ui.label_8.setText('Готово')
            self.ui.pushButton_5.setEnabled(True)
            # self.textBrowser.setText(open('main.log', 'rb').read().decode())
        except Exception:
            print('Error: check_all_crl()')
            logs('Error: check_all_crl()', 'errors', '1')

    def add_watch_current_crl(self, registration_number, keyid, stamp, serial_number, url_crl):
        try:
            count = WatchingCRL.select().where(WatchingCRL.Stamp.contains(stamp)
                                               | WatchingCRL.SerialNumber.contains(serial_number)).count()
            if count < 1:
                select_uc = UC.select().where(UC.Registration_Number == registration_number)
                for row in select_uc:
                    add_to_watching_crl = WatchingCRL(Name=row.Name,
                                                      INN=row.INN,
                                                      OGRN=row.OGRN,
                                                      KeyId=keyid,
                                                      Stamp=stamp,
                                                      SerialNumber=serial_number,
                                                      UrlCRL=url_crl,
                                                      status='Unknown',
                                                      download_status='Unknown',
                                                      download_count='0',
                                                      last_download='1970-01-01 00:00:00',
                                                      last_update='1970-01-01 00:00:00',
                                                      next_update='1970-01-01 00:00:00'
                                                      )
                    add_to_watching_crl.save()
                    self.ui.label_24.setText('Проводится проверка')
                    if check_crl(add_to_watching_crl.ID, row.Name, keyid, url_crl) == 'down_error':
                        print('Warning: add_watch_current_crl()::crl_added_error:down_error:' + keyid)
                        logs('Warning: add_watch_current_crl()::crl_added_error:down_error:' + keyid, 'warn', '4')
                        self.ui.label_24.setText('Ошибка добавления, невозможно скачать файл, проверьте источник')
                    else:
                        print('Info: add_watch_current_crl()::crl_added:' + keyid)
                        logs('Info: add_watch_current_crl()::crl_added:' + keyid, 'info', '7')
                        self.ui.label_24.setText('CRL ' + keyid + ' добавлен в список отлеживания')
            else:
                print('Info: add_watch_current_crl()::crl_exist:' + keyid)
                logs('Info: add_watch_current_crl()::crl_exist:' + keyid, 'info', '7')
                self.ui.label_24.setText('CRL ' + keyid + ' уже находится в списке отслеживания')
        except Exception:
            print('Error: add_watch_current_crl()')
            logs('Error: add_watch_current_crl()', 'errors', '1')

    def add_watch_custom_crl(self, url_crl):
        try:
            count = WatchingCustomCRL.select().where(WatchingCustomCRL.UrlCRL.contains(url_crl)).count()
            if count < 1:
                add_to_watching_crl = WatchingCustomCRL(Name='Unknown',
                                                        INN='0',
                                                        OGRN='0',
                                                        KeyId='Unknown',
                                                        Stamp='Unknown',
                                                        SerialNumber='Unknown',
                                                        UrlCRL=url_crl)
                add_to_watching_crl.save()
                self.counter_added_custom = self.counter_added_custom + 1
                print('Info: add_watch_custom_crl()::crl_added:' + url_crl)
                logs('Info: add_watch_custom_crl()::crl_added:' + url_crl, 'info', '7')
            else:
                print('Info: add_watch_custom_crl()::crl_exist:' + url_crl)
                logs('Info: add_watch_custom_crl()::crl_exist:' + url_crl, 'info', '7')
                self.counter_added_exist = self.counter_added_exist + 1
            self.on_changed_find_watching_crl('')
        except Exception:
            print('Error: add_watch_custom_crl()')
            logs('Error: add_watch_custom_crl()', 'errors', '1')

    def move_watching_to_passed(self, id_var, from_var):
        try:
            if from_var == 'current':
                from_bd = WatchingCRL.select().where(WatchingCRL.ID == id_var)
                for row in from_bd:
                    to_bd = WatchingDeletedCRL(Name=row.Name,
                                               INN=row.INN,
                                               OGRN=row.OGRN,
                                               KeyId=row.KeyId,
                                               Stamp=row.Stamp,
                                               SerialNumber=row.SerialNumber,
                                               UrlCRL=row.UrlCRL,
                                               status=row.status,
                                               download_status=row.download_status,
                                               download_count=row.download_count,
                                               last_download=row.last_download,
                                               last_update=row.last_update,
                                               next_update=row.next_update,
                                               moved_from='current')
                    to_bd.save()
                WatchingCRL.delete_by_id(id_var)
                self.sub_tab_watching_crl()
                self.sub_tab_watching_disabled_crl()
                print('Info: move_watching_to_passed()::moving_success_current:')
                logs('Info: move_watching_to_passed()::moving_success_current:', 'info', '7')
            elif from_var == 'custom':
                from_bd = WatchingCustomCRL.select().where(WatchingCustomCRL.ID == id_var)
                for row in from_bd:
                    to_bd = WatchingDeletedCRL(Name=row.Name,
                                               INN=row.INN,
                                               OGRN=row.OGRN,
                                               KeyId=row.KeyId,
                                               Stamp=row.Stamp,
                                               SerialNumber=row.SerialNumber,
                                               UrlCRL=row.UrlCRL,
                                               status=row.status,
                                               download_status=row.download_status,
                                               download_count=row.download_count,
                                               last_download=row.last_download,
                                               last_update=row.last_update,
                                               next_update=row.next_update,
                                               moved_from='custom')
                    to_bd.save()
                WatchingCustomCRL.delete_by_id(id_var)
                self.sub_tab_watching_custom_crl()
                self.sub_tab_watching_disabled_crl()
                print('Info: move_watching_to_passed()::moving_success_custom:')
                logs('Info: move_watching_to_passed()::moving_success_custom:', 'info', '7')
            else:
                print('Error: move_watching_to_passed()::Error_Moving')
                logs('Error: move_watching_to_passed()::Error_Moving', 'errors', '2')
        except Exception:
            print('Error: move_watching_to_passed()')
            logs('Error: move_watching_to_passed()', 'errors', '1')

    def move_passed_to_watching(self, id_var):
        try:
            from_bd = WatchingDeletedCRL.select().where(WatchingDeletedCRL.ID == id_var)
            for row in from_bd:
                if row.moved_from == 'current':
                    to_current = WatchingCRL(Name=row.Name,
                                             INN=row.INN,
                                             OGRN=row.OGRN,
                                             KeyId=row.KeyId,
                                             Stamp=row.Stamp,
                                             SerialNumber=row.SerialNumber,
                                             UrlCRL=row.UrlCRL,
                                             status=row.status,
                                             download_status=row.download_status,
                                             download_count=row.download_count,
                                             last_download=row.last_download,
                                             last_update=row.last_update,
                                             next_update=row.next_update)
                    to_current.save()
                    WatchingDeletedCRL.delete_by_id(id_var)
                    self.sub_tab_watching_disabled_crl()
                    self.sub_tab_watching_crl()
                    print('Info: move_passed_to_watching()::moving_success_current:')
                    logs('Info: move_passed_to_watching()::moving_success_current:', 'info', '7')
                elif row.moved_from == 'custom':
                    to_custom = WatchingCustomCRL(Name=row.Name,
                                                  INN=row.INN,
                                                  OGRN=row.OGRN,
                                                  KeyId=row.KeyId,
                                                  Stamp=row.Stamp,
                                                  SerialNumber=row.SerialNumber,
                                                  UrlCRL=row.UrlCRL,
                                                  status=row.status,
                                                  download_status=row.download_status,
                                                  download_count=row.download_count,
                                                  last_download=row.last_download,
                                                  last_update=row.last_update,
                                                  next_update=row.next_update)
                    to_custom.save()
                    WatchingDeletedCRL.delete_by_id(id_var)
                    self.sub_tab_watching_disabled_crl()
                    self.sub_tab_watching_custom_crl()
                    print('Info: move_passed_to_watching()::moving_success_custom:')
                    logs('Info: move_passed_to_watching()::moving_success_custom:', 'info', '7')
                else:
                    print('Error: move_passed_to_watching()::error_moving')
                    logs('Error: move_passed_to_watching()::error_moving', 'errors', '2')
        except Exception:
            print('Error: move_passed_to_watching()')
            logs('Error: move_passed_to_watching()', 'errors', '1')

    # def delete_watching(self, id):
    #     WatchingCRL.delete_by_id(id)
    #     self.on_changed_find_watching_crl('')
    #     print(id + ' id is deleted')

    def download_xml(self):
        try:
            self.ui.label_7.setText('Скачиваем список.')
            self.ui.label_7.adjustSize()
            self.ui.pushButton.setEnabled(False)
            self.ui.pushButton_2.setEnabled(False)
            self._download = Downloader('https://e-trust.gosuslugi.ru/CA/DownloadTSL?schemaVersion=0', 'tsl.xml')
            # Устанавливаем максимальный размер данных
            self._download.pre_progress.connect(lambda x: self.ui.progressBar.setMaximum(x))
            # Промежуточный/скачанный размер
            self._download.progress.connect(lambda y: self.ui.progressBar.setValue(y))
            # говорим что всё скачано
            self._download.downloading.connect(lambda z: self.ui.label_7.setText(z))
            self._download.done.connect(lambda z: self.ui.label_7.setText(z))
            self._download.done.connect(lambda hint1: self.ui.pushButton.setEnabled(True))
            self._download.done.connect(lambda hint2: self.ui.pushButton_2.setEnabled(True))
            # self._download.done.connect(lambda hint3: self.on_changed_find_uc(''))
            # self._download.done.connect(lambda hint4: self.on_changed_find_cert(''))
            # self._download.done.connect(lambda hint5: self.on_changed_find_crl(''))
            self._download.start()
        except Exception:
            print('Error: download_xml()')
            logs('Error: download_xml()', 'errors', '1')

    def download_all_crls(self):
        try:
            self.ui.pushButton_4.setEnabled(False)
            QCoreApplication.processEvents()
            query_1 = WatchingCRL.select()
            query_2 = WatchingCustomCRL.select()
            counter_watching_crl_all = WatchingCRL.select().count()
            watching_custom_crl_all = WatchingCustomCRL.select().count()
            counter_watching_crl = 0
            counter_watching_custom_crl = 0
            self.ui.label_8.setText('Загрузка началась')
            for wc in query_1:
                QCoreApplication.processEvents()
                counter_watching_crl = counter_watching_crl + 1
                file_url = wc.UrlCRL
                file_name = wc.KeyId + '.crl'
                # file_name = wc.UrlCRL.split('/')[-1]
                # file_name = wcc.KeyId
                folder = config['Folders']['crls']
                self.ui.label_8.setText(
                    str(counter_watching_crl) + ' из ' + str(counter_watching_crl_all) + ' Загружаем: ' + str(
                        wc.Name) + ' ' + str(wc.KeyId))
                download_file(file_url, file_name, folder, 'current', wc.ID)
                # Downloader(str(wc.UrlCRL), str(wc.SerialNumber)+'.crl')
            print('WatchingCRL downloaded ' + str(counter_watching_crl))
            logs('Info: WatchingCRL downloaded ' + str(counter_watching_crl), 'info', '5')
            for wcc in query_2:
                QCoreApplication.processEvents()
                counter_watching_custom_crl = counter_watching_custom_crl + 1
                file_url = wcc.UrlCRL
                file_name = wcc.KeyId + '.crl'
                # file_name = wcc.UrlCRL.split('/')[-1]
                # file_name = wcc.KeyId
                folder = config['Folders']['crls']
                self.ui.label_8.setText(
                    str(counter_watching_custom_crl) + ' из ' + str(watching_custom_crl_all) + ' Загружаем: ' + str(
                        wcc.Name) + ' ' + str(wcc.KeyId))
                download_file(file_url, file_name, folder, 'custome', wcc.ID)
                # Downloader(str(wcc.UrlCRL), str(wcc.SerialNumber)+'.crl'
            self.ui.label_8.setText('Загрузка закончена')
            print('WatchingCustomCRL downloaded ' + str(counter_watching_custom_crl))
            logs('Info: WatchingCustomCRL downloaded ' + str(counter_watching_custom_crl), 'info', '5')
            print('All download done, w=' + str(counter_watching_crl) + ', c=' + str(counter_watching_custom_crl))
            logs('Info: All download done, w=' + str(counter_watching_crl) + ', c=' + str(counter_watching_custom_crl), 'info', '5')
            self.ui.pushButton_4.setEnabled(True)
        except Exception:
            print('Error: download_all_crls()')
            logs('Error: download_all_crls()', 'errors', '1')

    def import_crl_list(self, file_name='crl_list.txt'):
        try:
            path = os.path.realpath(file_name)
            if os.path.exists(path):
                crl_list = open(file_name, 'r')
                crl_lists = crl_list.readlines()
                for crl_url in crl_lists:
                    QCoreApplication.processEvents()
                    crl_url = crl_url.replace("\n", "")
                    QCoreApplication.processEvents()
                    print(crl_url)
                    count = CRL.select().where(CRL.UrlCRL.contains(crl_url)).count()
                    data = CRL.select().where(CRL.UrlCRL.contains(crl_url))
                    if count > 0:
                        for row in data:
                            print(row.Registration_Number)
                            self.add_watch_current_crl(row.Registration_Number, row.KeyId, row.Stamp, row.SerialNumber,
                                                       row.UrlCRL)
                    else:
                        print('add to custom')
                        self.add_watch_custom_crl(crl_url)
                    # self.on_changed_find_watching_crl('')
                print(self.counter_added, self.counter_added_custom, self.counter_added_exist)
            else:
                print('Not found crl_list.txt')
                logs('Info: Not found crl_list.txt', 'info', '5')
        except Exception:
            print('Error: import_crl_list()')
            logs('Error: import_crl_list()', 'errors', '1')

    def export_crl(self):
        self.ui.label_7.setText('Генерируем файл')
        export_all_watching_crl()
        self.ui.label_7.setText('Файл сгенерирован')

    def export_crl_to_uc(self):
        self.ui.pushButton_3.setEnabled(False)
        self.ui.label_8.setText('Обрабатываем CRL для загрузки в УЦ')
        check_for_import_in_uc()
        self.ui.label_8.setText('Все CRL обработаны')
        self.ui.pushButton_3.setEnabled(True)

    def stop_thread(self):
        self.worker.stop()
        self.thread.quit()
        self.thread.wait()


class UcWindow(QWidget):
    def __init__(self, reg_number):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon('assists/favicon.ico'))
        self.init(reg_number)

    def init(self, reg_number):
        try:
            registration_number = 'Unknown'
            inn = 'Unknown'
            ogrn = 'Unknown'
            full_name = 'Unknown'
            email = 'Unknown'
            name = 'Unknown'
            url = 'Unknown'
            address_code = 'Unknown'
            address_name = 'Unknown'
            address_index = 'Unknown'
            address_address = 'Unknown'
            address_street = 'Unknown'
            address_town = 'Unknown'
            query = UC.select().where(UC.Registration_Number == reg_number)
            for row in query:
                registration_number = 'Регистрационный номер: ' + str(row.Registration_Number)
                inn = 'ИНН: ' + str(row.INN)
                ogrn = 'ОГРН: ' + str(row.OGRN)
                full_name = 'Полное название организации: ' + str(row.Full_Name)
                email = 'Электронная почта: ' + str(row.Email)
                name = 'Название организации: ' + str(row.Name)
                url = 'Интернет адрес: ' + str(row.URL)
                address_code = 'Код региона: ' + str(row.AddresCode)
                address_name = 'Регион: ' + str(row.AddresName)
                address_index = 'Почтовый индекс: ' + str(row.AddresIndex)
                address_address = 'Код страны: ' + str(row.AddresAddres)
                address_street = 'Улица: ' + str(row.AddresStreet)
                address_town = 'Город : ' + str(row.AddresTown)

            self.setWindowTitle(name)
            self.setWindowIcon(QIcon('assists/favicon.ico'))

            self.ui.label_7.setText(registration_number)
            self.ui.label_6.setText(inn)
            self.ui.label_5.setText(ogrn)
            self.ui.label_4.setText(full_name)
            self.ui.label_3.setText(email)
            self.ui.label_2.setText(url)
            self.ui.label.setText(name)

            self.ui.label_13.setText(address_code)
            self.ui.label_12.setText(address_name)
            self.ui.label_11.setText(address_index)
            self.ui.label_10.setText(address_address)
            self.ui.label_8.setText(address_street)
            self.ui.label_9.setText(address_town)

            query = CRL.select().where(CRL.Registration_Number == reg_number)
            query_count = CRL.select().where(CRL.Registration_Number == reg_number).count()
            self.ui.tableWidget.setRowCount(query_count)
            count = 0
            try:
                for row in query:
                    self.ui.tableWidget.setItem(count, 0, QTableWidgetItem(str(row.Registration_Number)))
                    self.ui.tableWidget.setItem(count, 1, QTableWidgetItem(str(row.KeyId)))
                    self.ui.tableWidget.setItem(count, 2, QTableWidgetItem(str(row.Stamp)))
                    self.ui.tableWidget.setItem(count, 3, QTableWidgetItem(str(row.SerialNumber)))
                    self.ui.tableWidget.setItem(count, 4, QTableWidgetItem(str()))
                    self.ui.tableWidget.setItem(count, 5, QTableWidgetItem(str(row.UrlCRL)))
                    count = count + 1
                self.ui.tableWidget.setColumnWidth(0, 50)
                self.ui.tableWidget.setColumnWidth(1, 150)
                self.ui.tableWidget.setColumnWidth(2, 150)
                self.ui.tableWidget.setColumnWidth(3, 150)
                self.ui.tableWidget.setColumnWidth(4, 150)
                self.ui.tableWidget.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
            except Exception:
                print('Error: UcWindow()::init()::query_to_row')
                logs('Error: UcWindow()::init()::query_to_row', 'errors', '2')
        except Exception:
            print('Error: UcWindow()::init()')
            logs('Error: UcWindow()::init()', 'errors', '1')


class AddCRLWindow(QWidget):
    def __init__(self):
        try:
            super().__init__()
            self.ui_add = Ui_Form_add()
            self.ui_add.setupUi(self)
            self.setWindowIcon(QIcon('assists/favicon.ico'))
            self.ui_add.lineEdit.textChanged[str].connect(self.init)
            self.ui_add.pushButton.pressed.connect(self.set_fields)
            self.ui_add.pushButton_2.pressed.connect(self.query_fields)
            self.init()
        except Exception:
            print('Error: AddCRLWindow()::__init__()', 'errors')
            logs('Error: AddCRLWindow()::__init__()', 'errors', '1')

    def init(self, text=''):
        try:
            self.ui_add.comboBox.clear()
            query = CERT.select().where(CERT.Registration_Number.contains(text)
                                        | CERT.Name.contains(text)
                                        | CERT.KeyId.contains(text)
                                        | CERT.Stamp.contains(text)
                                        | CERT.SerialNumber.contains(text)).limit(config['Listing']['cert'])
            for row in query:
                self.ui_add.comboBox.addItem(row.Name, row.KeyId)
        except Exception:
            print('Error: AddCRLWindow()::init()', 'errors')
            logs('Error: AddCRLWindow()::init()', 'errors', '2')

    def set_fields(self):
        try:
            id_cert = self.ui_add.comboBox.currentData()
            query = CERT.select().where(CERT.KeyId == id_cert)
            registration_number = 0
            for row_cert in query:
                registration_number = row_cert.Registration_Number
                self.ui_add.lineEdit_6.setText(str(row_cert.Name))
                self.ui_add.lineEdit_3.setText(str(row_cert.KeyId))
                self.ui_add.lineEdit_8.setText(str(row_cert.Stamp))
                self.ui_add.lineEdit_4.setText(str(row_cert.SerialNumber))
                self.ui_add.lineEdit_5.setText(str(row_cert.Registration_Number))
            query_2 = UC.select().where(UC.Registration_Number == registration_number)
            for row_uc in query_2:
                self.ui_add.lineEdit_7.setText(str(row_uc.INN))
                self.ui_add.lineEdit_2.setText(str(row_uc.OGRN))
        except Exception:
            print('Error: AddCRLWindow()::set_fields()', 'errors')
            logs('Error: AddCRLWindow()::set_fields()', 'errors', '2')

    def query_fields(self):
        try:
            if CERT.select().where(CERT.KeyId == self.ui_add.lineEdit_3.text()
                                   or CERT.Stamp == self.ui_add.lineEdit_8.text()
                                   or CERT.SerialNumber == self.ui_add.lineEdit_4.text()).count() > 0:
                if WatchingCRL.select().where(WatchingCRL.KeyId == self.ui_add.lineEdit_3.text()
                                              or WatchingCRL.Stamp == self.ui_add.lineEdit_8.text()
                                              or WatchingCRL.SerialNumber == self.ui_add.lineEdit_4.text()
                                              or WatchingCRL.UrlCRL == self.ui_add.lineEdit_9.text()).count() > 0:
                    print('Info: CRL is exists in WatchingCRL')
                    logs('Info: CRL is exists in WatchingCRL', 'info', '7')
                    self.ui_add.label_10.setText('CRL уже есть в основном списке отслеживания')
                elif WatchingCustomCRL.select().where(WatchingCustomCRL.KeyId == self.ui_add.lineEdit_3.text()
                                                      or WatchingCustomCRL.Stamp == self.ui_add.lineEdit_8.text()
                                                      or WatchingCustomCRL.SerialNumber == self.ui_add.lineEdit_4.text()
                                                      or WatchingCustomCRL.UrlCRL == self.ui_add.lineEdit_9.text())\
                        .count() > 0:
                    print('Info: CRL is exist in WatchingCustomCRL')
                    logs('Info: CRL is exist in WatchingCustomCRL', 'info', '7')
                    self.ui_add.label_10.setText('CRL уже есть в своем списке отслеживания')
                elif WatchingDeletedCRL.select().where(WatchingDeletedCRL.KeyId == self.ui_add.lineEdit_3.text()
                                                       or WatchingDeletedCRL.Stamp == self.ui_add.lineEdit_8.text()
                                                       or WatchingDeletedCRL.SerialNumber == self.ui_add.lineEdit_4.text()
                                                       or WatchingDeletedCRL.UrlCRL == self.ui_add.lineEdit_9.text())\
                        .count() > 0:
                    print('Info: CRL is exist in WatchingDeletedCRL')
                    logs('Info: CRL is exist in WatchingDeletedCRL', 'info', '7')
                    self.ui_add.label_10.setText('CRL уже есть в удаленных, или удалите полностью или верните обратно')
                else:
                    name = self.ui_add.lineEdit_6.text()
                    inn = self.ui_add.lineEdit_7.text()
                    ogrn = self.ui_add.lineEdit_2.text()
                    key_id = self.ui_add.lineEdit_3.text()
                    stamp = self.ui_add.lineEdit_8.text()
                    serial_number = self.ui_add.lineEdit_4.text()
                    url_crl = self.ui_add.lineEdit_9.text()
                    if name == '' or inn == '' or ogrn == '' or key_id == '' or stamp == '' or serial_number == '' or url_crl == '':
                        print('Заполните все поля')
                        print('Info: The fields should not be empty')
                        logs('Info: The fields should not be empty', 'info', '6')
                        self.ui_add.label_10.setText('Заполните все поля')
                    else:
                        query = WatchingCustomCRL(Name=name,
                                                  INN=inn,
                                                  OGRN=ogrn,
                                                  KeyId=key_id,
                                                  Stamp=stamp,
                                                  SerialNumber=serial_number,
                                                  UrlCRL=url_crl,
                                                  status='Unknown',
                                                  download_status='Unknown',
                                                  download_count='0',
                                                  last_download='1970-01-01 00:00:00',
                                                  last_update='1970-01-01 00:00:00',
                                                  next_update='1970-01-01 00:00:00')
                        query.save()
                        # download_file(url_crl,
                        #               key_id + '.crl',
                        #               config['Folders']['crls'],
                        #               'custome',
                        #               str(query.ID),
                        #               set_dd='Yes')
                        check_custom_crl(query.ID, name, key_id)
                        print('Info: CRL added in WatchingCustomCRL')
                        logs('Info: CRL added in WatchingCustomCRL', 'info', '7')
                        self.ui_add.label_10.setText('CRL "' + name + '" добавлен в список отслеживания')
            else:
                print('Warning: Cert not found')
                logs('Warning: Cert not found', 'warn', '4')
                self.ui_add.label_10.setText('Не найден квалифицированный сертификат УЦ')
        except Exception:
            print('Error: AddCRLWindow()::query_fields()')
            logs('Error: AddCRLWindow()::query_fields()', 'errors', '2')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle(config['Style']['window'])
    main_app = MainWindow()
    main_app.show()
    sys.exit(app.exec_())
