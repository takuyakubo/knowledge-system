import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  TextField,
  InputAdornment,
  CircularProgress,
  Fab,
} from '@mui/material';
import {
  Search as SearchIcon,
  Add as AddIcon,
  Edit as EditIcon,
} from '@mui/icons-material';
import { articleAPI } from '../lib/api';

interface Article {
  id: number;
  title: string;
  summary?: string;
  content: string;
  slug: string;
  status: string;
  meta_description?: string;
  featured_image_url?: string;
  is_public: boolean;
  category_id?: number;
  published_at?: string;
  view_count: number;
  like_count: number;
  created_at: string;
  updated_at: string;
}

export const ArticlesPage: React.FC = () => {
  const navigate = useNavigate();
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetchArticles();
  }, [search]);

  const fetchArticles = async () => {
    setLoading(true);
    try {
      const response = await articleAPI.list({ search });
      setArticles(response.data || []);
    } catch (error) {
      console.error('Failed to fetch articles:', error);
      setArticles([]); // エラー時は空配列に設定
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('この記事を削除しますか？')) {
      try {
        await articleAPI.delete(id);
        fetchArticles();
      } catch (error) {
        console.error('Failed to delete article:', error);
      }
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ja-JP');
  };

  return (
    <Container>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          技術記事
        </Typography>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="記事を検索..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
      </Box>

      {loading ? (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      ) : articles.length === 0 ? (
        <Box display="flex" justifyContent="center" p={4}>
          <Typography variant="h6" color="text.secondary">
            {search ? '検索結果がありません' : '記事がまだありません'}
          </Typography>
        </Box>
      ) : (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {articles.map((article) => (
            <Card key={article.id}>
                <CardContent>
                  <Typography variant="h6" component="h2" gutterBottom>
                    {article.title}
                  </Typography>
                  <Box sx={{ mb: 1 }}>
                    <Chip
                      label={article.status}
                      size="small"
                      color={article.status === 'published' ? 'success' : 'default'}
                      sx={{ mr: 1 }}
                    />
                    {article.is_public && (
                      <Chip
                        label="公開"
                        size="small"
                        color="primary"
                        sx={{ mr: 1 }}
                      />
                    )}
                    <Chip
                      label={`${article.view_count} views`}
                      size="small"
                      variant="outlined"
                      sx={{ mr: 1 }}
                    />
                  </Box>
                  {article.summary && (
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ mt: 1, mb: 1 }}
                    >
                      {article.summary}
                    </Typography>
                  )}
                  <Typography variant="caption" color="text.secondary">
                    作成日: {formatDate(article.created_at)} | 更新日: {formatDate(article.updated_at)}
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button size="small" onClick={() => navigate(`/articles/${article.id}`)}>
                    詳細を見る
                  </Button>
                  <Button
                    size="small"
                    startIcon={<EditIcon />}
                    onClick={() => navigate(`/articles/${article.id}/edit`)}
                  >
                    編集
                  </Button>
                  <Button size="small" color="error" onClick={() => handleDelete(article.id)}>
                    削除
                  </Button>
                </CardActions>
              </Card>
          ))}
        </Box>
      )}

      <Fab
        color="primary"
        aria-label="add"
        sx={{ position: 'fixed', bottom: 24, right: 24 }}
        onClick={() => navigate('/articles/new')}
      >
        <AddIcon />
      </Fab>
    </Container>
  );
};
