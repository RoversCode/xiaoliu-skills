"""通过命令行验证盘点脚本的项目边界、排除规则和只读行为。"""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "skills/neat-freak/scripts/audit-inventory.sh"


class AuditInventoryTests(unittest.TestCase):
    """在独立临时项目里运行真实脚本，避免接触用户的规则和仓库。"""

    def setUp(self):
        """创建带空格的项目目录，并隔离外部 Git 环境变量。

        Returns:
            None。
        """
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.workspace = Path(self.temporary_directory.name).resolve()
        self.project = self.workspace / "project with spaces"
        self.project.mkdir()
        self.environment = dict(os.environ)
        for variable in (
            "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
            "GIT_CONFIG", "GIT_CONFIG_PARAMETERS", "GIT_CONFIG_COUNT",
        ):
            self.environment.pop(variable, None)

    def write_file(self, relative_path, content="example\n"):
        """在测试项目中准备一个文件。

        Args:
            relative_path: 相对于测试项目的文件路径。
            content: 要写入的文本。

        Returns:
            创建的文件路径。
        """
        path = self.project / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def run_inventory(self, *arguments):
        """执行真实 Bash 入口并保存输出。

        Args:
            *arguments: 项目路径之后的命令行参数。

        Returns:
            包含退出码、标准输出和标准错误的执行结果。
        """
        return subprocess.run(
            ["bash", str(SCRIPT), str(self.project), *arguments],
            env=self.environment,
            text=True,
            capture_output=True,
            check=False,
        )

    def section(self, output, name):
        """取出输出中的一个区段，便于核对公开报告内容。

        Args:
            output: 脚本的完整标准输出。
            name: 要查找的区段名称。

        Returns:
            该区段的非空内容行。
        """
        body = output.split(f"## {name}\n", 1)[1].split("\n## ", 1)[0]
        return [line for line in body.splitlines() if line]

    def test_default_exclusions_apply_at_every_depth(self):
        """默认排除目录不进入 Markdown 清单和计数。

        Returns:
            None。
        """
        kept = self.write_file("docs/kept.md")
        for directory in (
            "ref_code", "nested/ref_code", "node_modules", "nested/node_modules",
            "dist", "build", ".git", ".venv", "__pycache__", "vendor", "target",
        ):
            self.write_file(f"{directory}/hidden.md")
        result = self.run_inventory()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.section(result.stdout, "project-markdown"), [str(kept)])
        self.assertEqual(self.section(result.stdout, "project-markdown-count"), ["1"])

    def test_repeatable_exclusions_are_literal_project_relative_directories(self):
        """重复排除参数支持空格和通配符字符，只排除指定目录。

        Returns:
            None。
        """
        kept = self.write_file("private-backup/kept.md")
        self.write_file("private files/hidden.md")
        self.write_file("docs/[draft]*/hidden.md")
        also_kept = self.write_file("docs/d/kept.mdx")
        result = self.run_inventory(
            "--exclude", "private files", "--exclude", "docs/[draft]*"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            self.section(result.stdout, "project-markdown"),
            sorted([str(kept), str(also_kept)]),
        )
        self.assertEqual(self.section(result.stdout, "project-markdown-count"), ["2"])
        self.assertNotIn(str(self.project / "private files"), result.stdout)

    @unittest.skipIf(os.geteuid() == 0, "root 能读取无权限目录，无法验证提前剪枝")
    def test_excluded_directories_are_not_entered(self):
        """不可读的排除目录不会产生遍历错误，证明过滤发生在进入之前。

        Returns:
            None。
        """
        for name in ("ref_code", "private"):
            directory = self.write_file(f"{name}/hidden.md").parent
            directory.chmod(0)
            self.addCleanup(directory.chmod, 0o700)
        result = self.run_inventory("--exclude", "private")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(self.section(result.stdout, "project-markdown-count"), ["0"])

    def test_symlinks_cannot_expose_excluded_or_external_contents(self):
        """目录和规则软链只能作为链接列出，不能读取链接目标。

        Returns:
            None。
        """
        hidden_rule = self.write_file("ref_code/AGENTS.md", "secret\n" * 11)
        outside = self.workspace / "outside"
        outside.mkdir()
        (outside / "hidden.md").write_text("outside\n", encoding="utf-8")
        (self.project / "reference-alias").symlink_to(hidden_rule.parent)
        (self.project / "outside-alias").symlink_to(outside)
        (self.project / "AGENTS.md").symlink_to(hidden_rule)
        (self.project / "linked.md").symlink_to(hidden_rule)
        result = self.run_inventory()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.section(result.stdout, "project-markdown"), [])
        self.assertNotIn("lines=11", result.stdout)
        self.assertNotIn(str(outside / "hidden.md"), result.stdout)

    def test_default_scope_does_not_inventory_home_or_ancestor_rules(self):
        """默认盘点只列本项目，不查询祖先目录和其他平台安装面。

        Returns:
            None。
        """
        ancestor_rule = self.workspace / "AGENTS.md"
        ancestor_rule.write_text("ancestor\n", encoding="utf-8")
        project_rule = self.write_file("src/AGENTS.md")
        result = self.run_inventory()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(str(ancestor_rule), result.stdout)
        self.assertNotIn(str(Path.home()), result.stdout)
        self.assertIn(str(project_rule), result.stdout)

    def test_inventory_and_count_share_one_tree_walk(self):
        """清单、计数和根目录条目复用一次真实目录遍历。

        Returns:
            None。
        """
        self.write_file("README.md")
        executable_directory = self.workspace / "bin"
        executable_directory.mkdir()
        call_log = self.workspace / "find-calls"
        real_find = shutil.which("find")
        self.assertIsNotNone(real_find)
        wrapper = executable_directory / "find"
        wrapper.write_text(
            '#!/bin/bash\nprintf "called\\n" >> "$INVENTORY_FIND_LOG"\n'
            'exec "$INVENTORY_REAL_FIND" "$@"\n',
            encoding="utf-8",
        )
        wrapper.chmod(0o755)
        self.environment.update(
            PATH=f"{executable_directory}{os.pathsep}{self.environment['PATH']}",
            INVENTORY_FIND_LOG=str(call_log),
            INVENTORY_REAL_FIND=real_find,
        )
        result = self.run_inventory()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(call_log.read_text(encoding="utf-8").splitlines(), ["called"])

    def test_non_git_project_and_empty_git_repository_are_supported(self):
        """没有 Git 或尚无提交时仍能完整输出盘点结果。

        Returns:
            None。
        """
        result = self.run_inventory()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("git_root=none", result.stdout)
        subprocess.run(
            ["git", "init", "--quiet", str(self.project)],
            env=self.environment, check=True,
        )
        result = self.run_inventory()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("head=unborn\n", result.stdout)
        self.assertNotIn("head=HEAD", result.stdout)

    def test_relative_root_uses_current_directory_despite_cdpath(self):
        """相对项目路径始终以调用目录为准，不能被 CDPATH 重定向。

        Returns:
            None。
        """
        kept = self.write_file("README.md")
        redirected_parent = self.workspace / "elsewhere"
        redirected_project = redirected_parent / self.project.name
        redirected_project.mkdir(parents=True)
        (redirected_project / "wrong.md").write_text("wrong project\n", encoding="utf-8")
        for cdpath in (str(self.workspace), str(redirected_parent)):
            with self.subTest(cdpath=cdpath):
                result = subprocess.run(
                    ["bash", str(SCRIPT), self.project.name],
                    cwd=self.workspace,
                    env=dict(self.environment, CDPATH=cdpath),
                    text=True, capture_output=True, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(f"project_root={self.project}\n", result.stdout)
                self.assertEqual(self.section(result.stdout, "project-markdown"), [str(kept)])

    def test_project_name_starting_with_dash_is_not_a_cd_option(self):
        """以短横线开头的项目名按目录处理，不作为 cd 的选项。

        Returns:
            None。
        """
        # 回归旧版时 cd -P 可能跳到用户目录，先拦住错误根路径再交给真实 find。
        executable_directory = self.workspace / "guard-bin"
        executable_directory.mkdir()
        wrapper = executable_directory / "find"
        wrapper.write_text(
            '#!/bin/bash\n'
            '[[ "$2" == "$INVENTORY_ALLOWED_ROOT" ]] || {\n'
            '  printf "refusing inventory outside test project\\n" >&2\n'
            '  exit 70\n'
            '}\nexec "$INVENTORY_REAL_FIND" "$@"\n',
            encoding="utf-8",
        )
        wrapper.chmod(0o755)
        for directory_name in ("-P", "-"):
            with self.subTest(directory_name=directory_name):
                project = self.workspace / directory_name
                project.mkdir()
                kept = project / "README.md"
                kept.write_text("project\n", encoding="utf-8")
                environment = dict(
                    self.environment,
                    PATH=f"{executable_directory}{os.pathsep}{self.environment['PATH']}",
                    INVENTORY_ALLOWED_ROOT=str(project), INVENTORY_REAL_FIND=shutil.which("find"),
                    OLDPWD=str(self.project),
                )
                result = subprocess.run(
                    ["bash", str(SCRIPT), project.name], cwd=self.workspace,
                    env=environment, text=True, capture_output=True, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(f"project_root={project}\n", result.stdout)
                self.assertEqual(self.section(result.stdout, "project-markdown"), [str(kept)])

    def test_git_metadata_ignores_inherited_repository_location(self):
        """外部 Git 定位变量不能让项目 A 的盘点报告项目 B 的仓库。

        Returns:
            None。
        """
        other_project = self.workspace / "other repository"
        for repository, branch in ((self.project, "target-project"), (other_project, "other-project")):
            subprocess.run(
                ["git", "init", "--quiet", str(repository)],
                env=self.environment, check=True,
            )
            subprocess.run(
                ["git", "-C", str(repository), "symbolic-ref", "HEAD", f"refs/heads/{branch}"],
                env=self.environment, check=True,
            )
        polluted_locations = (
            {"GIT_DIR": str(other_project / ".git")},
            {"GIT_WORK_TREE": str(other_project)},
            {"GIT_DIR": str(other_project / ".git"), "GIT_WORK_TREE": str(other_project)},
            {"GIT_COMMON_DIR": str(self.workspace / "missing-git-directory")},
            {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.worktree",
             "GIT_CONFIG_VALUE_0": str(other_project)},
        )
        for variables in polluted_locations:
            with self.subTest(variables=variables):
                result = subprocess.run(
                    ["bash", str(SCRIPT), str(self.project)],
                    env=dict(self.environment, **variables),
                    text=True, capture_output=True, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(
                    self.section(result.stdout, "git"),
                    [f"git_root={self.project}", "branch=target-project", "head=unborn"],
                )

    def test_inventory_does_not_modify_project_files(self):
        """成功盘点不会创建、修改或删除项目文件。

        Returns:
            None。
        """
        self.write_file("AGENTS.md")
        self.write_file("docs/guide.md")
        before = {path.relative_to(self.project): path.read_bytes()
                  for path in self.project.rglob("*") if path.is_file()}
        result = self.run_inventory()
        after = {path.relative_to(self.project): path.read_bytes()
                 for path in self.project.rglob("*") if path.is_file()}
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(before, after)

    def test_invalid_arguments_fail_with_an_explanation(self):
        """无效参数明确失败，不能悄悄扩大扫描范围。

        Returns:
            None。
        """
        for arguments in (
            ("--unknown",), ("--exclude",), ("--exclude", ""),
            ("--exclude", "."), ("--exclude", "../outside"),
            ("--exclude", "docs/../../outside"),
            ("--exclude", str(self.workspace)), ("extra-root",),
        ):
            with self.subTest(arguments=arguments):
                result = self.run_inventory(*arguments)
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(result.stderr.strip())
        for root in (self.workspace / "missing", self.write_file("plain-file")):
            with self.subTest(root=root):
                result = subprocess.run(
                    ["bash", str(SCRIPT), str(root)], text=True,
                    capture_output=True, check=False, env=self.environment,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(result.stderr.strip())


if __name__ == "__main__":
    unittest.main()
