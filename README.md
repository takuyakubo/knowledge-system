# Knowledge Management System

個人的な技術知見と研究論文を管理するためのWebアプリケーションです。

## 機能

- **記事管理**: マークダウン形式での技術記事の作成・編集・管理
- **論文管理**: 研究論文のメタデータ管理とファイル添付
- **検索・分類**: タグ・カテゴリによる分類と検索機能
- **ファイル添付**: PDFなどのファイル添付機能

## 技術スタック

### バックエンド
- Python FastAPI
- SQLAlchemy + PostgreSQL
- Alembic (マイグレーション)

### フロントエンド
- React 18 + TypeScript
- Material-UI (MUI)
- Monaco Editor (マークダウンエディタ)

### インフラ
- Docker & Docker Compose

## クイックスタート

```bash
# リポジトリのクローン
git clone https://github.com/takuyakubo/knowledge-management-system.git
cd knowledge-management-system

# 環境変数の設定
cp .env.example .env

# アプリケーションの起動
docker-compose up -d

# データベースマイグレーション
docker-compose exec backend alembic upgrade head
```

## アクセス

- **フロントエンド**: http://localhost:3000
- **API**: http://localhost:8000
- **API文書**: http://localhost:8000/docs

## 開発

### ローカル開発環境

**バックエンド:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**フロントエンド:**
```bash
cd frontend
npm install
npm start
```

### データベースマイグレーション

```bash
cd backend
alembic revision --autogenerate -m "migration message"
alembic upgrade head
```

## プロジェクト構造

```
knowledge-management-system/
├── backend/              # FastAPI アプリケーション
│   ├── app/
│   │   ├── api/         # REST API エンドポイント
│   │   ├── models/      # SQLAlchemy モデル
│   │   ├── services/    # ビジネスロジック
│   │   └── core/        # 設定・DB接続
│   └── alembic/         # マイグレーション
├── frontend/            # React アプリケーション
│   └── src/
│       ├── components/  # UIコンポーネント
│       ├── pages/       # ページコンポーネント
│       └── services/    # API クライアント
└── docker-compose.yml  # 開発環境
```

## API

詳細なAPI仕様は http://localhost:8000/docs で確認できます。

### 主要エンドポイント

- `GET /api/v1/articles/` - 記事一覧
- `POST /api/v1/articles/` - 記事作成
- `GET /api/v1/papers/` - 論文一覧
- `POST /api/v1/files/upload` - ファイルアップロード
- `GET /api/v1/search/` - 検索

## 将来の機能拡張

- Elasticsearch による全文検索
- 認証・認可システム
- PDFテキスト抽出
- エクスポート機能
- タグ階層化

## ライセンス

This project is private and for personal use only.
