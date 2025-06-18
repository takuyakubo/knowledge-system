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
  Grid,
  Divider,
} from '@mui/material';
import {
  Search as SearchIcon,
  Add as AddIcon,
  Edit as EditIcon,
  PictureAsPdf as PdfIcon,
  Launch as LaunchIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
} from '@mui/icons-material';
import { paperAPI } from '../lib/api';

interface Paper {
  id: number;
  title: string;
  abstract?: string;
  authors: string;
  journal?: string;
  conference?: string;
  publisher?: string;
  publication_year?: number;
  publication_date?: string;
  volume?: string;
  issue?: string;
  pages?: string;
  doi?: string;
  arxiv_id?: string;
  pmid?: string;
  isbn?: string;
  url?: string;
  pdf_url?: string;
  language: string;
  paper_type: string;
  personal_notes?: string;
  rating?: number;
  reading_status: string;
  priority: number;
  is_favorite: boolean;
  citation_count: number;
  category_id?: number;
  read_at?: string;
  created_at: string;
  updated_at: string;
}

export const PapersPage: React.FC = () => {
  const navigate = useNavigate();
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetchPapers();
  }, [search]);

  const fetchPapers = async () => {
    setLoading(true);
    try {
      const response = await paperAPI.list({ search });
      setPapers(response.data || []);
    } catch (error) {
      console.error('Failed to fetch papers:', error);
      setPapers([]); // エラー時は空配列に設定
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('この論文を削除しますか？')) {
      try {
        await paperAPI.delete(id);
        fetchPapers();
      } catch (error) {
        console.error('Failed to delete paper:', error);
      }
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ja-JP');
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'reading': return 'warning';
      case 'to_read': return 'default';
      case 'skipped': return 'error';
      default: return 'default';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'completed': return '読了';
      case 'reading': return '読書中';
      case 'to_read': return '未読';
      case 'skipped': return 'スキップ';
      default: return status;
    }
  };

  const getPaperTypeLabel = (type: string) => {
    switch (type) {
      case 'journal': return 'ジャーナル';
      case 'conference': return '学会';
      case 'preprint': return 'プレプリント';
      case 'thesis': return '論文';
      case 'book': return '書籍';
      default: return type;
    }
  };

  const renderAuthors = (authors: string) => {
    const authorList = authors.split(',').map(author => author.trim());
    if (authorList.length > 3) {
      return `${authorList.slice(0, 3).join(', ')} et al.`;
    }
    return authorList.join(', ');
  };

  const renderPublicationInfo = (paper: Paper) => {
    const parts = [];
    if (paper.journal) parts.push(paper.journal);
    if (paper.conference) parts.push(paper.conference);
    if (paper.volume) parts.push(`Vol. ${paper.volume}`);
    if (paper.issue) parts.push(`No. ${paper.issue}`);
    if (paper.pages) parts.push(`pp. ${paper.pages}`);
    if (paper.publication_year) parts.push(`(${paper.publication_year})`);
    return parts.join(', ');
  };

  return (
    <Container>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          研究論文
        </Typography>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="論文を検索..."
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
      ) : papers.length === 0 ? (
        <Box display="flex" justifyContent="center" p={4}>
          <Typography variant="h6" color="text.secondary">
            {search ? '検索結果がありません' : '論文がまだありません'}
          </Typography>
        </Box>
      ) : (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {papers.map((paper) => (
            <Card key={paper.id}>
              <CardContent>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={8}>
                    <Typography variant="h6" component="h2" gutterBottom>
                      {paper.title}
                    </Typography>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ mb: 1 }}
                    >
                      著者: {renderAuthors(paper.authors)}
                    </Typography>
                    {renderPublicationInfo(paper) && (
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ mb: 1 }}
                      >
                        {renderPublicationInfo(paper)}
                      </Typography>
                    )}
                    {paper.abstract && (
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ mt: 1, mb: 1 }}
                      >
                        {paper.abstract.length > 200
                          ? `${paper.abstract.substring(0, 200)}...`
                          : paper.abstract
                        }
                      </Typography>
                    )}
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        <Chip
                          label={getStatusLabel(paper.reading_status)}
                          size="small"
                          color={getStatusColor(paper.reading_status)}
                        />
                        <Chip
                          label={getPaperTypeLabel(paper.paper_type)}
                          size="small"
                          variant="outlined"
                        />
                        {paper.is_favorite && (
                          <Chip
                            icon={<StarIcon />}
                            label="お気に入り"
                            size="small"
                            color="warning"
                          />
                        )}
                      </Box>
                      {paper.rating && (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <Typography variant="caption">評価:</Typography>
                          {[...Array(5)].map((_, i) => (
                            i < paper.rating! ? (
                              <StarIcon key={i} fontSize="small" color="warning" />
                            ) : (
                              <StarBorderIcon key={i} fontSize="small" />
                            )
                          ))}
                        </Box>
                      )}
                      <Typography variant="caption" color="text.secondary">
                        優先度: {paper.priority}/5
                      </Typography>
                      {paper.citation_count > 0 && (
                        <Typography variant="caption" color="text.secondary">
                          被引用数: {paper.citation_count}
                        </Typography>
                      )}
                    </Box>
                  </Grid>
                </Grid>
                <Divider sx={{ my: 2 }} />
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {paper.doi && (
                    <Chip
                      label={`DOI: ${paper.doi}`}
                      size="small"
                      variant="outlined"
                      clickable
                      onClick={() => window.open(`https://doi.org/${paper.doi}`, '_blank')}
                    />
                  )}
                  {paper.arxiv_id && (
                    <Chip
                      label={`arXiv: ${paper.arxiv_id}`}
                      size="small"
                      variant="outlined"
                      clickable
                      onClick={() => window.open(`https://arxiv.org/abs/${paper.arxiv_id}`, '_blank')}
                    />
                  )}
                </Box>
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  作成日: {formatDate(paper.created_at)} | 更新日: {formatDate(paper.updated_at)}
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" onClick={() => navigate(`/papers/${paper.id}`)}>
                  詳細を見る
                </Button>
                <Button
                  size="small"
                  startIcon={<EditIcon />}
                  onClick={() => navigate(`/papers/${paper.id}/edit`)}
                >
                  編集
                </Button>
                {paper.pdf_url && (
                  <Button
                    size="small"
                    startIcon={<PdfIcon />}
                    onClick={() => window.open(paper.pdf_url, '_blank')}
                  >
                    PDF
                  </Button>
                )}
                {paper.url && (
                  <Button
                    size="small"
                    startIcon={<LaunchIcon />}
                    onClick={() => window.open(paper.url, '_blank')}
                  >
                    外部リンク
                  </Button>
                )}
                <Button size="small" color="error" onClick={() => handleDelete(paper.id)}>
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
        onClick={() => navigate('/papers/new')}
      >
        <AddIcon />
      </Fab>
    </Container>
  );
};
