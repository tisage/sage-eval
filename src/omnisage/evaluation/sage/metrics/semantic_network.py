"""
Semantic Network Metrics for SAGE Framework Layer 3

语义网络分析
"""

from typing import Dict, List, Tuple, Set, Optional
from collections import defaultdict, Counter
import re
import math


class SemanticNetworkAnalyzer:
    """
    语义网络分析器

    基于词共现构建语义网络，分析概念关联

    实现指标：
    - 网络密度 (Network Density)
    - 中心度 (Centrality)
    - 连通性 (Connectivity)
    """

    def __init__(self, window_size: int = 5, min_cooccurrence: int = 2):
        """
        初始化语义网络分析器

        Args:
            window_size: 共现窗口大小（词数）
            min_cooccurrence: 最小共现次数（低于此值的边被过滤）
        """
        self.window_size = window_size
        self.min_cooccurrence = min_cooccurrence

        # 停用词列表
        self.stopwords = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'she', 'her', 'his', 'they', 'them',
            'i', 'you', 'we', 'or', 'but', 'if', 'not', 'this', 'have', 'had',
            'were', 'been', 'being', 'do', 'does', 'did', 'can', 'could',
            'would', 'should', 'may', 'might', 'must', 'shall', 'so', 'than'
        }

    def tokenize(self, text: str) -> List[str]:
        """分词并清理"""
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        words = [w for w in words if w not in self.stopwords]
        return words

    def build_cooccurrence_graph(
        self,
        text: str
    ) -> Tuple[Dict[Tuple[str, str], int], Set[str]]:
        """
        构建词共现图

        Args:
            text: 输入文本

        Returns:
            (edges, nodes)
            edges: {(word1, word2): count}
            nodes: {word1, word2, ...}
        """
        words = self.tokenize(text)

        edges = defaultdict(int)
        nodes = set()

        # 滑动窗口提取共现关系
        for i in range(len(words)):
            window = words[i:i+self.window_size]

            # 窗口内任意两词视为共现
            for j in range(len(window)):
                for k in range(j+1, len(window)):
                    word1, word2 = sorted([window[j], window[k]])  # 排序保证一致性
                    edges[(word1, word2)] += 1
                    nodes.add(word1)
                    nodes.add(word2)

        # 过滤低频边
        filtered_edges = {
            edge: count
            for edge, count in edges.items()
            if count >= self.min_cooccurrence
        }

        # 重新提取节点（只包含有效边的节点）
        filtered_nodes = set()
        for (w1, w2) in filtered_edges.keys():
            filtered_nodes.add(w1)
            filtered_nodes.add(w2)

        return filtered_edges, filtered_nodes

    def calculate_network_density(
        self,
        edges: Dict[Tuple[str, str], int],
        nodes: Set[str]
    ) -> float:
        """
        计算网络密度

        Density = 实际边数 / 最大可能边数
        Density = E / (N*(N-1)/2)

        高密度 = 概念关联紧密
        低密度 = 概念关联稀疏
        """
        num_nodes = len(nodes)
        num_edges = len(edges)

        if num_nodes < 2:
            return 0.0

        max_edges = num_nodes * (num_nodes - 1) // 2

        density = num_edges / max_edges if max_edges > 0 else 0.0

        return density

    def calculate_degree_centrality(
        self,
        edges: Dict[Tuple[str, str], int],
        nodes: Set[str]
    ) -> Dict[str, float]:
        """
        计算度中心性

        Degree(v) = v的邻居数

        高度中心性 = 该词与很多其他词共现（核心概念）
        """
        degree = defaultdict(int)

        for (w1, w2) in edges.keys():
            degree[w1] += 1
            degree[w2] += 1

        # 归一化
        num_nodes = len(nodes)
        if num_nodes <= 1:
            return {}

        max_degree = num_nodes - 1

        centrality = {
            word: deg / max_degree
            for word, deg in degree.items()
        }

        return centrality

    def calculate_average_centrality(
        self,
        centrality: Dict[str, float]
    ) -> float:
        """计算平均中心性"""
        if not centrality:
            return 0.0

        return sum(centrality.values()) / len(centrality)

    def find_top_central_words(
        self,
        centrality: Dict[str, float],
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """找到中心性最高的top_k个词"""
        sorted_words = sorted(
            centrality.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return sorted_words[:top_k]

    def calculate_connectivity(
        self,
        edges: Dict[Tuple[str, str], int],
        nodes: Set[str]
    ) -> float:
        """
        计算连通性（简化版）

        使用平均边权重作为连通性指标

        高连通性 = 词语之间频繁共现
        """
        if not edges:
            return 0.0

        total_weight = sum(edges.values())
        num_edges = len(edges)

        avg_weight = total_weight / num_edges

        # 归一化到[0,1]，假设最大共现次数为50
        max_weight = 50.0
        connectivity = min(1.0, avg_weight / max_weight)

        return connectivity

    def calculate_all(self, text: str) -> Dict[str, any]:
        """
        计算所有语义网络指标

        Args:
            text: 输入文本

        Returns:
            {
                "network_density": float,
                "average_centrality": float,
                "connectivity": float,
                "top_central_words": [(word, centrality), ...],
                "num_nodes": int,
                "num_edges": int
            }
        """
        edges, nodes = self.build_cooccurrence_graph(text)

        if not nodes:
            return {
                "network_density": 0.0,
                "average_centrality": 0.0,
                "connectivity": 0.0,
                "top_central_words": [],
                "num_nodes": 0,
                "num_edges": 0
            }

        density = self.calculate_network_density(edges, nodes)
        centrality = self.calculate_degree_centrality(edges, nodes)
        avg_centrality = self.calculate_average_centrality(centrality)
        connectivity = self.calculate_connectivity(edges, nodes)
        top_words = self.find_top_central_words(centrality)

        return {
            "network_density": density,
            "average_centrality": avg_centrality,
            "connectivity": connectivity,
            "top_central_words": top_words,
            "num_nodes": len(nodes),
            "num_edges": len(edges)
        }

    def score_semantic_network(
        self,
        network_density: float,
        average_centrality: float,
        connectivity: float,
        density_weight: float = 0.3,
        centrality_weight: float = 0.4,
        connectivity_weight: float = 0.3
    ) -> Tuple[float, Dict[str, float]]:
        """
        将语义网络指标映射到1-5分制

        映射规则：
        - 网络密度: 0.05→1分, 0.20→5分
        - 平均中心性: 0.10→1分, 0.40→5分
        - 连通性: 0.05→1分, 0.20→5分

        Args:
            network_density: 网络密度
            average_centrality: 平均中心性
            connectivity: 连通性
            density_weight: 密度权重
            centrality_weight: 中心性权重
            connectivity_weight: 连通性权重

        Returns:
            (综合分数, {density_score, centrality_score, connectivity_score})
        """
        # 密度映射
        if network_density < 0.05:
            density_score = 1.0
        elif network_density > 0.20:
            density_score = 5.0
        else:
            density_score = 1.0 + (network_density - 0.05) / 0.15 * 4.0

        # 中心性映射
        if average_centrality < 0.10:
            centrality_score = 1.0
        elif average_centrality > 0.40:
            centrality_score = 5.0
        else:
            centrality_score = 1.0 + (average_centrality - 0.10) / 0.30 * 4.0

        # 连通性映射
        if connectivity < 0.05:
            connectivity_score = 1.0
        elif connectivity > 0.20:
            connectivity_score = 5.0
        else:
            connectivity_score = 1.0 + (connectivity - 0.05) / 0.15 * 4.0

        # 加权平均（归一化）
        total_weight = density_weight + centrality_weight + connectivity_weight
        if total_weight > 0:
            final_score = (
                density_weight * density_score +
                centrality_weight * centrality_score +
                connectivity_weight * connectivity_score
            ) / total_weight
        else:
            final_score = 0.0

        return final_score, {
            "density_score": density_score,
            "centrality_score": centrality_score,
            "connectivity_score": connectivity_score
        }


# ==================== 辅助函数 ====================

def analyze_semantic_network(
    text: str,
    window_size: int = 5,
    min_cooccurrence: int = 2
) -> Dict[str, any]:
    """
    便捷函数：分析语义网络

    Args:
        text: 输入文本
        window_size: 共现窗口大小
        min_cooccurrence: 最小共现次数

    Returns:
        包含所有指标的字典
    """
    analyzer = SemanticNetworkAnalyzer(
        window_size=window_size,
        min_cooccurrence=min_cooccurrence
    )
    return analyzer.calculate_all(text)
