#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git 管理模块
提供文件版本控制功能，作为文件缓存的替代方案
"""

import logging
import os
from datetime import datetime

from git import GitCommandError, InvalidGitRepositoryError, Repo

# 配置日志
logger = logging.getLogger(__name__)


class GitManager:
    """Git 管理器"""

    def __init__(self, repo_path="."):
        """
        初始化 Git 管理器

        Args:
            repo_path (str): Git 仓库路径，默认为当前目录
        """
        self.repo_path = repo_path
        self.repo = None
        self.init_repo()

    def init_repo(self):
        """初始化 Git 仓库"""
        try:
            # 尝试打开现有仓库
            self.repo = Repo(self.repo_path)
            logger.info(f"已连接到 Git 仓库: {self.repo.working_tree_dir}")
        except InvalidGitRepositoryError:
            # 如果不存在，则初始化新仓库
            try:
                self.repo = Repo.init(self.repo_path)
                logger.info(f"已初始化新的 Git 仓库: {self.repo.working_tree_dir}")
                # 设置用户信息（如果尚未设置）
                try:
                    self.repo.config_writer().set_value(
                        "user", "name", "FileMonitor"
                    ).release()
                    self.repo.config_writer().set_value(
                        "user", "email", "filemonitor@example.com"
                    ).release()
                except Exception as e:
                    logger.warning(f"设置 Git 用户信息失败: {e}")
            except GitCommandError as e:
                logger.error(f"初始化 Git 仓库失败: {e}")
                self.repo = None

    def is_ready(self):
        """
        检查 Git 管理器是否准备就绪

        Returns:
            bool: 如果 Git 管理器准备就绪则返回 True，否则返回 False
        """
        return self.repo is not None

    def add_file(self, file_path):
        """
        添加文件到 Git 暂存区

        Args:
            file_path (str): 文件路径
        """
        if not self.is_ready():
            return

        try:
            # 添加文件到暂存区
            self.repo.index.add([file_path])
            logger.debug(f"已添加文件到暂存区: {file_path}")
        except Exception as e:
            logger.error(f"添加文件到暂存区失败: {e}")

    def commit_changes(self, message=None):
        """
        提交更改

        Args:
            message (str): 提交信息，默认自动生成
        """
        if not self.is_ready():
            return

        try:
            # 检查是否有更改需要提交
            if not self.repo.is_dirty():
                logger.debug("没有更改需要提交")
                return

            # 生成提交信息
            if message is None:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                message = f"Auto commit at {timestamp}"

            # 提交更改
            commit = self.repo.index.commit(message)
            logger.info(f"已提交更改: {commit.hexsha[:8]} - {message}")
        except Exception as e:
            logger.error(f"提交更改失败: {e}")

    def get_file_diff(self, file_path, commit_hash=None):
        """
        获取文件差异

        Args:
            file_path (str): 文件路径
            commit_hash (str): 提交哈希，默认为最新提交

        Returns:
            str: 文件差异内容
        """
        if not self.is_ready():
            return ""

        try:
            if commit_hash is None:
                # 获取最新提交
                commit = self.repo.head.commit
            else:
                # 获取指定提交
                commit = self.repo.commit(commit_hash)

            # 获取文件差异
            diff = self.repo.git.diff(
                commit.parents[0].hexsha, commit.hexsha, "--", file_path
            )
            return diff
        except Exception as e:
            logger.error(f"获取文件差异失败: {e}")
            return ""

    def get_file_history(self, file_path, limit=10):
        """
        获取文件历史记录

        Args:
            file_path (str): 文件路径
            limit (int): 返回的历史记录数量限制

        Returns:
            list: 历史记录列表
        """
        if not self.is_ready():
            return []

        try:
            # 获取文件的提交历史
            commits = list(self.repo.iter_commits(paths=file_path, max_count=limit))
            history = []

            for commit in commits:
                history.append(
                    {
                        "hash": commit.hexsha[:8],
                        "message": commit.message.strip(),
                        "author": commit.author.name,
                        "date": datetime.fromtimestamp(commit.committed_date).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                    }
                )

            return history
        except Exception as e:
            logger.error(f"获取文件历史记录失败: {e}")
            return []


# 全局 Git 管理器实例
git_manager = GitManager()


def get_git_manager():
    """
    获取全局 Git 管理器实例

    Returns:
        GitManager: Git 管理器实例
    """
    return git_manager
