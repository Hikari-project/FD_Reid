# coding: utf-8

import logging.config
import sys, os

import Algorithm.libs.config.model_cfgs as cfgs
IS_DEBUG=cfgs.IS_DEBUG

class IgnoreFaissLoaderFilter(logging.Filter):
    def filter(self, record):
        # 只允许非 faiss.loader 的日志记录

        return 'faiss.loader' not in record.name

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            'format': '[%(asctime)s: %(name)s:%(lineno)d] - %(levelname)s: %(message)s'
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": "ext://sys.stdout"
        },

        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "INFO",
            "formatter": "standard",
            "filename": os.path.join(cfgs.SAVE_LOG_PATH, 'reid_process.log'),
            'when': 'D',
            'interval': 1,
            "backupCount": 15,
            "encoding": "utf8"
        },
    },

    "loggers": {
        "faiss": {
            "level": "DEBUG",  # 仍然可以记录 DEBUG 级别，但会被过滤
            "handlers": ["console", "file"] if  IS_DEBUG else ["file"],
            "propagate": False,
        },
    },

    "root": {
        'handlers': ['console', 'file'] if  IS_DEBUG else ["file"],
        'level': "INFO",
        'propagate': False
    },

    "filters": {
        'ignore_faiss_loader': {
            '()': IgnoreFaissLoaderFilter,
        }
    }
}

# 为每个 handler 添加过滤器
for handler in LOGGING_CONFIG['handlers'].values():
    handler['filters'] = ['ignore_faiss_loader']

if not os.path.exists(cfgs.SAVE_LOG_PATH):
    os.makedirs(cfgs.SAVE_LOG_PATH)
logging.config.dictConfig(LOGGING_CONFIG)



def get_logger(name='root'):
    return logging.getLogger(name)

