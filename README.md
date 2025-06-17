# Python Template for Claude Code

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-latest-green.svg)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![CI](https://github.com/discus0434/python-template-for-claude-code/actions/workflows/ci.yml/badge.svg)](https://github.com/discus0434/python-template-for-claude-code/actions/workflows/ci.yml)
[![Benchmark](https://github.com/discus0434/python-template-for-claude-code/actions/workflows/benchmark.yml/badge.svg)](https://github.com/discus0434/python-template-for-claude-code/actions/workflows/benchmark.yml)

[Claude Code](https://www.anthropic.com/claude-code)との協働に最適化された、プロダクション対応のPythonプロジェクトテンプレートです。厳格な型チェック、自動パフォーマンス測定、包括的なドキュメント、進化するメモリ管理システムを備えています。

## 🚀 クイックスタート

### このテンプレートを使用する

1. GitHubで「Use this template」ボタンをクリックして新しいリポジトリを作成
2. 新しいリポジトリをクローン
3. セットアップスクリプトを実行

```bash
# 新しいリポジトリをクローン
git clone https://github.com/yourusername/project-name.git
cd project-name

# セットアップ
make setup
```

セットアップスクリプトは以下を実行します：
- すべての `project_name` を実際のプロジェクト名に更新（途中でプロジェクト名を入力するように求められます）
- uvを使用してPython環境を初期化
- Claude Codeをインストール
- GitHub CLI（`gh`）をインストール（途中でログインを求められます）
- すべての依存関係をインストール
- pre-commitフックを設定
- 初期テストを実行

### 手動セットアップ（代替方法）

手動セットアップを希望する場合：

```bash
# プロジェクト名を更新
python scripts/update_project_name.py your_project_name

# uvをインストール（まだインストールしていない場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# Pythonバージョンを設定
uv python pin 3.12

# 依存関係をインストール
uv sync --all-extras

# pre-commitフックをインストール
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg

# テストを実行
uv run pytest
```

## ✨ 主な特徴

### 🚀 Claude Code最適化
- **進化するメモリシステム** - CLAUDE.mdが動的に更新される知識ベース
- **体系的な更新プロトコル** - 頻度・変更・品質指標ベースの自動更新
- **分散ドキュメント管理** - プロジェクトタイプ別の専門ガイド
- **GitHub統合** - `make pr`、`make issue`コマンドでシームレスな操作

### 🛠️ 開発ツールチェーン
- **[uv](https://github.com/astral-sh/uv)** - 高速なPythonパッケージマネージャー
- **[Ruff](https://github.com/astral-sh/ruff)** - 超高速Pythonリンター・フォーマッター
- **[mypy](https://mypy-lang.org/)** - strictモード＋PEP 695型構文対応
- **[pytest](https://pytest.org/)** - カバレッジ付きテストフレームワーク
- **[hypothesis](https://hypothesis.readthedocs.io/)** - プロパティベーステストフレームワーク
- **[pytest-benchmark](https://pytest-benchmark.readthedocs.io/)** - 自動パフォーマンステスト
- **[bandit](https://github.com/PyCQA/bandit)** - セキュリティスキャン
- **[pip-audit](https://github.com/pypa/pip-audit)** - 依存関係の脆弱性チェック
- **[pre-commit](https://pre-commit.com/)** - コード品質用Gitフック

### 🔍 コード品質・型安全性
- ✅ PEP 695新型構文（`type` statement）対応
- ✅ TypedDict・Literal・Protocol活用の堅牢な型システム
- ✅ JSON操作用の型安全なユーティリティ
- ✅ プロパティベーステストによるエッジケース検証
- ✅ 包括的なヘルパー関数テストスイート
- ✅ 自動セキュリティ・脆弱性チェック

### ⚡ パフォーマンス・プロファイリング
- ✅ `@profile`、`@timeit`デコレータによる性能測定
- ✅ 自動ベンチマークCI（PR時の性能比較レポート）
- ✅ コンテキストマネージャー型プロファイラー
- ✅ 性能回帰検出システム
- ✅ メモリ・実行時間の詳細監視

### 🔄 CI/CD・自動化
- ✅ 並列実行対応の高速CIパイプライン
- ✅ 自動パフォーマンスベンチマーク（PR時レポート生成）
- ✅ Dependabotによる自動依存関係更新
- ✅ GitHub CLIによるワンコマンドPR・Issue作成
- ✅ キャッシュ最適化された実行環境

### 📚 包括的ドキュメント
- ✅ **動的CLAUDE.md** - プロジェクトと共に進化する知識ベース
- ✅ **専門ガイド** - ML/バックエンドプロジェクト対応
- ✅ **協働戦略ガイド** - 人間とClaude Codeの効果的な連携方法
- ✅ **メモリ更新プロトコル** - ドキュメント品質管理フレームワーク

## 📁 プロジェクト構造

```
project-root/
├── .github/                     # GitHub Actionsの設定ファイル
│   ├── workflows/               # CI/CD + ベンチマークワークフロー
│   │   ├── ci.yml              # メインCI（テスト・リント・型チェック）
│   │   └── benchmark.yml       # パフォーマンスベンチマーク
│   ├── dependabot.yml           # Dependabotの設定
│   ├── ISSUE_TEMPLATE/          # Issueテンプレート
│   └── PULL_REQUEST_TEMPLATE.md # Pull Requestテンプレート
├── src/
│   └── project_name/            # メインパッケージ（uv syncでインストール可能）
│       ├── __init__.py
│       ├── py.typed             # PEP 561準拠の型情報マーカー
│       ├── types.py             # プロジェクト共通型定義
│       ├── core/                # コアロジック
│       │   └── example.py       # 型ヒント強化済みサンプル
│       └── utils/               # ユーティリティ
│           ├── helpers.py       # JSON・リスト・辞書操作
│           └── profiling.py     # パフォーマンス測定ツール
├── tests/                       # テストコード
│   ├── unit/                    # 単体テスト
│   │   ├── test_example.py     # 既存テスト
│   │   └── test_helpers.py     # 全ヘルパー関数テスト
│   ├── property/                # プロパティベーステスト
│   │   └── test_helpers_property.py # Hypothesis使用
│   ├── integration/             # 統合テスト
│   └── conftest.py              # pytest設定
├── docs/                        # ドキュメント
├── scripts/                     # セットアップスクリプト
├── pyproject.toml               # 依存関係・ツール設定
├── .pre-commit-config.yaml      # pre-commit設定
├── README.md                    # プロジェクト説明
└── CLAUDE.md                    # Claude Code用ガイド
```

## 🛠️ 開発

### 📋 テストの実行

```bash
# すべてのテストを実行（単体・プロパティ・統合）
make test

# カバレッジ付きで実行
make test-cov

# テスト種別で実行
uv run pytest tests/unit/ -v           # 単体テスト
uv run pytest tests/property/ -v       # プロパティベーステスト
uv run pytest tests/integration/ -v    # 統合テスト

# 特定のテストを実行
uv run pytest tests/unit/test_helpers.py -v
```

### コード品質

```bash
# コードをフォーマット
make format

# コードをリント
make lint

# 型チェック
make typecheck

# すべてのチェックを順番に実行
make check

# pre-commitで完全チェック
make check-all
```

### ⚡ パフォーマンス測定・プロファイリング

```bash
# ローカルベンチマーク実行
make benchmark

# プロファイリング実行（cProf使用）
make profile

# カスタムプロファイリング
uv run python -c "
from project_name.utils.profiling import profile, timeit, Timer

# デコレータでの測定
@profile
def heavy_function():
    return sum(i**2 for i in range(10000))

@timeit
def quick_function():
    return [i for i in range(1000)]

# コンテキストマネージャーでの測定
with Timer('Custom operation') as timer:
    result = heavy_function()
print(f'Took {timer.elapsed:.4f} seconds')
"

# 詳細プロファイリング（上位10関数表示）
uv run python -c "
from project_name.utils.profiling import profile_context
with profile_context(sort_by='cumulative', limit=10) as prof:
    # 重い処理をここに記述
    pass
"
```

### 🔗 GitHub統合

```bash
# プルリクエスト作成
make pr TITLE="新機能追加" BODY="説明" LABEL="enhancement"
make pr TITLE="バグ修正" BODY="修正内容" LABEL="bug"

# イシュー作成
make issue TITLE="機能要求" BODY="詳細" LABEL="enhancement"
make issue TITLE="バグ報告" BODY="再現手順" LABEL="bug"

# 直接gh CLIを使用
gh pr create --title "タイトル" --body "本文" --label "ラベル"
gh issue create --title "タイトル" --body "本文" --label "ラベル"
```

### 🛠️ その他のコマンド

```bash
# 利用可能なコマンドを表示
make help

# キャッシュファイルの削除
make clean

# セキュリティスキャン
make security

# 依存関係の脆弱性チェック
make audit
```

### 📦 依存関係の管理

```bash
# ランタイム依存関係を追加
uv add requests

# 開発依存関係を追加
uv add --dev pytest-mock

# ドキュメント関連依存関係を追加
uv sync --extra docs

# すべての依存関係を同期
uv sync --all-extras

# 依存関係を更新
uv lock --upgrade
```

## 🤖 Claude Code との次世代協働システム

このテンプレートはClaude Codeとの協働を革新的にサポートします：

### 🧠 進化するメモリシステム
- **体系的更新プロトコル**: 頻度・変更等による自動更新判定
- **分散メモリ管理**: メイン（CLAUDE.md）とサブ（専門ガイド）の最適分散

### 🔄 自己改善サイクル
Claude Code使用時の自動学習・改善プロセス：

1. **パターン検出**: 同じ質問2回で自動FAQ追加
2. **品質監視**: 再質問率25%超過で改善トリガー
3. **情報統合**: 新しい知識の体系的な蓄積
4. **効果測定**: 協働効率の継続的向上

### 🎯 Claude Code最適化機能

**即座に利用可能**:
- プロジェクトコンテキストの自動把握
- 型安全な開発環境（PEP 695対応）
- ワンコマンドGitHub操作（`make pr`、`make issue`）
- 自動品質チェック・パフォーマンス測定

**段階的に進化**:
- プロジェクト固有パターンの学習
- チーム開発慣習の蓄積
- トラブルシューティング知識の拡充
- 最適化されたワークフローの確立

### 📋 協働効率指標
- 再質問回数：30%減少目標
- 新規参加者オンボーディング：50%短縮目標
- コードレビュー指摘事項：40%減少目標
- 問題解決時間：大幅短縮

## 📚 ドキュメント階層

### 🎯 メインドキュメント
- **[CLAUDE.md](CLAUDE.md)** - 動的進化する包括的プロジェクトガイド
  - プロジェクト概要・コーディング規約
  - よく使うコマンド・GitHub操作
  - 型ヒント・テスト戦略・セキュリティ

### 🤝 協働・戦略ガイド
- **[claude-collaboration-guide.md](docs/claude-collaboration-guide.md)** - Claude Code協働の全て
  - メモリ更新プロトコル・品質管理フレームワーク
  - 段階的カスタマイズ・動的ルール追加
  - 効果的なフィードバックループ・継続的改善

### 🎨 プロジェクトタイプ別ガイド
- **[ml-project-guide.md](docs/ml-project-guide.md)** - 機械学習プロジェクト
  - PyTorch・Hydra・wandb統合設定
  - 実験管理・データバージョニング
  - GPU最適化・モデル管理

- **[backend-project-guide.md](docs/backend-project-guide.md)** - FastAPIバックエンド
  - 非同期データベース操作・JWT認証
  - API設計・セキュリティ設定
  - Docker開発環境・プロダクション考慮事項

## ✅ 新規プロジェクト設定チェックリスト

### 🔧 基本プロジェクト設定
- [ ] **プロジェクト名更新**: `make setup`実行またはスクリプトで一括変更
- [ ] **作者情報更新**: `pyproject.toml`の`authors`セクション
- [ ] **ライセンス選択**: LICENSEファイルを適切なライセンスに更新
- [ ] **README.md更新**: プロジェクト固有の説明・機能・使用方法
- [ ] **CLAUDE.md カスタマイズ**: プロジェクト概要をテンプレートから更新

### ⚙️ 開発環境・品質設定
- [ ] **依存関係調整**: プロジェクトに必要な追加パッケージの導入
- [ ] **型チェック厳格さ**: 必要に応じて段階的に`mypy`設定を調整
- [ ] **リントルール**: プロジェクトに合わせた`ruff`設定のカスタマイズ
- [ ] **テストカバレッジ**: `pytest`カバレッジ要件の調整
- [ ] **プロファイリング**: パフォーマンス要件に応じたベンチマーク設定

### 🔐 GitHubリポジトリ・セキュリティ設定
- [ ] **ブランチ保護**: `main`ブランチの保護ルール有効化
- [ ] **PR必須レビュー**: Pull Request作成時のレビュー要求設定
- [ ] **ステータスチェック**: CI・型チェック・テストの必須化
- [ ] **Dependabot**: 自動依存関係更新の有効化
- [ ] **Issues/Projects**: 必要に応じてプロジェクト管理機能の有効化
- [ ] **Secrets管理**: 必要なAPI키や認証情報の安全な設定

### 📚 ドキュメント・協働設定
- [ ] **CLAUDE.md詳細化**: プロジェクト固有の開発ルール・制約の追加
- [ ] **専門ガイド選択**: ML/バックエンドなど該当するガイドのインポート
- [ ] **チーム規約**: `docs/team-rules.md`などチーム固有ルールの追加
- [ ] **協働メトリクス**: 効率指標の初期値設定・測定開始

## 🔧 カスタマイズ

### 型チェックの厳格さ調整

mypyのstrictモードが最初から厳しすぎる場合：

```toml
# pyproject.toml - 基本設定から開始
[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true

# 段階的により厳格な設定を有効化
[[tool.mypy.overrides]]
module = ["project_name.core.*"]
strict = true  # まずコアモジュールにstrictモードを適用
```

### リントルールの変更

```toml
# pyproject.toml
[tool.ruff.lint]
# 必要に応じてルールコードを追加・削除
select = ["E", "F", "I"]  # 基本から開始
ignore = ["E501"]  # 行の長さはフォーマッターが処理
```

### テストカバレッジ要件の変更

```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = [
    "--cov-fail-under=60",  # 初期要件を低めに設定
]
```

## 🔗 外部リソース・参考資料

### 🛠️ 開発ツール公式ドキュメント
- **[uv ドキュメント](https://docs.astral.sh/uv/)** - Pythonパッケージ管理
- **[Ruff ドキュメント](https://docs.astral.sh/ruff/)** - リント・フォーマッター
- **[mypy ドキュメント](https://mypy.readthedocs.io/)** - 型チェッカー
- **[pytest ドキュメント](https://docs.pytest.org/en/stable/)** - テストフレームワーク
- **[Hypothesis ドキュメント](https://hypothesis.readthedocs.io/)** - プロパティベーステスト

### 🤖 Claude Code関連
- **[Claude Code 公式サイト](https://www.anthropic.com/claude-code)** - 基本情報・インストール
- **[Claude Code ドキュメント](https://docs.anthropic.com/en/docs/claude-code)** - 使用方法・ベストプラクティス

### 🐍 Python・型ヒント
- **[PEP 695 - Type Parameter Syntax](https://peps.python.org/pep-0695/)** - 新型構文仕様
- **[TypedDict Guide](https://docs.python.org/3/library/typing.html#typing.TypedDict)** - 型安全な辞書
- **[Python 3.12 リリースノート](https://docs.python.org/3/whatsnew/3.12.html)** - 新機能一覧

---

## 📄 ライセンス

このテンプレートはMITライセンスの下でリリースされています。詳細は[LICENSE](LICENSE)をご覧ください。

あなたのプロジェクトは任意のライセンスを使用できます - LICENSEファイルを更新するだけです。

---

## 🚀 始めましょう

Claude Codeとの協働による、次世代Python開発を体験してください：

1. **このテンプレートを使用** → 「Use this template」ボタンをクリック
2. **セットアップ実行** → `make setup`で全自動環境構築
3. **開発開始** → 型安全・高性能・自動品質管理の開発環境を即座に利用

**Happy Coding with Claude! 🤖✨**
