import pickle
import os

BASE_DIR = "./data"


def get_thread_dir(thread_id):
    """thread_idに基づいてディレクトリパスを生成し、存在しない場合は作成する"""
    thread_dir = os.path.join(BASE_DIR, thread_id)
    if not os.path.exists(thread_dir):
        os.makedirs(thread_dir)
    return thread_dir


# 保存関数
def save_store(thread_id, store):
    """指定されたthread_idフォルダにstoreを保存する"""
    thread_dir = get_thread_dir(thread_id)
    with open(os.path.join(thread_dir, "store.pkl"), "wb") as f:
        pickle.dump(store, f)


def save_config(thread_id, config):
    """指定されたthread_idフォルダにconfigを保存する"""
    thread_dir = get_thread_dir(thread_id)
    with open(os.path.join(thread_dir, "config.pkl"), "wb") as f:
        pickle.dump(config, f)


def save_user_info(thread_id, user_info):
    """指定されたthread_idフォルダにuser_infoを保存する"""
    thread_dir = get_thread_dir(thread_id)
    with open(os.path.join(thread_dir, "user_info.pkl"), "wb") as f:
        pickle.dump(user_info, f)


# ロード関数
def load_store(thread_id):
    """指定されたthread_idフォルダからstoreをロードする"""
    thread_dir = get_thread_dir(thread_id)
    filepath = os.path.join(thread_dir, "store.pkl")
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            return pickle.load(f)
    return None


def load_config(thread_id):
    """指定されたthread_idフォルダからconfigをロードする"""
    thread_dir = get_thread_dir(thread_id)
    filepath = os.path.join(thread_dir, "config.pkl")
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            return pickle.load(f)
    return None


def load_user_info(thread_id):
    """指定されたthread_idフォルダからuser_infoをロードする"""
    thread_dir = get_thread_dir(thread_id)
    filepath = os.path.join(thread_dir, "user_info.pkl")
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            return pickle.load(f)
    return None
