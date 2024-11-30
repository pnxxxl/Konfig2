import csv
import subprocess
import os
os.environ["PATH"] += os.pathsep + "C:\Program Files\Graphviz\bin"
import pydot

class DependencyVisualizer:
    def init(self, config_path):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        config = {}
        with open(self.config_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                config.update(row) # Добавляем данные в словарь
        self.repo_path = config.get('repository_path')
        self.target_file = config.get('target_file')
        self.output_path = config.get('output_path')
        return config


    def _run_git_command(self, *args):
        command = ['git', '-C', self.repo_path] + list(args)
        print(f"Выполняемая команда: {' '.join(command)}") # Добавлено для отладки
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        if result.returncode != 0:
            print(f"Вывод ошибки: {result.stderr}") # Добавлено для отладки
            raise Exception(f"Git command failed: {' '.join(command)}, Error: {result.stderr}")
        return result.stdout


    def get_commit_file_changes(self):
        """Возвращает словарь {коммит: [список файлов]}"""
        log_output = self._run_git_command("log", "--pretty=format:%H", "--name-only")
        commits = {}
        current_commit = None
        for line in log_output.splitlines():
            line = line.strip()
            if line.startswith("commit"):
                current_commit = line
                commits[current_commit] = []
            elif line:  # Не пустая строка, значит имя файла
                commits[current_commit].append(line)
        return commits

    def build_graph(self, commit_files):
        graph = pydot.Dot(graph_type='digraph')
        nodes = set()
        edges = set()

        for commit, files in commit_files.items():
            nodes.add(commit)
            for file in files:
                nodes.add(file)
                edges.add((commit, file)) # Добавляем кортеж

        for node in nodes:
            graph.add_node(pydot.Node(node))
        for edge in edges:
            graph.add_edge(pydot.Edge(edge[0], edge[1]))
        return graph

    def visualize_graph(self, graph, output_image='output.png'):
        graph.write_png(output_image)
        if os.name == 'posix':
            subprocess.run(['open', output_image])
        elif os.name == 'nt':
            os.startfile(output_image)

    def run(self):
        commit_files = self.get_commit_file_changes()
        graph = self.build_graph(commit_files)
        self.visualize_graph(graph, os.path.join(self.output_path, 'output.png'))
if name == "main":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python visualize_deps.py <config_path>")
        sys.exit(1)
    config_path = sys.argv[1]
    visualizer = DependencyVisualizer(config_path)
    visualizer.run()
    