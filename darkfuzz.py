import argparse
import asyncio
import aiohttp
import sys
import time
import logging
import re
import json
import csv
import itertools
import random
import sqlite3
import threading
import queue
import hashlib
import importlib.util
from urllib.parse import urljoin, urlencode
from colorama import init, Fore, Style
from aiohttp import ClientSession, TCPConnector
from websockets.client import connect as ws_connect
from typing import List, Tuple, Optional, Dict
import pickle
import os
from concurrent.futures import ThreadPoolExecutor
import statistics
import string

# Initialize colorama for colored output
init()

ASCII_ART = """
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⢆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⢠⠳⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⢸⢸⢳⡙⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠖⡏⠀⠀⠀⢸⠀⠐⡜⣆⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⢞⠵⢸⠀⠀⢀⡇⣸⠀⡆⠘⣌⢆⠀⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⢞⡵⠁⡆⡇⠀⡠⠋⡼⠀⠀⡇⠀⠘⠈⢧⡏⡄⢠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢠⠀⠀⠀⠀⢀⡴⣡⡯⠀⢀⡇⣧⠞⠁⡰⠃⠀⠀⣧⠀⠀⠀⢸⡇⢃⢸⢇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢸⡀⠀⠀⢠⢎⡜⡿⠁⠀⢸⣇⡵⠁⠀⠀⠀⠀⠀⣿⠀⠀⠀⠈⠀⢸⣸⠘⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢸⢣⠀⡴⣡⣿⠁⠃⠀⢀⣾⡿⠁⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠈⡏⠀⢇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢸⠈⢇⡇⣿⡏⠀⠀⠀⣼⣿⠃⠀⠀⠀⠀⢀⠇⡰⣿⠀⠀⠀⠀⠀⡇⠁⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠸⠐⠄⠀⠏⡇⠀⠀⣧⣿⡇⡀⡜⢰⠀⠀⡘⡐⠁⠏⡆⠀⠀⡄⢠⡇⡄⠀⠈⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⠦⢠⣧⠀⣆⣿⣿⢁⣷⣇⡇⠀⣴⣯⠀⠀⠀⡇⠀⣸⡇⣾⡿⠁⠀⡀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢀⠀⠀⠀⢀⢀⢠⠀⠸⣿⣆⢹⣿⣿⣾⣿⣿⣠⢾⠛⠁⠀⠀⠀⡇⡠⡟⣿⣿⠃⠀⠀⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠘⡶⣄⠀⢸⠸⣼⣧⡀⣿⣿⣾⣿⣿⣿⣿⣿⡇⠘⠀⡀⠀⠀⢠⠟⠀⠃⢹⣥⠃⠀⢠⢏⣜⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠙⡌⠳⢄⣣⠹⣿⣿⣿⣿⣿⣿⣿⡿⢿⣿⡇⠀⠀⢀⣄⣴⡢⠀⠀⠀⡿⣯⠀⠐⠁⠘⣻⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠘⢎⢶⣍⣀⠈⢿⣿⣿⣿⣿⣿⣿⣦⠑⣤⡀⠀⣰⠟⡿⠁⠀⠀⠈⠀⠁⠀⠀⡀⡰⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠈⢣⣻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡀⠘⣷⣾⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⡵⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠑⣝⠻⠿⣿⣿⣿⣿⣿⣿⣿⣇⠀⣿⣿⣿⣇⣀⣤⠆⠀⠁⠀⠉⠀⠸⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⠉⡇⢸⣿⣿⣿⣿⣿⣿⣿⣼⣿⣿⣿⣿⣿⠋⠀⠀⠀⠀⠀⠐⢤⡀⠙⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠱⢬⣙⠛⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣏⡄⠀⠀⠀⠀⠀⠀⠈⠻⠆⠀⠈⠑⠒⣿⣦⣆⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠑⠲⣼⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⣀⣀⣀⠀⠀⣀⣀⣠⣴⣾⣾⣿⣿⣿⣿⣿⣷⣦⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣘⣿⣷⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⠤⣀⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢘⣿⠟⣡⣶⣶⣤⡄⠙⣿⣿⣿⣿⣿⣿⣟⡛⠿⠿⣿⣿⣿⣿⣿⣿⣿⡿⠿⢿⣿⣿⣿⡿⠟⣩⣿⣿⣿⣿⡀⠀⠀⢏⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣶⣿⢋⣼⢿⠿⢛⣿⠷⢶⣶⠂⠿⣿⣿⣿⣿⣿⣷⣶⣤⣀⡀⠉⠉⠀⠀⣀⣀⡀⠀⠀⠀⠠⢾⣿⣿⣿⣿⣿⠇⠀⠀⣘⠢⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢀⣽⠁⠘⠁⠀⠀⠁⠀⠠⠟⠛⣿⣄⡩⢉⣿⣿⣿⣿⣿⡿⠋⠀⡠⣶⣶⣶⡶⣶⣶⣾⠿⠶⠀⠀⠻⣿⣿⣿⣿⠀⠀⠠⣿⣷⡘⢆⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⡸⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⣿⣿⣤⡈⣿⣿⣿⣿⡟⠁⣠⣾⡇⠀⣿⣿⣆⠀⠀⠀⠀⣀⣠⣆⠀⢹⣿⣿⡿⠀⠀⢠⣿⣿⣿⡘⡆⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⣿⠁⣺⣿⣿⣿⡿⠀⢰⡟⠛⠇⠘⠿⣿⣇⠀⠀⣀⠀⢀⣽⣿⡀⠀⣿⣿⠃⠀⠀⢸⣿⣿⣿⣧⢸⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢣⠀⠀⠀⠀⠀⠀⠀⢀⣴⠟⣿⠃⢰⠨⣿⣿⣿⠃⠀⣿⡇⢀⠀⢰⠀⠛⠛⠀⠀⠛⠀⠈⠉⠹⠇⠀⣿⡏⠀⠀⠀⣹⣿⣿⣿⣿⠘⢦⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠈⡆⠀⠀⠀⠀⣠⡶⠋⠁⡼⠃⠀⣾⠃⣿⣿⣿⠀⠀⡟⢀⡜⠀⢋⣠⣶⠀⠀⠒⠒⠀⠀⣶⡾⠀⢠⠏⠀⠀⣠⣾⣿⣿⣿⣿⢿⠁⠀⣣⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣼⣷⢤⣤⢶⠟⠁⠀⠀⠀⠀⢀⣼⡏⣸⣿⣿⣿⣇⠀⢻⣿⡇⠀⣿⣿⣿⠀⠀⣶⣶⠀⢸⣿⠃⠀⠎⠀⠀⠀⠿⣿⣿⣿⣿⡿⠀⠀⢀⣯⢇⠀⠀
⠀⠀⠀⠀⠀⠀⢰⣿⣿⠘⠁⠁⠀⠀⢀⣠⣴⣾⣿⠟⣰⣿⣿⣿⣿⣿⡄⠀⠻⠀⣠⣿⣿⣿⠀⠀⠉⠉⠀⠘⠁⢀⠌⠀⠀⠀⢀⠀⠀⠈⠉⠀⠀⠀⢀⣾⣿⡿⠀⠀
⠀⠀⠀⠀⠀⠀⡟⣿⡏⠀⠀⢀⣠⣾⣿⣿⡿⠛⣡⠀⣿⣿⣿⣿⣿⣿⣿✨⢀⠈⠙⠻⠿⠿⠶⠾⠟⠃⠀⢀⠔⠁⠀⠀⠀⠀⣾⣆⠀⠀⠀⠀⣰⢀⣾⣿⣿⣧⡇⠀
⠀⠀⠀⠀⠀⢸⠁⣿⠃⢀⣴⣿⣿⣿⠟⢻⢁⣾⣿⢀⣿⣿⣿⣿⣿⣿⣿⣷⣦⣤⣄⣀⡀⠠⠤⠐⠊⠀⠀⠀⠀⠀⠀⠀⢀⡰⣿⣿⡆⠀⠀⣿⣧⣿⣿⣿⣿⣿⡇⠀
⠀⠀⠀⠀⠀⣌⠀⠘⢠⣿⣿⣿⡟⠁⢀⣏⣾⣿⡇⣸⣿⣿⣿⣿⣿⣟⠛⠛⠛⠛⠛⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡰⠋⢱⣿⣿⣧⠀⢠⣿⣿⣿⣿⣿⣿⡏⢱⠀
⠀⠀⠀⠀⠀⠈⠑⠢⢿⣿⣿⡟⠀⢀⣾⣿⣿⡟⢠⣿⣿⣿⣿⡿⠿⢿⣿⣷⣶⣤⣤⣤⣄⣤⣤⣤⠤⠖⠂⠀⠀⣠⠊⠀⠀⠀⢿⣿⣿⠀⢸⣿⣿⣿⣿⣿⣿⠇⢸⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠙⠣⢤⣈⣿⣿⠏⣰⣿⣿⣿⣷⣭⣍⣑⠂⠀⠀⠈⠉⠉⠉⠉⠉⠀⠀⠀⠀⠀⢀⡼⠁⠀⠀⠀⠀⠈⢿⢿⠀⣼⣿⣿⣿⣿⣿⣧⢴⣾⡄
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠑⠚⠿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠶⠶⠶⠖⠒⠂⠀⠀⠀⠀⢠⠞⠀⠀⠀⠀⠀⠀⠀⠘⡄⠀⣿⣿⣿⣿⣿⣿⣡⣿⣿⡇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠓⠒⠒⠒⠒⠒⠒⠒⠒⠊⠉⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠱⠤⠛⠛⠿⠯⠭⠭⠙⠒⠚⠁
Made by Dark Legend
"""

class FuzzResult:
    def __init__(self, url: str, status: Optional[int], length: int, content: str, headers: dict, response_time: float, protocol: str):
        self.url = url
        self.status = status
        self.length = length
        self.content = content
        self.headers = headers
        self.response_time = response_time
        self.hash = hashlib.md5(content.encode('utf-8')).hexdigest() if content else ""
        self.protocol = protocol

class FuzzDB:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(":memory:" if db_path == ":memory:" else db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS results
                             (url TEXT, status INTEGER, length INTEGER, lines INTEGER, title TEXT, headers TEXT, hash TEXT, response_time REAL, protocol TEXT)''')
        self.conn.commit()

    def save_result(self, result: FuzzResult, title: str):
        self.cursor.execute('''INSERT INTO results (url, status, length, lines, title, headers, hash, response_time, protocol)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (result.url, result.status, result.length, len(result.content.splitlines()),
                            title, json.dumps(result.headers), result.hash, result.response_time, result.protocol))
        self.conn.commit()

    def get_summary(self) -> Dict:
        self.cursor.execute("SELECT status, COUNT(*) FROM results GROUP BY status")
        status_counts = dict(self.cursor.fetchall())
        self.cursor.execute("SELECT AVG(response_time), MIN(response_time), MAX(response_time) FROM results WHERE status IS NOT NULL")
        times = self.cursor.fetchone()
        self.cursor.execute("SELECT DISTINCT protocol FROM results")
        protocols = [row[0] for row in self.cursor.fetchall()]
        return {
            "status_counts": status_counts,
            "avg_response_time": times[0] or 0,
            "min_response_time": times[1] or 0,
            "max_response_time": times[2] or 0,
            "protocols": protocols
        }

class FuzzOrchestrator:
    def __init__(self):
        self.queue = queue.Queue()
        self.results = []
        self.hits = 0
        self.total = 0

    def add_task(self, url: str, payload: str):
        self.queue.put((url, payload))
        self.total += 1

    def get_progress(self) -> float:
        return (self.total - self.queue.qsize()) / self.total * 100 if self.total else 0

async def fetch(session: ClientSession, url: str, method: str, headers: dict, data: Optional[str], timeout: int, retries: int) -> Tuple[Optional[int], int, str, dict, float]:
    start_time = time.time()
    for attempt in range(retries):
        try:
            async with session.request(method, url, headers=headers, data=data, timeout=timeout) as response:
                content = await response.text()
                return response.status, len(content), content, dict(response.headers), time.time() - start_time
        except Exception as e:
            if attempt == retries - 1:
                return None, 0, str(e), {}, time.time() - start_time
            await asyncio.sleep(0.5 * (2 ** attempt))
    return None, 0, "Max retries exceeded", {}, time.time() - start_time

async def ws_fuzz(url: str, payload: str, timeout: int) -> Tuple[Optional[int], int, str, dict, float]:
    start_time = time.time()
    try:
        async with ws_connect(url, max_size=None, open_timeout=timeout) as ws:
            await ws.send(payload)
            content = await ws.recv()
            return 101, len(content), content, {}, time.time() - start_time
    except Exception as e:
        return None, 0, str(e), {}, time.time() - start_time

async def custom_protocol_fuzz(url: str, payload: str, protocol: str, timeout: int) -> Tuple[Optional[int], int, str, dict, float]:
    # Placeholder for custom protocols (e.g., FTP, SMTP)
    start_time = time.time()
    return None, 0, f"Unsupported protocol: {protocol}", {}, time.time() - start_time

def load_extension(ext_file: str, func_name: str):
    try:
        spec = importlib.util.spec_from_file_location("ext", ext_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, func_name, None)
    except Exception as e:
        print(f"{Fore.RED}Error loading extension {ext_file}: {e}{Style.RESET_ALL}")
        return None

def generate_payloads(wordlists: List[str], numeric: Optional[str], chars: Optional[str], mutations: List[str], ext_file: Optional[str], orchestrator: FuzzOrchestrator) -> List[str]:
    payloads = []
    def load_wordlist(wl):
        try:
            with open(wl, 'r') as f:
                for line in f:
                    word = line.strip()
                    if word:
                        payloads.append(word)
                        orchestrator.add_task("", word)  # Track in orchestrator
        except FileNotFoundError:
            print(f"{Fore.RED}Error: Wordlist '{wl}' not found{Style.RESET_ALL}")
            sys.exit(1)
    
    # Stream wordlists in parallel
    with ThreadPoolExecutor() as executor:
        executor.map(load_wordlist, wordlists)
    
    # Generate numeric range
    if numeric:
        start, end = map(int, numeric.split('-'))
        for i in range(start, end + 1):
            payloads.append(str(i))
            orchestrator.add_task("", str(i))
    
    # Generate character combinations
    if chars:
        length = int(chars.split(':')[1]) if ':' in chars else 3
        chars = chars.split(':')[0] if ':' in chars else chars
        for p in itertools.product(chars, repeat=length):
            payload = ''.join(p)
            payloads.append(payload)
            orchestrator.add_task("", payload)
    
    # Apply mutations
    mutated = []
    for p in payloads:
        mutated.append(p)
        if 'upper' in mutations:
            mutated.append(p.upper())
        if 'lower' in mutations:
            mutated.append(p.lower())
        if 'urlencode' in mutations:
            mutated.append(urlencode({'': p})[1:])
        if 'doubleencode' in mutations:
            mutated.append(urlencode({'': urlencode({'': p})[1:]})[1:])
    
    # Custom extension
    if ext_file:
        custom_gen = load_extension(ext_file, 'generate_payloads')
        if custom_gen:
            custom_payloads = custom_gen(payloads)
            mutated.extend(custom_payloads)
            for p in custom_payloads:
                orchestrator.add_task("", p)
    
    return list(set(mutated))

def save_session(state: dict, filename: str):
    with open(filename, 'wb') as f:
        pickle.dump(state, f)

def load_session(filename: str) -> dict:
    try:
        with open(filename, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

def detect_tech(headers: dict, content: str) -> str:
    tech = []
    if 'Server' in headers:
        tech.append(headers['Server'])
    if 'X-Powered-By' in headers:
        tech.append(headers['X-Powered-By'])
    if 'wordpress' in content.lower():
        tech.append('WordPress')
    if 'drupal' in content.lower():
        tech.append('Drupal')
    return ', '.join(tech) if tech else 'Unknown'

async def fuzz_url(base_url: str, payload: str, session: ClientSession, args, semaphore: asyncio.Semaphore, db: FuzzDB, orchestrator: FuzzOrchestrator) -> FuzzResult:
    async with semaphore:
        # Randomize headers
        headers = json.loads(args.headers) if args.headers else {}
        if args.random_ua:
            headers['User-Agent'] = random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
                "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
            ])
        if args.header_fuzz:
            headers[random.choice(['X-Forwarded-For', 'X-Real-IP', 'X-Test'])] = ''.join(random.choices(string.ascii_letters, k=10))
        
        target_url = base_url
        for i, placeholder in enumerate(args.placeholders):
            target_url = target_url.replace(placeholder, payload if i == 0 else args.placeholders[i])
        
        # Select protocol
        protocol = 'http'
        if args.websocket:
            protocol = 'ws'
            status, content_length, content, headers, response_time = await ws_fuzz(target_url, payload, args.timeout)
        elif args.custom_protocol:
            protocol = args.custom_protocol
            status, content_length, content, headers, response_time = await custom_protocol_fuzz(target_url, payload, args.custom_protocol, args.timeout)
        else:
            status, content_length, content, headers, response_time = await fetch(session, target_url, args.method, headers, args.data, args.timeout, args.retries)
        
        result = FuzzResult(target_url, status, content_length, content, headers, response_time, protocol)
        
        if status is None:
            print(f"{Fore.RED}URL: {target_url} | Error: {content}{Style.RESET_ALL}")
            logging.error(f"URL: {target_url} | Error: {content}")
            return result

        # Apply filters
        if args.show_codes and status not in args.show_codes:
            return result
        if args.hide_codes and status in args.hide_codes:
            return result
        if args.min_size and content_length < args.min_size:
            return result
        if args.max_size and content_length > args.max_size:
            return result
        if args.min_lines and len(content.splitlines()) < args.min_lines:
            return result
        if args.max_lines and len(content.splitlines()) > args.max_lines:
            return result
        if args.match_regex and not re.search(args.match_regex, content):
            return result
        if args.header_filter and not any(h in headers for h in args.header_filter):
            return result
        if args.content_type and args.content_type.lower() not in headers.get('Content-Type', '').lower():
            return result
        
        # Extract title
        title = ""
        if args.extract_title:
            match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
            title = match.group(1).strip() if match else "N/A"
        
        # Custom response processing
        if args.ext_response:
            custom_process = load_extension(args.ext_response, 'process_response')
            if custom_process:
                content = custom_process(content)
        
        # Detect technology
        tech = detect_tech(headers, content)
        
        # Save to database
        db.save_result(result, title)
        orchestrator.results.append(result)
        orchestrator.hits += 1
        
        # Format output
        output = (
            f"{Fore.GREEN}URL: {target_url} | Status: {status} | Length: {content_length} | "
            f"Lines: {len(content.splitlines())} | Time: {response_time:.3f}s | Tech: {tech} | Title: {title}{Style.RESET_ALL}"
        )
        print(output)
        
        # Log to file
        log_entry = {
            'url': target_url, 'status': status, 'length': content_length,
            'lines': len(content.splitlines()), 'response_time': response_time,
            'title': title, 'headers': headers, 'tech': tech, 'protocol': protocol
        }
        if args.output_format == 'json':
            logging.info(json.dumps(log_entry))
        elif args.output_format == 'csv':
            csv_writer.writerow([target_url, status, content_length, len(content.splitlines()), response_time, title, tech, protocol])
        else:
            logging.info(output)
        
        return result

async def display_dashboard(orchestrator: FuzzOrchestrator, db: FuzzDB, stop_event: asyncio.Event):
    while not stop_event.is_set():
        progress = orchestrator.get_progress()
        summary = db.get_summary()
        hits = orchestrator.hits
        print(f"\r{Fore.CYAN}Dashboard: Progress: {progress:.1f}% | Hits: {hits} | "
              f"Statuses: {summary['status_counts']} | Avg Time: {summary['avg_response_time']:.3f}s{Style.RESET_ALL}", end='')
        await asyncio.sleep(1)

async def main(args):
    global csv_writer
    print(ASCII_ART)
    
    # Configure logging
    logging.basicConfig(filename=args.output, level=logging.INFO, format='%(asctime)s - %(message)s')
    if args.output_format == 'csv':
        csv_file = open(args.output, 'w', newline='')
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['URL', 'Status', 'Length', 'Lines', 'ResponseTime', 'Title', 'Tech', 'Protocol'])
    
    # Initialize database and orchestrator
    db = FuzzDB(":memory:" if not args.db else args.db)
    orchestrator = FuzzOrchestrator()
    
    # Load or initialize session
    session_file = args.session or f"{args.output}.session"
    session_state = load_session(session_file) if args.resume else None
    start_index = session_state.get('completed', 0) if session_state else 0
    
    # Generate payloads
    payloads = generate_payloads(args.wordlist, args.numeric, args.chars, args.mutations, args.ext_payload, orchestrator)
    total_payloads = len(payloads)
    if start_index >= total_payloads:
        print(f"{Fore.YELLOW}Session already completed{Style.RESET_ALL}")
        return
    
    # Configure proxy
    proxy = args.proxy if args.proxy else None
    
    # Adaptive concurrency
    concurrency = args.concurrency
    response_times = []
    
    # Configure connector for HTTP/2
    connector = TCPConnector(limit=0, force_close=False, enable_cleanup_closed=True)
    async with ClientSession(connector=connector, trust_env=True) as session:
        if proxy:
            session._default_headers['Proxy'] = proxy
        
        semaphore = asyncio.Semaphore(concurrency)
        tasks = []
        completed = start_index
        cluster_hashes = {}
        stop_event = asyncio.Event()
        
        # Start dashboard
        if args.dashboard:
            asyncio.create_task(display_dashboard(orchestrator, db, stop_event))
        
        for i, payload in enumerate(payloads[start_index:], start=start_index):
            tasks.append(fuzz_url(args.url, payload, session, args, semaphore, db, orchestrator))
            if len(tasks) >= concurrency:
                results = await asyncio.gather(*tasks)
                completed += len(tasks)
                
                # Cluster responses
                for result in results:
                    if result.status and args.cluster:
                        cluster_hashes.setdefault(result.hash, []).append(result.url)
                    if result.response_time:
                        response_times.append(result.response_time)
                
                # Adaptive concurrency
                if response_times and args.adaptive:
                    avg_time = statistics.mean(response_times[-100:])
                    if avg_time > 0.5:
                        concurrency = max(10, concurrency - 10)
                    elif avg_time < 0.1:
                        concurrency = min(1000, concurrency + 10)
                    semaphore = asyncio.Semaphore(concurrency)
                
                tasks = []
                if args.session:
                    save_session({'completed': completed, 'payloads': payloads}, session_file)
                if args.rate_limit:
                    await asyncio.sleep(1.0 / args.rate_limit)
                if args.jitter:
                    await asyncio.sleep(random.uniform(args.delay / 1000.0, args.jitter / 1000.0))
                elif args.delay:
                    await asyncio.sleep(args.delay / 1000.0)
        
        if tasks:
            results = await asyncio.gather(*tasks)
            completed += len(tasks)
            for result in results:
                if result.status and args.cluster:
                    cluster_hashes.setdefault(result.hash, []).append(result.url)
                if result.response_time:
                    response_times.append(result.response_time)
        
        stop_event.set()
        print(f"\n{Fore.CYAN}Progress: {completed}/{total_payloads} (100.0%){Style.RESET_ALL}")
        
        # Print clusters
        if args.cluster:
            print(f"\n{Fore.MAGENTA}Response Clusters:{Style.RESET_ALL}")
            for h, urls in cluster_hashes.items():
                if len(urls) > 1:
                    print(f"{Fore.MAGENTA}Hash {h}: {len(urls)} URLs: {', '.join(urls[:5])}{'...' if len(urls) > 5 else ''}{Style.RESET_ALL}")
        
        # Print summary
        summary = db.get_summary()
        print(f"\n{Fore.YELLOW}Summary:{Style.RESET_ALL}")
        print(f"Status Counts: {summary['status_counts']}")
        print(f"Avg Response Time: {summary['avg_response_time']:.3f}s")
        print(f"Min Response Time: {summary['min_response_time']:.3f}s")
        print(f"Max Response Time: {summary['max_response_time']:.3f}s")
        print(f"Protocols: {', '.join(summary['protocols'])}")
        
        if args.output_format == 'csv':
            csv_file.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WebFuzz: The Monster Fuzzing Tool - Made by Dark Legend")
    parser.add_argument("-u", "--url", required=True, help="Base URL with FUZZ placeholder(s) (e.g., http://example.com/FUZZ)")
    parser.add_argument("-w", "--wordlist", action='append', default=[], help="Path to wordlist file(s), can be used multiple times")
    parser.add_argument("-o", "--output", default="fuzz_results.txt", help="Output file for results")
    parser.add_argument("-c", "--concurrency", type=int, default=300, help="Initial number of concurrent requests")
    parser.add_argument("--show", help="Comma-separated status codes to show (e.g., 200,301)")
    parser.add_argument("--hide", help="Comma-separated status codes to hide (e.g., 404,403)")
    parser.add_argument("--min-size", type=int, help="Minimum response size to show")
    parser.add_argument("--max-size", type=int, help="Maximum response size to show")
    parser.add_argument("--min-lines", type=int, help="Minimum number of lines in response")
    parser.add_argument("--max-lines", type=int, help="Maximum number of lines in response")
    parser.add_argument("--match-regex", help="Regex to match in response content")
    parser.add_argument("--header-filter", action='append', default=[], help="Response headers to filter (e.g., Server:nginx)")
    parser.add_argument("--content-type", help="Filter by Content-Type (e.g., text/html)")
    parser.add_argument("--method", default="GET", help="HTTP method (e.g., GET, POST)")
    parser.add_argument("--headers", help="JSON string of custom headers (e.g., '{\"User-Agent\": \"Fuzzer\"}')")
    parser.add_argument("--data", help="POST data (e.g., 'key=value')")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds")
    parser.add_argument("--retries", type=int, default=3, help="Number of retries for failed requests")
    parser.add_argument("--delay", type=int, default=0, help="Delay between requests in milliseconds")
    parser.add_argument("--jitter", type=int, help="Max jitter for delay in milliseconds")
    parser.add_argument("--rate-limit", type=int, help="Max requests per second")
    parser.add_argument("--proxy", help="Proxy URL (e.g., http://localhost:8080)")
    parser.add_argument("--numeric", help="Numeric range (e.g., 1-100)")
    parser.add_argument("--chars", help="Character set for combinations (e.g., abc:3 for 3-char combos)")
    parser.add_argument("--mutations", action='append', default=[], help="Payload mutations (upper, lower, urlencode, doubleencode)")
    parser.add_argument("--output-format", choices=['txt', 'json', 'csv'], default='txt', help="Output format")
    parser.add_argument("--extract-title", action='store_true', help="Extract page title from responses")
    parser.add_argument("--session", help="Session file to save/resume progress")
    parser.add_argument("--resume", action='store_true', help="Resume from saved session")
    parser.add_argument("--db", help="SQLite database file for results (default: in-memory)")
    parser.add_argument("--random-ua", action='store_true', help="Use random User-Agent headers")
    parser.add_argument("--websocket", action='store_true', help="Fuzz WebSocket endpoints")
    parser.add_argument("--custom-protocol", help="Custom protocol to fuzz (e.g., ftp, smtp)")
    parser.add_argument("--cluster", action='store_true', help="Cluster similar responses by content hash")
    parser.add_argument("--ext-payload", help="Python script for custom payload generation")
    parser.add_argument("--ext-response", help="Python script for custom response processing")
    parser.add_argument("--header-fuzz", action='store_true', help="Fuzz request headers with random values")
    parser.add_argument("--adaptive", action='store_true', help="Adapt concurrency based on response times")
    parser.add_argument("--dashboard", action='store_true', help="Show real-time ASCII dashboard")
    
    args = parser.parse_args()

    if not args.wordlist and not args.numeric and not args.chars and not args.ext_payload:
        print(f"{Fore.RED}Error: At least one of --wordlist, --numeric, --chars, or --ext-payload is required{Style.RESET_ALL}")
        sys.exit(1)

    args.placeholders = re.findall(r'FUZZ\d*', args.url)
    if not args.placeholders:
        print(f"{Fore.RED}Error: URL must contain at least one FUZZ placeholder (e.g., http://example.com/FUZZ){Style.RESET_ALL}")
        sys.exit(1)

    args.show_codes = [int(c) for c in args.show.split(',')] if args.show else []
    args.hide_codes = [int(c) for c in args.hide.split(',')] if args.hide else []

    if args.match_regex:
        try:
            re.compile(args.match_regex)
        except re.error:
            print(f"{Fore.RED}Error: Invalid regex pattern '{args.match_regex}'{Style.RESET_ALL}")
            sys.exit(1)

    start_time = time.time()
    try:
        asyncio.run(main(args))
        print(f"\n{Fore.GREEN}Fuzzing completed in {time.time() - start_time:.2f} seconds{Style.RESET_ALL}")
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Fuzzing interrupted by user{Style.RESET_ALL}")
        sys.exit(0)
