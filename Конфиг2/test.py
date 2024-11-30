import unittest
from unittest.mock import patch, mock_open
import subprocess
import os
from typing import List
import tempfile # Добавлен для временных файлов

# Предполагается, что функции находятся в файле dependency_visualizer.py
from dependency_visualizer import get_commit_messages, build_mermaid_graph, save_graph_to_file, main


class TestCommitDependencyVisualizer(unittest.TestCase):

    @patch("subprocess.run")
    def test_get_commit_messages_success(self, mock_run):
        mock_run.return_value.stdout = "initial commit\nadded second change\nadded third change\n"
        mock_run.return_value.returncode = 0
        expected_messages = ["initial commit", "added second change", "added third change"]
        commit_messages = get_commit_messages("fake/repo/path")
        self.assertEqual(commit_messages, expected_messages[::-1])

    @patch("subprocess.run")
    def test_get_commit_messages_failure(self, mock_run):
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Git command failed"
        with self.assertRaises(Exception) as context:
            get_commit_messages("fake/repo/path")
        self.assertTrue("Git command failed" in str(context.exception))


    def test_build_mermaid_graph(self):
        commit_messages = ["initial commit", "added second change", "added third change"]
        expected_graph = (
            "graph TD;\n"
            "    0: \"initial commit\"\n"
            "    1: \"added second change\"\n"
            "    2: \"added third change\"\n"
            "    0 --> 1\n"
            "    1 --> 2\n"
        )
        graph = build_mermaid_graph(commit_messages)
        self.assertEqual(graph, expected_graph)

    @patch("builtins.open", new_callable=mock_open)
    def test_save_graph_to_file(self, mock_file):
        graph = "graph TD;\n0[\"Initial commit\"]\n1[\"Added feature\"]\n0 --> 1"
        save_graph_to_file(graph, "test.mmd")
        mock_file.assert_called_once_with("test.mmd", "w")
        mock_file().write.assert_called_once_with(graph)

    @patch("dependency_visualizer.get_commit_messages", return_value=["Test Commit"])
    @patch("dependency_visualizer.build_mermaid_graph", return_value="Test Graph")
    @patch("builtins.open", new_callable=mock_open)
    def test_main_with_existing_repo(self, mock_file, mock_build_mermaid_graph, mock_get_commit_messages):
        with patch("sys.argv", ["prog", "--repo-path", "test_repo", "--output-file", "test.mmd"]):
            main()
        mock_file.assert_called_once_with("test.mmd", "w")
        mock_file().write.assert_called_once_with("Test Graph")
        # Проверка вывода на консоль осложняется и требует дополнительного мокирования


    @patch("dependency_visualizer.get_commit_messages", return_value=[])
    @patch("dependency_visualizer.build_mermaid_graph", return_value="")
    @patch("builtins.open", new_callable=mock_open)
    def test_main_empty_repo(self, mock_file, mock_build_mermaid_graph, mock_get_commit_messages):
        with patch("sys.argv", ["prog", "--repo-path", "empty_repo", "--output-file", "test.mmd"]):
            main()
        #Проверка отсутствия записи в файл


    @patch("dependency_visualizer.get_commit_messages", side_effect=Exception("Git Error"))
    def test_main_git_error(self, mock_get_commit_messages):
        with patch("sys.argv", ["prog", "--repo-path", "error_repo", "--output-file", "test.mmd"]):
            with self.assertRaises(Exception) as context:
                main()
            self.assertTrue("Git Error" in str(context.exception))



if __name__ == "__main__":
    unittest.main()
