import argparse
import asyncio
from asyncio import TaskGroup
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
import base64
import urllib.parse
import zlib
from colorama import init, Fore, Style
from aiohttp import ClientSession, TCPConnector
from websockets.client import connect as ws_connect
from typing import List, Tuple, Optional, Dict, TypeAlias, Set
import pickle
import os
from concurrent.futures import ThreadPoolExecutor
import statistics
import string
import jsonlines
from string import Template

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
⠀⠀⠀⠀⠀⠀⡟⣿⡏⠀⠀⢀⣠⣾⣿⣿⡿⠛⣡⠀⣿⣿⣿⣿⣿⣿⣿⣦⣀⠈⠙⠻⠿⠿⠶⠾⠟⠃⠀⢀⠔⠁⠀⠀⠀⠀⣾⣆⠀⠀⠀⠀⣰⢀⣾⣿⣿⣧⡇⠀
⠀⠀⠀⠀⠀⢸⠁⣿⠃⢀⣴⣿⣿⣿⠟⢻⢁⣾⣿⢀⣿⣿⣿⣿⣿⣿⣿⣷⣦⣤⣄⣀⡀⠠⠤⠐⠊⠀⠀⠀⠀⠀⠀⠀⢀⡰⣿⣿⡆⠀⠀⣿⣧⣿⣿⣿⣿⣿⡇⠀
⠀⠀⠀⠀⠀⣌⠀⠘⢠⣿⣿⣿⡟⠁⢀⣏⣾⣿⡇⣸⣿⣿⣿⣿⣿⣟⠛⠛⠛⠛⠛⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡰⠋⢱⣿⣿⣧⠀⢠⣿⣿⣿⣿⣿⣿⡏⢱⠀
⠀⠀⠀⠀⠀⠈⠑⠢⢿⣿⣿⡟⠀⢀⣾⣿⣿⡟⢠⣿⣿⣿⣿⡿⠿⢿⣿⣷⣶⣤⣤⣤⣄⣤⣤⣤⠤⠖⠂⠀⠀⣠⠊⠀⠀⠀⢿⣿⣿⠀⢸⣿⣿⣿⣿⣿⣿⠇⢸⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠙⠣⢤⣈⣿⣿⠏⣰⣿⣿⣿⣷⣭⣍⣑⠂⠀⠀⠈⠉⠉⠉⠉⠉⠀⠀⠀⠀⠀⢀⡼⠁⠀⠀⠀⠀⠈⢿⢿⠀⣼⣿⣿⣿⣿⣿⣧⢴⣾⡄
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠑⠚⠿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠶⠶�6f⠆⠀⠀⠀⠀⠀⠀⢠⠞⠀⠀⠀⠀⠀⠀⠀⠘⡄⠀⣿⣿⣿⣿⣿⣡⣖⣿⡇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠓⠒⠒⠒⠒⠒⠒⠒⠒⠒⠒⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠱⠤⠛⠛⠿⠯⠭⠭⠙⠒⠚⠁
Made by Dark Legend
"""

FuzzResultType: TypeAlias = Tuple[str, Optional[int], int, str, Dict[str, str], float, str, float, Dict[str, int]]

class FuzzResult:
    def __init__(
        self,
        url: str,
        status: Optional[int],
        length: int,
        content: str,
        headers: Dict[str, str],
        response_time: float,
        protocol: str,
        score: int,
        metadata: Dict[str, int],
    ) -> None:
        self.url = url
        self.status = status
        self.length = length
        self.content = content
        self.headers = headers
        self.response_time = response_time
        self.hash = hashlib.md5(content.encode('utf-8', errors='ignore')).hexdigest() if content else ""
        self.protocol = protocol
        self.score = score
        self.metadata = metadata

class FuzzDB:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(":memory:" if db_path == ":memory:" else db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS results
                             (url TEXT, status INTEGER, length INTEGER, lines INTEGER, title TEXT, headers TEXT, hash TEXT, response_time REAL, protocol TEXT, score INTEGER, metadata TEXT)"""
        )
        self.conn.commit()

    def save_result(self, result: FuzzResult, title: str):
        self.cursor.execute(
            """INSERT INTO results (url, status, length, lines, title, headers, hash, response_time, protocol, score, metadata)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                result.url,
                result.status,
                result.length,
                len(result.content.splitlines()),
                title,
                json.dumps(result.headers),
                result.hash,
                result.response_time,
                result.protocol,
                result.score,
                json.dumps(result.metadata),
            ),
        )
        self.conn.commit()

    def get_summary(self) -> Dict[str, any]:
        self.cursor.execute("SELECT status, COUNT(*) FROM results GROUP BY status")
        status_counts = dict(self.cursor.fetchall())
        self.cursor.execute(
            "SELECT AVG(response_time), MIN(response_time), MAX(response_time), AVG(score) FROM results WHERE status IS NOT NULL"
        )
        times = self.cursor.fetchone()
        self.cursor.execute("SELECT DISTINCT protocol FROM results")
        protocols = [row[0] for row in self.cursor.fetchall()]
        return {
            "status_counts": status_counts,
            "avg_response_time": times[0] or 0,
            "min_response_time": times[1] or 0,
            "max_response_time": times[2] or 0,
            "avg_score": times[3] or 0,
            "protocols": protocols,
        }

class FuzzOrchestrator:
    def __init__(self):
        self.queue = queue.Queue()
        self.results: List[FuzzResult] = []
        self.hits = 0
        self.total = 0
        self.payload_scores: Dict[str, int] = {}
        self.payload_freq: Dict[str, int] = {}
        self.baseline: Optional[FuzzResult] = None
        self.scheduler = {"pause": False, "max_hits": None, "schedule_time": None}
        self.seen_hashes: Set[str] = set()

    def add_task(self, url: str, payload: str, stage: str = "default"):
        self.queue.put((url, payload, stage))
        self.total += 1

    def get_progress(self) -> float:
        return (self.total - self.queue.qsize()) / self.total * 100 if self.total else 0

    def update_score(self, payload: str, result: FuzzResult):
        score = 0
        if result.status in {200, 201, 301, 302}:
            score += 50
        if result.length > 1000:
            score += 20
        if result.response_time < 0.1:
            score += 10
        if result.metadata.get("endpoints", 0) > 0:
            score += 30
        self.payload_scores[payload] = score
        self.payload_freq[payload] = self.payload_freq.get(payload, 0) + 1

    def is_redundant(self, result_hash: str, threshold: float = 1.0) -> bool:
        if threshold >= 1.0:
            return result_hash in self.seen_hashes
        return False  # Placeholder for similarity-based deduplication

async def fetch(
    session: ClientSession, url: str, method: str, headers: Dict[str, str], data: Optional[str], timeout: int, retries: int
) -> FuzzResultType:
    start_time = time.time()
    for attempt in range(retries):
        try:
            async with session.request(method, url, headers=headers, data=data, timeout=timeout) as response:
                if response.status in {404, 429} and response.content_length < 100000:
                    return response.status, response.content_length or 0, "", dict(response.headers), time.time() - start_time
                content = await response.text(errors="ignore")
                return response.status, len(content), content, dict(response.headers), time.time() - start_time
        except Exception as e:
            if attempt == retries - 1:
                return None, 0, str(e), {}, time.time() - start_time
            await asyncio.sleep(0.5 * (2**attempt))
    return None, 0, "Max retries exceeded", {}, time.time() - start_time

async def ws_fuzz(url: str, payload: str, timeout: int) -> FuzzResultType:
    start_time = time.time()
    try:
        async with ws_connect(url, max_size=None, open_timeout=timeout) as ws:
            await ws.send(payload)
            content = await ws.recv()
            return 101, len(content), content, {}, time.time() - start_time
    except Exception as e:
        return None, 0, str(e), {}, time.time() - start_time

async def custom_protocol_fuzz(url: str, payload: str, protocol: str, timeout: int) -> FuzzResultType:
    start_time = time.time()
    return None, 0, f"Unsupported protocol: {protocol}", {}, time.time() - start_time

def load_extension(ext_file: str, func_name: str) -> Optional[callable]:
    try:
        spec = importlib.util.spec_from_file_location("ext", ext_file)
        if spec is None:
            raise ImportError(f"Cannot load spec for {ext_file}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore
        return getattr(module, func_name, None)
    except Exception as e:
        print(f"{Fore.RED}Error loading extension {ext_file}: {e}{Style.RESET_ALL}")
        return None

def generate_payloads(
    wordlists: List[str], numeric: str | None, chars: str | None, mutations: List[str], ext_file: str | None, orchestrator: FuzzOrchestrator
) -> List[str]:
    seen_payloads: Set[str] = set()
    payloads = []

    def load_wordlist(wl: str):
        try:
            with open(wl, "rb") as f:
                compressed = zlib.compress(f.read())
                decompressed = zlib.decompress(compressed).decode(errors="ignore")
                for line in decompressed.splitlines():
                    word = line.strip()
                    if word and word not in seen_payloads:
                        seen_payloads.add(word)
                        payloads.append(word)
                        orchestrator.add_task("", word)
        except FileNotFoundError:
            print(f"{Fore.RED}Error: Wordlist '{wl}' not found{Style.RESET_ALL}")
            sys.exit(1)

    with ThreadPoolExecutor() as executor:
        executor.map(load_wordlist, wordlists)

    if numeric:
        start, end = map(int, numeric.split("-"))
        for i in range(start, end + 1):
            payload = str(i)
            if payload not in seen_payloads:
                seen_payloads.add(payload)
                payloads.append(payload)
                orchestrator.add_task("", payload)

    if chars:
        length = int(chars.split(":")[1]) if ":" in chars else 3
        chars_set = chars.split(":")[0] if ":" in chars else chars
        for p in itertools.product(chars_set, repeat=length):
            payload = "".join(p)
            if payload not in seen_payloads:
                seen_payloads.add(payload)
                payloads.append(payload)
                orchestrator.add_task("", payload)

    mutated = []
    for p in payloads:
        mutated.append(p)
        if "upper" in mutations:
            mutated.append(p.upper())
        if "lower" in mutations:
            mutated.append(p.lower())
        if "urlencode" in mutations:
            mutated.append(urllib.parse.quote(p))
        if "doubleencode" in mutations:
            mutated.append(urllib.parse.quote(urllib.parse.quote(p)))
        if "base64" in mutations:
            mutated.append(base64.b64encode(p.encode()).decode())
        if "hex" in mutations:
            mutated.append(p.encode().hex())
        if "unicode" in mutations:
            mutated.append("".join(f"\\u{ord(c):04x}" for c in p))

    if ext_file:
        custom_gen = load_extension(ext_file, "generate_payloads")
        if custom_gen:
            custom_payloads = custom_gen(payloads)
            for p in custom_payloads:
                if p not in seen_payloads:
                    seen_payloads.add(p)
                    mutated.append(p)
                    orchestrator.add_task("", p)

    # Feedback-driven mutation
    if orchestrator.payload_freq:
        top_payloads = sorted(orchestrator.payload_freq.items(), key=lambda x: x[1], reverse=True)[:20]
        for payload, _ in top_payloads:
            for suffix in ["_test", "_admin", "_api", "_v2", "_backup", ".bak"]:
                new_payload = payload + suffix
                if new_payload not in seen_payloads:
                    seen_payloads.add(new_payload)
                    mutated.append(new_payload)
                    orchestrator.add_task("", new_payload)

    return mutated

def save_session(state: Dict, filename: str):
    with open(filename, "wb") as f:
        pickle.dump(state, f)

def load_session(filename: str) -> Dict | None:
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

def detect_tech(headers: Dict[str, str], content: str) -> str:
    tech = []
    signatures = {
        "Server": ["nginx", "apache", "iis", "tomcat", "cloudflare"],
        "X-Powered-By": ["php", "asp.net", "node.js", "express", "laravel"],
        "X-Generator": ["drupal", "joomla"],
        "Content": [
            "wordpress",
            "drupal",
            "joomla",
            "magento",
            "react",
            "vue",
            "angular",
            "shopify",
            "wix",
        ],
    }
    for header, values in signatures.items():
        if header == "Content":
            for value in values:
                if value in content.lower():
                    tech.append(value.capitalize())
        elif header in headers:
            for value in values:
                if value.lower() in headers[header].lower():
                    tech.append(value.capitalize())
    return ", ".join(sorted(set(tech))) if tech else "Unknown"

def detect_vuln(content: str) -> List[str]:
    vulns = []
    patterns = {
        "XSS": re.compile(r"<\s*script.*>.*alert\(|on\w+\s*=", re.IGNORECASE),
        "SQLi": re.compile(r"SQL syntax.*MySQL|ORA-\d+|SQLSTATE", re.IGNORECASE),
        "LFI": re.compile(r"etc/passwd|win.ini", re.IGNORECASE),
        "Open Redirect": re.compile(r"location\.href\s*=|window\.location\s*=", re.IGNORECASE),
        "RCE": re.compile(r"eval\(|exec\(|system\(", re.IGNORECASE),
    }
    for vuln, pattern in patterns.items():
        if pattern.search(content):
            vulns.append(vuln)
    return sorted(set(vulns))

def content_analysis(content: str) -> Dict[str, int]:
    endpoints = len(re.findall(r'href=["\'](.*?)["\']', content, re.IGNORECASE))
    forms = len(re.findall(r"<form", content, re.IGNORECASE))
    params = len(re.findall(r"[?&]([^=]+)=", content))
    return {"endpoints": endpoints, "forms": forms, "params": params}

def diff_response(baseline: FuzzResult | None, result: FuzzResult) -> str:
    if not baseline or not result.content:
        return ""
    diff = []
    if baseline.status != result.status:
        diff.append(f"Status: {baseline.status} -> {result.status}")
    if abs(baseline.length - result.length) > 100:
        diff.append(f"Length: {baseline.length} -> {result.length}")
    if baseline.headers.get("Content-Type") != result.headers.get("Content-Type"):
        diff.append(f"Content-Type: {baseline.headers.get('Content-Type')} -> {result.headers.get('Content-Type')}")
    if baseline.metadata != result.metadata:
        diff.append(f"Metadata: {json.dumps(baseline.metadata)} -> {json.dumps(result.metadata)}")
    return "; ".join(diff) if diff else "No significant differences"

def store_url(url: str, filename: str):
    with open(filename, "a") as f:
        f.write(url + "\n")

def export_graph(results: List[FuzzResult], filename: str):
    graph = {"nodes": [], "edges": []}
    url_ids = {}
    for i, result in enumerate(results):
        if result.status in {200, 201, 301, 302}:
            url_ids[result.url] = i
            graph["nodes"].append({"id": i, "label": result.url, "status": result.status})
    for i, result in enumerate(results):
        if result.status in {301, 302} and "Location" in result.headers:
            redirect_url = result.headers["Location"]
            if redirect_url in url_ids:
                graph["edges"].append({"from": i, "to": url_ids[redirect_url]})
    with open(filename + ".graph.json", "w") as f:
        json.dump(graph, f, indent=2)

async def fuzz_url(
    base_url: str,
    payload: str,
    stage: str,
    session: ClientSession,
    args,
    template: Template,
    semaphore: asyncio.Semaphore,
    db: FuzzDB,
    orchestrator: FuzzOrchestrator,
    proxies: List[str],
    header_cache: List[Dict[str, str]],
) -> FuzzResult:
    async with semaphore:
        headers = random.choice(header_cache) if args.waf_evasion else (json.loads(args.headers) if args.headers else {})
        if args.random_ua or args.waf_evasion:
            headers["User-Agent"] = random.choice(
                [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 15_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
                ]
            )
        if args.header_fuzz or args.waf_evasion:
            headers[random.choice(["X-Forwarded-For", "X-Real-IP", "X-Client-ID"])] = "".join(random.choices(string.ascii_letters, k=15))
        if args.session_track and args.session_cookies:
            headers["Cookie"] = args.session_cookies.get(payload, "")

        target_url = template.substitute({f"FUZZ{i or ''}": payload if i == j else args.placeholders[i] for i in range(len(args.placeholders)) for j in range(len(args.placeholders)) if i == j})
        if args.inject_point == "query":
            parsed = urllib.parse.urlparse(target_url)
            query = urllib.parse.urlencode({**urllib.parse.parse_qs(parsed.query), "q": payload})
            target_url = urllib.parse.urlunparse(parsed._replace(query=query))
        elif args.inject_point == "header":
            headers["X-Fuzz"] = payload
        elif args.inject_point == "body" and args.method == "POST":
            args.data = args.data.replace("FUZZ", payload) if args.data else f"fuzz={payload}"

        protocol = "http" if target_url.startswith(("http://", "https://")) else "ws" if target_url.startswith(("ws://", "wss://")) else args.custom_protocol or "unknown"
        timeout = args.timeout
        if args.adaptive_timeout and orchestrator.results:
            timeout = max(1, min(30, statistics.median([r.response_time for r in orchestrator.results[-100:]])))

        if proxies:
            headers["Proxy"] = random.choice(proxies)

        if protocol == "ws":
            status, content_length, content, headers, response_time = await ws_fuzz(target_url, payload, timeout)
        elif protocol == "unknown":
            status, content_length, content, headers, response_time = await custom_protocol_fuzz(target_url, payload, args.custom_protocol or "unknown", timeout)
        else:
            status, content_length, content, headers, response_time = await fetch(session, target_url, args.method, headers, args.data, timeout, args.retries)

        metadata = content_analysis(content) if args.content_analysis else {}
        score = orchestrator.payload_scores.get(payload, 0)
        result = FuzzResult(target_url, status, content_length, content, headers, response_time, protocol, score, metadata)

        if status is None:
            print(f"{Fore.RED}URL: {target_url} | Error: {content}{Style.RESET_ALL}")
            logging.error(f"URL: {target_url} | Error: {content}")
            return result

        if args.hide_redundant and await orchestrator.is_redundant(result.hash, args.dedupe_threshold):
            return result
        orchestrator.seen_hashes.add(result.hash)

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
        if args.match_regex and not any(p.search(content) for p in args.regex_cache):
            return result
        if args.header_filter and not any(h in headers for h in args.header_filter):
            return result
        if args.content_type and args.content_type.lower() not in headers.get("Content-Type", "").lower():
            return result

        title = ""
        if args.extract_title:
            match = args.title_regex.search(content)
            title = match.group(1).strip() if match else ""

        if args.ext_response:
            custom_process = load_extension(args.ext_response, "process_response")
            if custom_process:
                content = custom_process(content)

        tech = detect_tech(headers, content)
        vulns = detect_vuln(content) if args.vuln_scan else []
        diff = diff_response(orchestrator.baseline, result) if args.diff else ""

        db.save_result(result, title)
        orchestrator.results.append(result)
        orchestrator.hits += 1
        orchestrator.update_score(payload, result)

        if args.session_track and "Set-Cookie" in headers:
            args.session_cookies[payload] = headers["Set-Cookie"]

        if args.store_urls:
            store_url(target_url, args.store_urls)

        output = (
            f"{Fore.GREEN}URL: {target_url} | Status: {status} | Length: {content_length} | "
            f"Lines: {len(content.splitlines())} | Time: {response_time:.3f}s | Tech: {tech} | "
            f"Title: {title} | Vulns: {', '.join(vulns) or 'None'} | Diff: {diff} | "
            f"Metadata: {json.dumps(metadata)}{Style.RESET_ALL}"
        )
        print(output)

        log_entry = {
            "url": target_url,
            "status": status,
            "length": content_length,
            "lines": len(content.splitlines()),
            "response_time": response_time,
            "title": title,
            "headers": headers,
            "tech": tech,
            "protocol": protocol,
            "vulns": vulns,
            "diff": diff,
            "score": score,
            "metadata": metadata,
        }
        if args.output_format == "json":
            logging.info(json.dumps(log_entry))
        elif args.output_format == "csv":
            csv_writer.writerow(
                [
                    target_url,
                    status,
                    content_length,
                    len(content.splitlines()),
                    response_time,
                    title,
                    tech,
                    protocol,
                    ",".join(vulns),
                    diff,
                    score,
                    json.dumps(metadata),
                ]
            )
        elif args.output_format == "jsonl":
            with jsonlines.open(args.output, "a") as writer:
                writer.write(log_entry)
        else:
            logging.info(output)

        if args.stream:
            async with session.post(args.stream, json=log_entry) as _:
                pass

        return result

async def display_dashboard(orchestrator: FuzzOrchestrator, db: FuzzDB, stop_event: asyncio.Event, args):
    stages = {"default": orchestrator.get_progress()}
    while not stop_event.is_set():
        progress = orchestrator.get_progress()
        summary = db.get_summary()
        hits = orchestrator.hits
        print(
            f"\r{Fore.CYAN}┌── DarkFuzz Dashboard ── Made by Dark Legend ──\n"
            f"│ Progress: {progress:.1f}% | Hits: {hits} | Concurrency: {args.concurrency}\n"
            f"│ Statuses: {summary['status_counts']} | Avg Time: {summary['avg_response_time']:.3f}s\n"
            f"│ Protocols: {', '.join(summary['protocols'])} | Avg Score: {summary['avg_score']:.1f}\n"
            f"└── Press 'p' to pause, 'f' to adjust filters, 'q' to quit{Style.RESET_ALL}",
            end="",
        )
        await asyncio.sleep(1)

async def main(args):
    global csv_writer
    args.time_start = time.time()
    print(ASCII_ART)

    logging.basicConfig(filename=args.output, level=logging.INFO, format="%(asctime)s - %(message)s")
    if args.output_format == "csv":
        csv_file = open(args.output, "w", newline="")
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(
            [
                "URL",
                "Status",
                "Length",
                "Lines",
                "ResponseTime",
                "Title",
                "Tech",
                "Protocol",
                "Vulns",
                "Diff",
                "Score",
                "Metadata",
            ]
        )

    db = FuzzDB(":memory:" if not args.db else args.db)
    orchestrator = FuzzOrchestrator()

    session_file = args.session or f"{args.output}.session"
    session_state = load_session(session_file) if args.resume else None
    start_index = session_state.get("completed", 0) if session_state else 0

    payloads = generate_payloads(args.wordlist, args.numeric, args.chars, args.mutations, args.ext_payload, orchestrator)
    total_payloads = len(payloads)
    if start_index >= total_payloads:
        print(f"{Fore.YELLOW}Session already completed{Style.RESET_ALL}")
        return

    template = Template(args.url)
    if args.diff:
        async with ClientSession() as session:
            status, length, content, headers, response_time = await fetch(
                session, args.url.replace(args.placeholders[0], ""), args.method, {}, args.data, args.timeout, args.retries
            )
            orchestrator.baseline = FuzzResult(
                args.url, status, length, content, headers, response_time, "http", 0, {}
            )

    proxies = []
    if args.proxy_list:
        try:
            with open(args.proxy_list, "r") as f:
                proxies = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"{Fore.RED}Error: Proxy list '{args.proxy_list}' not found{Style.RESET_ALL}")
            sys.exit(1)

    header_cache = []
    if args.waf_evasion:
        for _ in range(100):
            headers = {
                random.choice(["Accept", "Accept-Language", "Referer"]): random.choice(
                    [
                        "text/html,application/xhtml+xml",
                        "en-US,en;q=0.9",
                        "https://example.com",
                    ]
                )
            }
            header_cache.append(headers)

    proxy = args.proxy if args.proxy else None
    concurrency = args.concurrency
    response_times = []
    error_rate = 0
    args.session_cookies = {}

    args.regex_cache = [re.compile(args.match_regex)] if args.match_regex else []
    args.title_regex = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)

    rate_profile = {
        "slow": lambda t: min(1.0 / (50 + t * 10), 0.02),
        "burst": lambda t: 1.0 / (10 if t % 10 < 2 else 100),
        "steady": lambda t: 1.0 / args.rate_limit if args.rate_limit else 0,
    }.get(args.rate_profile, lambda t: 1.0 / args.rate_limit if args.rate_limit else 0)

    connector = TCPConnector(
        limit=0,
        force_close=False,
        enable_cleanup_closed=True,
        keepalive_timeout=30,
        ssl=False if args.no_ssl_verify else None,
    )
    async with ClientSession(connector=connector, trust_env=True) as session:
        if proxy:
            session._default_headers["Proxy"] = proxy

        semaphore = asyncio.Semaphore(concurrency)
        stop_event = asyncio.Event()

        if args.dashboard:
            asyncio.create_task(display_dashboard(orchestrator, db, stop_event, args))

        if orchestrator.payload_scores:
            payloads.sort(key=lambda p: orchestrator.payload_scores.get(p, 0), reverse=True)

        async with TaskGroup() as tg:
            completed = start_index
            cluster_hashes: Dict[str, List[str]] = {}
            batch_size = 50
            time_elapsed = 0

            for i in range(start_index, total_payloads, batch_size):
                if orchestrator.scheduler["pause"] or (
                    orchestrator.scheduler["max_hits"] and orchestrator.hits >= orchestrator.scheduler["max_hits"]
                ):
                    await asyncio.sleep(60)
                    continue

                batch = payloads[i : i + batch_size]
                tasks = []
                for payload in batch:
                    tasks.append(
                        tg.create_task(
                            fuzz_url(
                                args.url,
                                payload,
                                "default",
                                session,
                                args,
                                template,
                                semaphore,
                                db,
                                orchestrator,
                                proxies,
                                header_cache,
                            )
                        )
                    )

                results = [await task for task in tasks]
                completed += len(batch)

                for result in results:
                    if isinstance(result, Exception):
                        error_rate = (error_rate * completed + 1) / (completed + 1)
                    elif result.status and args.cluster:
                        cluster_hashes.setdefault(result.hash, []).append(result.url)
                    if result.response_time:
                        response_times.append(result.response_time)
                    if args.auto_rate_limit and result.status == 429:
                        concurrency = max(10, concurrency // 2)
                        args.delay = min(10000, args.delay * 2) if args.delay else 1000

                if response_times and args.adaptive:
                    avg_time = statistics.mean(response_times[-100:])
                    if avg_time > 0.5 or error_rate > 0.1:
                        concurrency = max(10, concurrency - 20)
                    elif avg_time < 0.1 and error_rate < 0.05:
                        concurrency = min(2000, concurrency + 20)
                    semaphore = asyncio.Semaphore(concurrency)

                if args.session:
                    save_session({"completed": completed, "payloads": payloads}, session_file)

                time_elapsed += 1
                sleep_time = rate_profile(time_elapsed)
                if args.jitter:
                    sleep_time = random.uniform(max(0, args.delay / 1000.0), args.jitter / 1000.0)
                elif args.delay:
                    sleep_time = max(sleep_time, args.delay / 1000.0)
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

                # Dynamic payload prioritization
                if orchestrator.payload_freq and len(orchestrator.results) % 1000 == 0:
                    payloads[completed:] = sorted(
                        payloads[completed:], key=lambda p: orchestrator.payload_scores.get(p, 0), reverse=True
                    )

        stop_event.set()
        print(f"\n{Fore.CYAN}Progress: {completed}/{total_payloads} (100.0%){Style.RESET_ALL}")

        if args.cluster:
            print(f"\n{Fore.MAGENTA}Response Clusters:{Style.RESET_ALL}")
            for h, urls in cluster_hashes.items():
                if len(urls) > 1:
                    print(
                        f"{Fore.MAGENTA}Hash {h}: {len(urls)} URLs: {', '.join(urls[:5])}{'...' if len(urls) > 5 else ''}{Style.RESET_ALL}"
                    )

        if args.replay:
            print(f"\n{Fore.YELLOW}Replaying {orchestrator.hits} hits...{Style.RESET_ALL}")
            async with TaskGroup() as tg:
                for result in orchestrator.results:
                    if result.status in args.show_codes:
                        tg.create_task(
                            fuzz_url(
                                args.url,
                                result.url.split("/")[-1],
                                "replay",
                                session,
                                args,
                                template,
                                semaphore,
                                db,
                                orchestrator,
                                proxies,
                                header_cache,
                            )
                        )

        if args.export_graph:
            export_graph(orchestrator.results, args.output)

        summary = db.get_summary()
        print(f"\n{Fore.YELLOW}Summary:{Style.RESET_ALL}")
        print(f"Status Counts: {summary['status_counts']}")
        print(f"Avg Response Time: {summary['avg_response_time']:.3f}s")
        print(f"Min Response Time: {summary['min_response_time']:.3f}s")
        print(f"Max Response Time: {summary['max_response_time']:.3f}s")
        print(f"Avg Payload Score: {summary['avg_score']:.1f}")
        print(f"Protocols: {', '.join(summary['protocols'])}")

        generate_report(args, summary, args.output)

        if args.output_format == "csv":
            csv_file.close()

def generate_report(args, summary: Dict[str, any], output_file: str):
    report = (
        f"DarkFuzz Report - Made by Dark Legend\n"
        f"Target: {args.url}\n"
        f"Start Time: {time.ctime(args.time_start)}\n"
        f"Duration: {time.time() - args.time_start:.2f} seconds\n"
        f"Status Counts: {summary['status_counts']}\n"
        f"Avg Response Time: {summary['avg_response_time']:.3f}s\n"
        f"Min Response Time: {summary['min_response_time']:.3f}s\n"
        f"Max Response Time: {summary['max_response_time']:.3f}s\n"
        f"Avg Payload Score: {summary['avg_score']:.1f}\n"
        f"Protocols: {', '.join(summary['protocols'])}\n"
        f"Recommendations: Use --content-analysis for deeper endpoint discovery, enable --auto-rate-limit for WAF-heavy targets."
    )
    with open(output_file + ".report.txt", "w") as f:
        f.write(report)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DarkFuzz: The Ultimate Fuzzing Tool - Made by Dark Legend")
    parser.add_argument("-u", "--url", required=True, help="Base URL with FUZZ placeholder(s) (e.g., http://example.com/FUZZ)")
    parser.add_argument("-w", "--wordlist", action="append", default=[], help="Path to wordlist file(s)")
    parser.add_argument("-o", "--output", default="fuzz_results.txt", help="Output file for results")
    parser.add_argument("-c", "--concurrency", type=int, default=300, help="Initial number of concurrent requests")
    parser.add_argument("--show", help="Comma-separated status codes to show (e.g., 200,301)")
    parser.add_argument("--hide", help="Comma-separated status codes to hide (e.g., 404,403)")
    parser.add_argument("--min-size", type=int, help="Minimum response size")
    parser.add_argument("--max-size", type=int, help="Maximum response size")
    parser.add_argument("--min-lines", type=int, help="Minimum number of response lines")
    parser.add_argument("--max-lines", type=int, help="Maximum number of response lines")
    parser.add_argument("--match-regex", help="Regex to match in response content")
    parser.add_argument("--header-filter", action="append", default=[], help="Response headers to filter")
    parser.add_argument("--content-type", help="Filter by Content-Type")
    parser.add_argument("--method", default="GET", help="HTTP method (e.g., GET, POST)")
    parser.add_argument("--headers", help="JSON string of custom headers")
    parser.add_argument("--data", help="POST data (e.g., 'key=value')")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds")
    parser.add_argument("--retries", type=int, default=3, help="Number of retries for failed requests")
    parser.add_argument("--delay", type=int, default=0, help="Delay between requests in milliseconds")
    parser.add_argument("--jitter", type=int, help="Max jitter for delay in milliseconds")
    parser.add_argument("--rate-limit", type=int, help="Max requests per second")
    parser.add_argument("--proxy", help="Proxy URL (e.g., http://localhost:8080)")
    parser.add_argument("--proxy-list", help="File with list of proxy URLs")
    parser.add_argument("--numeric", help="Numeric range (e.g., 1-1000)")
    parser.add_argument("--chars", help="Character set for combinations (e.g., abc:3)")
    parser.add_argument(
        "--mutations",
        action="append",
        default=[],
        help="Payload mutations (upper, lower, urlencode, doubleencode, base64, hex, unicode)",
    )
    parser.add_argument(
        "--output-format", choices=["txt", "json", "csv", "jsonl"], default="txt", help="Output format"
    )
    parser.add_argument("--extract-title", action="store_true", help="Extract page title")
    parser.add_argument("--session", help="Session file to save/resume")
    parser.add_argument("--resume", action="store_true", help="Resume from session")
    parser.add_argument("--db", help="SQLite database file (default: in-memory)")
    parser.add_argument("--random-ua", action="store_true", help="Use random User-Agent")
    parser.add_argument("--custom-protocol", help="Custom protocol (e.g., ftp, smtp)")
    parser.add_argument("--cluster", action="store_true", help="Cluster similar responses")
    parser.add_argument("--ext-payload", help="Python script for custom payload generation")
    parser.add_argument("--ext-response", help="Python script for custom response processing")
    parser.add_argument("--header-fuzz", action="store_true", help="Fuzz headers with random values")
    parser.add_argument("--adaptive", action="store_true", help="Adapt concurrency and rate")
    parser.add_argument("--adaptive-timeout", action="store_true", help="Adapt timeout based on response times")
    parser.add_argument("--dashboard", action="store_true", help="Show real-time ASCII dashboard")
    parser.add_argument("--diff", action="store_true", help="Diff responses against baseline")
    parser.add_argument("--vuln-scan", action="store_true", help="Scan for vulnerabilities")
    parser.add_argument("--store-urls", help="File to store successful URLs")
    parser.add_argument("--waf-evasion", action="store_true", help="Enable WAF evasion techniques")
    parser.add_argument("--stream", help="HTTP endpoint to stream results")
    parser.add_argument("--rate-profile", choices=["slow", "burst", "steady"], help="Request rate profile")
    parser.add_argument("--replay", action="store_true", help="Replay successful requests")
    parser.add_argument("--interactive", action="store_true", help="Enable interactive dashboard controls")
    parser.add_argument("--content-analysis", action="store_true", help="Analyze response content for endpoints")
    parser.add_argument("--auto-rate-limit", action="store_true", help="Auto-adjust rate on 429 responses")
    parser.add_argument(
        "--inject-point", choices=["path", "query", "header", "body"], default="path", help="Payload injection point"
    )
    parser.add_argument("--session-track", action="store_true", help="Track session cookies")
    parser.add_argument("--hide-redundant", action="store_true", help="Hide redundant responses")
    parser.add_argument("--dedupe-threshold", type=float, default=1.0, help="Deduplication similarity threshold (0.0-1.0)")
    parser.add_argument("--export-graph", action="store_true", help="Export endpoint relationship graph")
    parser.add_argument("--no-ssl-verify", action="store_true", help="Disable SSL verification")

    args = parser.parse_args()

    if not args.wordlist and not args.numeric and not args.chars and not args.ext_payload:
        print(f"{Fore.RED}Error: At least one of --wordlist, --numeric, --chars, or --ext-payload is required{Style.RESET_ALL}")
        sys.exit(1)

    args.placeholders = re.findall(r"FUZZ\d*", args.url)
    if not args.placeholders:
        print(f"{Fore.RED}Error: URL must contain at least one FUZZ placeholder{Style.RESET_ALL}")
        sys.exit(1)

    args.show_codes = [int(c) for c in args.show.split(",")] if args.show else []
    args.hide_codes = [int(c) for c in args.hide.split(",")] if args.hide else []

    if args.match_regex:
        try:
            re.compile(args.match_regex)
        except re.error:
            print(f"{Fore.RED}Error: Invalid regex pattern '{args.match_regex}'{Style.RESET_ALL}")
            sys.exit(1)

    try:
        asyncio.run(main(args))
        print(f"\n{Fore.GREEN}Fuzzing completed in {time.time() - args.time_start:.2f} seconds{Style.RESET_ALL}")
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Fuzzing interrupted by user{Style.RESET_ALL}")
        sys.exit(0)
