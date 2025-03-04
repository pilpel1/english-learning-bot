"""
מודול להגדרת לוגר מרכזי לפרויקט
"""

import os
import logging
from logging.handlers import RotatingFileHandler
import sys
from datetime import datetime

def setup_logger(name: str = "english_learning_bot", log_level: str = None) -> logging.Logger:
    """
    הגדרת לוגר מרכזי לפרויקט
    
    Args:
        name: שם הלוגר
        log_level: רמת הלוגים (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        logging.Logger: אובייקט הלוגר המוגדר
    """
    # קבלת רמת הלוג מהסביבה או שימוש בברירת מחדל
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO")
    
    # המרת מחרוזת רמת הלוג למספר
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # יצירת הלוגר
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    
    # ניקוי הנדלרים הקיימים אם יש
    if logger.handlers:
        logger.handlers.clear()
    
    # הגדרת פורמט ללוגים
    log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # יצירת תיקיית לוגים אם לא קיימת
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # הגדרת קובץ לוג עם רוטציה
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f"{name}_{today}.log")
    file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5)
    file_handler.setFormatter(log_format)
    file_handler.setLevel(numeric_level)
    logger.addHandler(file_handler)
    
    # הגדרת לוג לקונסול
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    console_handler.setLevel(numeric_level)
    logger.addHandler(console_handler)
    
    # השבתת לוגים של HTTPX אם מוגדר בסביבה
    if os.getenv("DISABLE_HTTPX_LOGS", "False").lower() in ("true", "1", "yes"):
        logging.getLogger("httpx").setLevel(logging.WARNING)
    
    return logger 