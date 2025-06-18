import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  CardActions,
  Button,
} from '@mui/material';
import {
  Article as ArticleIcon,
  Description as PaperIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

export const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  return (
    <Container>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          ようこそ、{user?.display_name || user?.email}さん
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Knowledge Systemで技術知見と研究論文を管理しましょう
        </Typography>
      </Box>

      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
        <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <ArticleIcon sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
                <Typography variant="h5" component="h2">
                  技術記事
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                技術的な知見やノウハウをマークダウン形式で記録・管理できます。
                タグやカテゴリで整理して、後から簡単に検索できます。
              </Typography>
            </CardContent>
            <CardActions>
              <Button
                size="small"
                startIcon={<AddIcon />}
                onClick={() => navigate('/articles/new')}
              >
                新規作成
              </Button>
              <Button size="small" onClick={() => navigate('/articles')}>
                一覧を見る
              </Button>
            </CardActions>
          </Card>

        <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <PaperIcon sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
                <Typography variant="h5" component="h2">
                  研究論文
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                読んだ論文のメタデータを管理し、PDFファイルを添付できます。
                著者、発表年、ジャーナルなどで整理できます。
              </Typography>
            </CardContent>
            <CardActions>
              <Button
                size="small"
                startIcon={<AddIcon />}
                onClick={() => navigate('/papers/new')}
              >
                新規登録
              </Button>
              <Button size="small" onClick={() => navigate('/papers')}>
                一覧を見る
              </Button>
            </CardActions>
          </Card>
      </Box>
    </Container>
  );
};
