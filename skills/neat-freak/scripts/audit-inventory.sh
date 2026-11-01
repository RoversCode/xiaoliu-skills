#!/usr/bin/env bash
# 只读盘点指定项目：输出路径和规则文件统计，不修改项目或跟随软链。

set -euo pipefail

# 输出调用方式和错误原因，避免参数错误时意外扫描其他位置。
# Args:
#   $1: 可选的错误说明。
# Returns:
#   向标准错误输出说明，并以 64 退出。
usage() {
  [[ $# -eq 0 ]] || printf '[ERR] %s\n' "$1" >&2
  printf 'usage: %s <project-root> [--exclude <project-relative-directory>]...\n' "$0" >&2
  exit 64
}

# 输出报告区段标题。
# Args:
#   $1: 区段名称。
# Returns:
#   向标准输出写入标题。
section() {
  printf '\n## %s\n' "$1"
}

# 输出规则文件统计；软链只报告链接本身，避免读取排除目录或项目外内容。
# Args:
#   $1: 本次遍历已经纳入范围的规则文件路径。
# Returns:
#   向标准输出写入路径、链接目标或行数和字节数。
describe_rule_file() {
  local file="$1"
  local counts
  if [[ -L "$file" ]]; then
    printf '%s\tsymlink=%s\n' "$file" "$(readlink "$file")"
    return
  fi
  counts="$(wc -lc < "$file")"
  printf '%s\t%s\n' "$file" "$(printf '%s\n' "$counts" | awk '{printf "lines=%s\tbytes=%s", $1, $2}')"
}

[[ $# -ge 1 ]] || usage
[[ -d "$1" ]] || { printf '[ERR] project root is not a directory: %s\n' "$1" >&2; exit 66; }
# 相对路径必须从调用目录解析；CDPATH 会重定向并输出路径，-- 避免把目录名当选项。
PROJECT_ROOT="$1"
# 单独的 - 即使放在 -- 后仍代表 OLDPWD，所以相对路径还需显式加 ./。
[[ "$PROJECT_ROOT" == /* ]] || PROJECT_ROOT="./$PROJECT_ROOT"
PROJECT_ROOT="$(
  unset CDPATH
  cd -- "$PROJECT_ROOT" && pwd -P
)"
shift

# 默认目录名在任何深度都剪枝；.git 在 worktree 中也可能是普通文件。
PRUNE_EXPRESSION=( '(' '(' -type d -o -type l ')' '(' -name ref_code
  -o -name node_modules -o -name .next -o -name dist -o -name build
  -o -name .venv -o -name venv -o -name __pycache__ -o -name target
  -o -name vendor -o -name .turbo -o -name .cache ')' -o -name .git )

while [[ $# -gt 0 ]]; do
  [[ "$1" == "--exclude" ]] || usage "unknown argument: $1"
  [[ $# -ge 2 ]] || usage "--exclude requires a project-relative directory"
  excluded_directory="$2"
  case "$excluded_directory" in
    ''|/*|--*) usage "invalid project-relative directory: $excluded_directory" ;;
  esac
  case "/$excluded_directory/" in
    */../*) usage "--exclude cannot contain '..': $excluded_directory" ;;
  esac

  # 接受常见的 ./ 和尾部斜杠写法；不用 realpath，避免解析并进入软链目标。
  normalized_directory=""
  remaining_path="$excluded_directory/"
  while [[ "$remaining_path" == */* ]]; do
    component="${remaining_path%%/*}"
    remaining_path="${remaining_path#*/}"
    [[ -n "$component" && "$component" != "." ]] || continue
    normalized_directory="${normalized_directory:+$normalized_directory/}$component"
  done
  [[ -n "$normalized_directory" ]] || usage "--exclude cannot exclude the project root"
  if [[ -e "$PROJECT_ROOT/$normalized_directory" && ! -d "$PROJECT_ROOT/$normalized_directory" ]]; then
    usage "--exclude must name a directory: $excluded_directory"
  fi

  # find 的 -path 使用通配符语义；转义后才能按用户输入的字面目录匹配。
  literal_path="${PROJECT_ROOT%/}/$normalized_directory"
  literal_path="${literal_path//\\/\\\\}"
  literal_path="${literal_path//\*/\\*}"
  literal_path="${literal_path//\?/\\?}"
  literal_path="${literal_path//\[/\\[}"
  PRUNE_EXPRESSION+=( -o -path "$literal_path" )
  shift 2
done
PRUNE_EXPRESSION+=( ')' -prune -o -print0 )

# 一次遍历同时收集所有报告数据。-P 不跟随软链，剪枝先于枚举；管道保留 find 的失败码。
# 数组留在管道子进程中，既兼容 macOS Bash 3.2，也不需要落盘临时清单。
find -P "$PROJECT_ROOT" -mindepth 1 "${PRUNE_EXPRESSION[@]}" | {
  MARKDOWN_FILES=()
  RULE_FILES=()
  ROOT_ENTRIES=()
  OTHER_RULE_ARTIFACTS=()
  while IFS= read -r -d '' file; do
    relative_path="${file#"${PROJECT_ROOT%/}/"}"
    [[ "$relative_path" == */* ]] || ROOT_ENTRIES+=( "$file" )
    case "$relative_path" in
      .cursorrules|.windsurfrules|.cursor/rules|.qoder|.trae|.iflow)
        OTHER_RULE_ARTIFACTS+=( "$file" ) ;;
    esac

    # Markdown 清单只纳入实体文件；规则软链可显示路径，但绝不读取其内容。
    if [[ ! -L "$file" && -f "$file" ]]; then
      case "$file" in *.md|*.mdx) MARKDOWN_FILES+=( "$file" ) ;; esac
    fi
    [[ -L "$file" || -f "$file" ]] || continue
    case "${file##*/}" in
      AGENTS.override.md|AGENTS.md|CLAUDE.md|CLAUDE.local.md) RULE_FILES+=( "$file" ) ;;
    esac
  done

  printf '# neat-freak inventory v3\n'
  printf 'project_root=%s\n' "$PROJECT_ROOT"
  printf 'generated_at=%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"

  section "other-agent-rule-artifacts"
  if [[ ${#OTHER_RULE_ARTIFACTS[@]} -gt 0 ]]; then
    printf '%s\n' "${OTHER_RULE_ARTIFACTS[@]}" | LC_ALL=C sort
  fi

  section "git"
  (
    # 调用方可能正在另一个 worktree 或 hook 中；仅在查询范围隔离 Git 的仓库定位和本地状态。
    unset GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR GIT_INDEX_FILE \
      GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES \
      GIT_CEILING_DIRECTORIES GIT_DISCOVERY_ACROSS_FILESYSTEM GIT_IMPLICIT_WORK_TREE \
      GIT_PREFIX GIT_NAMESPACE GIT_CONFIG GIT_CONFIG_PARAMETERS GIT_CONFIG_COUNT \
      GIT_GRAFT_FILE GIT_SHALLOW_FILE GIT_REPLACE_REF_BASE GIT_NO_REPLACE_OBJECTS
    if GIT_ROOT="$(git -C "$PROJECT_ROOT" rev-parse --show-toplevel 2>/dev/null)"; then
      printf 'git_root=%s\n' "$GIT_ROOT"
      printf 'branch=%s\n' "$(git -C "$PROJECT_ROOT" symbolic-ref --quiet --short HEAD 2>/dev/null || true)"
      printf 'head=%s\n' "$(git -C "$PROJECT_ROOT" rev-parse --verify HEAD 2>/dev/null || printf 'unborn')"
      # 这里只读 Git 元数据；status/worktree 审查按任务需要单独执行，避免再次扫描整个仓库。
    else
      printf 'git_root=none\n'
    fi
  )

  section "rule-chain-candidates"
  if [[ ${#RULE_FILES[@]} -gt 0 ]]; then
    while IFS= read -r -d '' file; do
      describe_rule_file "$file"
    done < <(printf '%s\0' "${RULE_FILES[@]}")
  fi

  section "project-markdown"
  if [[ ${#MARKDOWN_FILES[@]} -gt 0 ]]; then
    printf '%s\n' "${MARKDOWN_FILES[@]}" | LC_ALL=C sort
  fi

  section "project-markdown-count"
  printf '%s\n' "${#MARKDOWN_FILES[@]}"

  section "root-entries"
  if [[ ${#ROOT_ENTRIES[@]} -gt 0 ]]; then
    printf '%s\n' "${ROOT_ENTRIES[@]}" | LC_ALL=C sort
  fi
}
