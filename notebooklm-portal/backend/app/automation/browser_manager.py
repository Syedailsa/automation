from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from pathlib import Path
from datetime import datetime
import asyncio
import json
import random
import logging
from typing import Optional, Dict, List, Any
from functools import wraps

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('notebooklm')
