---
title: CLAUDE.md
created_at: 2025-06-14
updated_at: 2025-06-15
# このプロパティは、Claude Codeが関連するドキュメントの更新を検知するために必要です。消去しないでください。
---

このファイルは、[Claude Code](https://www.anthropic.com/claude-code) がこのリポジトリのコードを扱う際のガイダンスを提供します。

## プロジェクト概要

**To Claude Code: プロジェクトを開始する前に、必ずこの項目をプロジェクトに特化したものに更新してください。**

このプロジェクトは、Claude Codeでの開発に最適化されたPythonプロジェクトテンプレートです。
厳格な型チェック、自動化されたコード品質管理、CIに加えて、GitHub CLIを使用したGitHub操作をサポートします。
また、Claude Codeとの協働をサポートするためのドキュメントも提供します。

### 開発方針

- **パッケージ構造**: コアロジックは `src/knowledge_system` に配置し、パッケージとして管理
- **依存関係管理**: `uv` を使用し、`uv sync` で開発環境を構築
- **コード品質**: `ruff` によるリント・フォーマット、`mypy` による型チェック
- **自動化**: `pre-commit` によるコード品質の自動チェック
- **CI/CD**: GitHub Actionsによる継続的インテグレーション

## 技術スタック

- **言語**: Python 3.12+
- **主要ツール**: uv (パッケージ管理), Ruff (リント・フォーマット), mypy (型チェック), pytest (テスト)
- **パッケージ管理**: uv
- **リンター/フォーマッター**: ruff
- **型チェッカー**: mypy (strict mode + PEP 695対応)
- **テストフレームワーク**: pytest + Hypothesis (プロパティベーステスト)
- **パフォーマンス**: pytest-benchmark (自動ベンチマーク)
- **自動化**: pre-commit, GitHub Actions

## プロジェクト構造(デフォルト。必要に応じて更新してください)

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
│   └── knowledge_system/            # メインパッケージ（uv syncでインストール可能）
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
│   ├── property/                # プロパティベーステスト（Hypothesis）
│   │   └── test_helpers_property.py # Hypothesis使用
│   ├── integration/             # 統合テスト
│   └── conftest.py              # pytest設定
├── docs/                        # ドキュメント
├── scripts/                     # ユーティリティスクリプト
├── pyproject.toml               # uv/ruff/mypyの設定ファイル
├── .gitignore                   # バージョン管理除外ファイル
├── .pre-commit-config.yaml      # pre-commitの設定ファイル
├── README.md                    # プロジェクトの説明
└── CLAUDE.md                    # このファイル
```

## 型システムとコード品質

### Python3.12+基準の強化された型ヒント

**PEP 695新型構文とTypedDict・Literal・Protocolの活用**
```python
# src/knowledge_system/types.py で定義済み
from knowledge_system.types import ItemDict, ProcessorStatus, JSONObject

# PEP 695型構文の使用
type ProcessorStatus = Literal["success", "error", "pending"]
type JSONValue = str | int | float | bool | None | dict[str, "JSONValue"] | list["JSONValue"]

# 構造化されたデータ
item: ItemDict = {"id": 1, "name": "テスト", "value": 100}

# ステータス管理
status: ProcessorStatus = "success"  # "success" | "error" | "pending"

# JSON操作
config: JSONObject = {"setting": True, "count": 42}
```

## コーディング規約

### Python コーディングスタイル

- **型ヒント**: Python 3.12+ の型ヒントを必ず使用（mypy strict mode + PEP 695準拠）
- **Docstring**: NumPy形式のDocstringを使用
- **命名規則**:
  - クラス: PascalCase
  - 関数/変数: snake_case
  - 定数: UPPER_SNAKE_CASE
  - プライベート: 先頭に `_`
- **インポート順序**: 標準ライブラリ → サードパーティ → ローカル（ruffが自動整理）
- **インポート形式**: `from knowledge_system.module import function`

### 更新された型ヒントベストプラクティス

```python
# 共通型の使用
from knowledge_system.types import ItemDict, ProcessorStatus, JSONObject
from typing import Protocol
from collections.abc import Sequence

class DataProcessor(Protocol):
    """改良されたデータプロセッサープロトコル"""
    def process(self, data: list[ItemDict]) -> list[ItemDict]: ...

def process_items(
    items: list[ItemDict],
    processor: DataProcessor,
    *,  # キーワード専用引数を強制
    validate: bool = True,
) -> list[ItemDict]:
    """アイテムを処理する。

    Parameters
    ----------
    items : list[ItemDict]
        処理対象のアイテムリスト
    processor : DataProcessor
        データプロセッサー
    validate : bool
        バリデーションを実行するか

    Returns
    -------
    list[ItemDict]
        処理済みアイテムのリスト
    """
    if validate and not items:
        raise ValueError("データが空です")
    return processor.process(items)
```

## パフォーマンス測定とベンチマーク

### プロファイリングツールの使用

```python
from knowledge_system.utils.profiling import profile, timeit, Timer, profile_context

# 関数デコレーター
@profile
def heavy_computation():
    return sum(i**2 for i in range(10000))

@timeit
def quick_function():
    return [i for i in range(1000)]

# コンテキストマネージャー
with Timer("Custom operation") as timer:
    result = process_large_dataset()
print(f"Took {timer.elapsed:.4f} seconds")

# 詳細プロファイリング
with profile_context(sort_by="cumulative", limit=10) as prof:
    complex_operation()
```

### ベンチマーク自動化

GitHub Actionsで自動ベンチマークが実行されます：
- PR作成時にパフォーマンス比較
- 10%以上の性能低下でアラート
- ベンチマーク結果をPRコメントに自動投稿

## テスト戦略

### テストの種類

1. **単体テスト** (`tests/unit/`)
   - 関数・クラスの基本動作
   - 正常系・異常系・エッジケース

2. **プロパティベーステスト** (`tests/property/`)
   - Hypothesisで様々な入力パターンを自動生成
   - 不変条件と数学的性質を検証

3. **統合テスト** (`tests/integration/`)
   - コンポーネント間の連携

### テスト命名規約

```python
# 日本語で意図を明確に
def test_正常系_有効なデータで処理成功():
    """chunk_listが正しくチャンク化できることを確認。"""

 def test_異常系_不正なサイズでValueError():
    """チャンクサイズが0以下の場合、ValueErrorが発生することを確認。"""

def test_エッジケース_空リストで空結果():
    """空のリストをチャンク化すると空の結果が返されることを確認。"""
```

## セキュリティベストプラクティス

### 自動セキュリティチェック

```bash
# セキュリティスキャン
make security

# 依存関係の脆弱性チェック
make audit
```

## よく使うコマンド

### 基本的な開発コマンド（Makefile使用）

```bash
# 開発環境のセットアップ
make setup                  # 依存関係インストール + pre-commitフック設定など

# テスト実行
make test                   # 全テスト実行（単体・プロパティベース・統合）
make test-cov               # カバレッジ付きテスト実行
make test-unit              # 単体テストのみ実行
make test-property          # プロパティベーステストのみ実行

# コード品質チェック
make format                 # コードフォーマット
make lint                   # リントチェック（自動修正付き）
make typecheck              # 型チェック（strict mode）
make security               # セキュリティチェック（bandit）
make audit                  # 依存関係の脆弱性チェック（pip-audit）

# パフォーマンス測定
make benchmark              # ローカルベンチマーク実行
make profile                # プロファイリング実行

# 統合チェック
make check                  # format, lint, typecheck, testを順番に実行
make check-all              # pre-commitで全ファイルをチェック

# パフォーマンス測定
make benchmark              # ローカルベンチマーク実行
make profile                # プロファイリング実行

# GitHub操作
make pr TITLE="タイトル" BODY="本文" [LABEL="ラベル"]      # PR作成
make issue TITLE="タイトル" BODY="本文" [LABEL="ラベル"]   # イシュー作成

# その他
make clean                  # キャッシュファイルの削除
make help                   # 利用可能なコマンド一覧

# 依存関係の追加
uv add package_name                    # ランタイム依存関係
uv add --dev dev_package_name          # 開発依存関係
uv sync --all-extras                   # 全依存関係を同期
uv lock --upgrade                      # 依存関係を更新
```

### 直接実行する場合（uv run使用）

```bash
# Makefileが使えない環境での代替コマンド
uv run pytest                        # 全テスト
uv run pytest tests/unit/           # 単体テストのみ
uv run pytest tests/property/       # プロパティテストのみ
uv run ruff format .                 # フォーマット
uv run ruff check . --fix           # リント
uv run mypy src/ --strict           # 型チェック
uv run bandit -r src/               # セキュリティスキャン
uv run pip-audit                    # 脆弱性チェック
uv run pre-commit run --all-files   # 全チェック
```

### Time-saving tips

- 複数の独立した処理を実行しなければならない場合は、コマンドを順番に呼び出すのではなく、同時に実行可能なものをまとめて実行することを推奨
- コマンドを実行する前に、`make help` を実行して、利用可能なコマンドを確認可能

## GitHub操作のベストプラクティス

Claude Codeは `gh` コマンドを使用してGitHub操作を行うことができます。

### プルリクエスト作成

#### ブランチ名の命名規則

- 機能追加: `feature/...`
- バグ修正: `fix/...`
- リファクタリング: `refactor/...`
- ドキュメント更新: `docs/...`
- テスト: `test/...`

#### ラベル名の命名規則

- 機能追加: `enhancement`
- バグ修正: `bug`
- リファクタリング: `refactor`
- ドキュメント更新: `documentation`
- テスト: `test`

#### コマンドの例

```bash
# Makefileコマンドを使用したPR作成
make pr TITLE="機能追加" BODY="新しい機能を実装しました" LABEL="enhancement"
make pr TITLE="認証エラー修正" BODY="ログイン時の500エラーを修正" LABEL="bug"
make pr TITLE="ドキュメント更新" BODY="READMEを更新しました" LABEL="documentation"

# ラベルなしでPR作成
make pr TITLE="リファクタリング" BODY="コードの可読性を向上させました"

# 直接gh CLIを使用する場合
gh pr create --title "Feature: Add new functionality" --body "Description of changes"

# ドラフトPRの作成
gh pr create --draft --title "WIP: Working on feature" --body "Description of changes"
```

### イシュー管理

```bash
# Makefileコマンドを使用したイシューの作成
make issue TITLE="認証の不具合" BODY="ログイン時にエラーが発生します" LABEL="bug"
make issue TITLE="新機能の提案" BODY="〜の機能があると便利です" LABEL="enhancement"
make issue TITLE="Claude Code改善" BODY="〜の部分で改善が必要です" LABEL="documentation"
make issue TITLE="質問" BODY="〜について教えてください" LABEL="question"

# ラベルなしでイシュー作成
make issue TITLE="一般的な改善提案" BODY="〜を改善してはどうでしょうか"

# 直接gh CLIを使用する場合
gh issue create --title "Bug: Fix authentication" --body "Description"

# イシューの一覧表示
gh issue list

# イシューの詳細表示
gh issue view 123
```

## テスト戦略

### テストの種類

1. **単体テスト** (`tests/unit/`)
   - 関数・クラスの基本動作
   - 正常系・異常系・エッジケース

2. **プロパティベーステスト** (`tests/property/`)
   - Hypothesisで様々な入力パターンを自動生成
   - 不変条件と数学的性質を検証

3. **統合テスト** (`tests/integration/`)
   - コンポーネント間の連携

### テスト命名規約

```python
# 日本語で意図を明確に
def test_正常系_有効なデータで処理成功():
    """chunk_listが正しくチャンク化できることを確認。"""

def test_異常系_不正なサイズでValueError():
    """チャンクサイズが0以下の場合、ValueErrorが発生することを確認。"""

def test_エッジケース_空リストで空結果():
    """空のリストをチャンク化すると空の結果が返されることを確認。"""
```

## パフォーマンス測定とベンチマーク

### プロファイリングツールの使用

```python
from knowledge_system.utils.profiling import profile, timeit, Timer, profile_context

# 関数デコレーター
@profile
def heavy_computation():
    return sum(i**2 for i in range(10000))

@timeit
def quick_function():
    return [i for i in range(1000)]

# コンテキストマネージャー
with Timer("Custom operation") as timer:
    result = process_large_dataset()
print(f"Took {timer.elapsed:.4f} seconds")

# 詳細プロファイリング
with profile_context(sort_by="cumulative", limit=10) as prof:
    complex_operation()
```

### ベンチマーク自動化

GitHub Actionsで自動ベンチマークが実行されます：
- PR作成時にパフォーマンス比較
- 10%以上の性能低下でアラート
- ベンチマーク結果をPRコメントに自動投稿

## 実装戦略

このプロジェクトで作業する際は、以下の点に特に注意してください：

1. **開発環境**
   - すべてのPythonコマンドに `uv run` を前置
   - 新しい依存関係は `uv add` で追加（直接 pyproject.toml を編集しない）

2. **コード品質**
   - 型ヒントは省略しない（mypy strict mode + PEP 695準拠）
   - 新しいコードを書いた後は必ず `make format` を実行
   - テストを書く際は、正常系・異常系・エッジケースをカバー

3. **パッケージ構造**
   - コアロジックは必ず `src/knowledge_system` パッケージ内に配置
   - インポートは `from knowledge_system.module import ...` の形式を使用

4. **エラーハンドリング**
   - 適切な例外クラスを定義して使用
   - エラーメッセージは具体的で actionable に
   - コンテキストを提供し、解決策を提示する

5. **テスト**
   - 新機能には必ず対応するテストを追加
   - 単体テスト・プロパティベーステスト・統合テストを適切に使い分け
   - テストメソッド名は日本語で意図を明確に（例: `test_正常系_ユーザー登録が成功する`）

6. **パフォーマンス**
   - 新機能には適切なプロファイリング測定を追加
   - 性能要件が重要な場合はベンチマークテストを作成

7. **コミット前の確認**
   - `make check-all` でチェックをパス
   - テストがすべて通ることを確認

8. **GitHub操作**
   - イシュー作成時は `make issue`、PR作成時は `make pr` を使用


## トラブルシューティング

### よくある問題と解決策

#### 1. pre-commitが失敗する

```bash
# キャッシュをクリア
uv run pre-commit clean
uv run pre-commit gc

# 再インストール
uv run pre-commit uninstall
uv run pre-commit install
```

#### 2. mypyが大量のエラーを出す

```bash
# 特定のファイルだけチェック
uv run mypy src/knowledge_system/specific_module.py

# 型スタブのインストール
uv add --dev types-requests types-pyyaml
```

#### 3. GitHub ActionsでCIが失敗

```bash
# ローカルで同じ環境を再現
uv sync
uv run pytest
uv run mypy src/ --strict
uv run ruff check .
```

## 段階的な導入のベストプラクティス

### 初期設定を緩めに

- 最初はすべての厳密なチェックを有効にしない
- プロジェクトが成熟するにつれて徐々に厳しくする

### 継続的な改善

- 定期的にCLAUDE.mdを見直して更新
- 新しいベストプラクティスを追加

## 詳細ガイドの参照

以下の専用ガイドを必要に応じてインポートしてください。

### Claude Code協働戦略

@docs/claude-collaboration-guide.md をインポートしてください。

CLAUDE.mdやサブドキュメントの保守戦略に関する記述が主で、更新プロトコル、動的なルール追加、フィードバックループなどの説明があります。まずは必ずこのドキュメントを参照してください。

### プロジェクトタイプ別専用ガイド

プロジェクトの性質に応じて、以下の専用ガイドを動的にインポートできます：

#### 機械学習プロジェクト

機械学習プロジェクトの場合、@docs/ml-project-guide.md をインポートしてください。

このガイドには以下が含まれます：
- PyTorch, numpy, pandas の設定
- Weights & Biases (wandb) の統合手順
- Hydra による設定管理
- GPU環境の最適化
- 実験管理のベストプラクティス
- データバージョニング戦略

#### バックエンドAPI プロジェクト

FastAPI を使用したバックエンドプロジェクトの場合、@docs/backend-project-guide.md をインポートしてください。

このガイドには以下が含まれます：
- FastAPI + Pydantic の設定
- SQLAlchemy による非同期データベース操作
- JWT認証とセキュリティ設定
- API設計のベストプラクティス
- Docker開発環境
- プロダクション考慮事項

### カスタムガイドの追加

プロジェクト固有の要件に応じて、追加のガイドを`docs/` ディレクトリに作成できます。
例: フロントエンドプロジェクトのガイド(`docs/frontend-project-guide.md`), チーム固有のルール(`docs/team-specific-guide.md`)など
