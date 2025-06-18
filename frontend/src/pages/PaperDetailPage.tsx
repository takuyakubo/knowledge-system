import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Chip,
  Divider,
  Grid,
  Paper,
  IconButton,
  Tooltip,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  PictureAsPdf as PdfIcon,
  Launch as LaunchIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
  Favorite as FavoriteIcon,
  FavoriteBorder as FavoriteBorderIcon,
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

export const PaperDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [paper, setPaper] = useState<Paper | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      fetchPaper(parseInt(id));
    }
  }, [id]);

  const fetchPaper = async (paperId: number) => {
    setLoading(true);
    setError(null);
    try {
      const response = await paperAPI.getById(paperId);
      setPaper(response.data);
    } catch (error) {
      console.error('Failed to fetch paper:', error);
      setError('論文の取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!paper) return;

    if (window.confirm('この論文を削除しますか？この操作は取り消せません。')) {
      try {
        await paperAPI.delete(paper.id);
        navigate('/papers');
      } catch (error) {
        console.error('Failed to delete paper:', error);
        setError('論文の削除に失敗しました');
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

  const renderPublicationInfo = (paper: Paper) => {
    const parts = [];
    if (paper.journal) parts.push(paper.journal);
    if (paper.conference) parts.push(paper.conference);
    if (paper.publisher) parts.push(paper.publisher);
    if (paper.volume) parts.push(`Vol. ${paper.volume}`);
    if (paper.issue) parts.push(`No. ${paper.issue}`);
    if (paper.pages) parts.push(`pp. ${paper.pages}`);
    if (paper.publication_year) parts.push(`(${paper.publication_year})`);
    return parts.join(', ');
  };

  if (loading) {
    return (
      <Container>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Box sx={{ mt: 3 }}>
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate('/papers')}
          >
            論文一覧に戻る
          </Button>
        </Box>
      </Container>
    );
  }

  if (!paper) {
    return (
      <Container>
        <Box sx={{ mt: 3 }}>
          <Alert severity="warning" sx={{ mb: 2 }}>
            論文が見つかりません
          </Alert>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate('/papers')}
          >
            論文一覧に戻る
          </Button>
        </Box>
      </Container>
    );
  }

  return (
    <Container>
      <Box sx={{ mt: 3, mb: 3 }}>
        {/* Header */}
        <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate('/papers')}
            variant="outlined"
          >
            戻る
          </Button>
          <Box sx={{ flex: 1 }}>
            <Typography variant="h4" component="h1">
              論文詳細
            </Typography>
          </Box>
          <Button
            startIcon={<EditIcon />}
            onClick={() => navigate(`/papers/${paper.id}/edit`)}
            variant="contained"
            color="primary"
          >
            編集
          </Button>
          <Button
            startIcon={<DeleteIcon />}
            onClick={handleDelete}
            variant="outlined"
            color="error"
          >
            削除
          </Button>
        </Box>

        {/* Main Content */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                {/* Title and Basic Info */}
                <Typography variant="h5" component="h2" gutterBottom>
                  {paper.title}
                </Typography>

                <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
                  {paper.authors}
                </Typography>

                {renderPublicationInfo(paper) && (
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {renderPublicationInfo(paper)}
                  </Typography>
                )}

                <Divider sx={{ my: 2 }} />

                {/* Abstract */}
                {paper.abstract && (
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="h6" gutterBottom>
                      アブストラクト
                    </Typography>
                    <Paper sx={{ p: 2, backgroundColor: 'grey.50' }}>
                      <Typography variant="body1" style={{ whiteSpace: 'pre-wrap' }}>
                        {paper.abstract}
                      </Typography>
                    </Paper>
                  </Box>
                )}

                {/* Personal Notes */}
                {paper.personal_notes && (
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="h6" gutterBottom>
                      個人的なメモ
                    </Typography>
                    <Paper sx={{ p: 2, backgroundColor: 'blue.50' }}>
                      <Typography variant="body1" style={{ whiteSpace: 'pre-wrap' }}>
                        {paper.personal_notes}
                      </Typography>
                    </Paper>
                  </Box>
                )}

                {/* External Links */}
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    外部リンク
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {paper.pdf_url && (
                      <Button
                        startIcon={<PdfIcon />}
                        variant="outlined"
                        onClick={() => window.open(paper.pdf_url, '_blank')}
                      >
                        PDF
                      </Button>
                    )}
                    {paper.url && (
                      <Button
                        startIcon={<LaunchIcon />}
                        variant="outlined"
                        onClick={() => window.open(paper.url, '_blank')}
                      >
                        外部リンク
                      </Button>
                    )}
                    {paper.doi && (
                      <Button
                        startIcon={<LaunchIcon />}
                        variant="outlined"
                        onClick={() => window.open(`https://doi.org/${paper.doi}`, '_blank')}
                      >
                        DOI
                      </Button>
                    )}
                    {paper.arxiv_id && (
                      <Button
                        startIcon={<LaunchIcon />}
                        variant="outlined"
                        onClick={() => window.open(`https://arxiv.org/abs/${paper.arxiv_id}`, '_blank')}
                      >
                        arXiv
                      </Button>
                    )}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            {/* Status and Metadata */}
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  ステータス
                </Typography>

                <Box sx={{ mb: 2 }}>
                  <Chip
                    label={getStatusLabel(paper.reading_status)}
                    color={getStatusColor(paper.reading_status)}
                    sx={{ mb: 1, mr: 1 }}
                  />
                  <Chip
                    label={getPaperTypeLabel(paper.paper_type)}
                    variant="outlined"
                    sx={{ mb: 1 }}
                  />
                </Box>

                {/* Rating */}
                {paper.rating && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      評価
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      {[...Array(5)].map((_, i) => (
                        i < paper.rating! ? (
                          <StarIcon key={i} color="warning" />
                        ) : (
                          <StarBorderIcon key={i} />
                        )
                      ))}
                      <Typography variant="body2" sx={{ ml: 1 }}>
                        ({paper.rating}/5)
                      </Typography>
                    </Box>
                  </Box>
                )}

                {/* Priority */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    優先度
                  </Typography>
                  <Typography variant="body2">
                    {paper.priority}/5
                  </Typography>
                </Box>

                {/* Favorite */}
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {paper.is_favorite ? (
                      <FavoriteIcon color="error" />
                    ) : (
                      <FavoriteBorderIcon />
                    )}
                    <Typography variant="subtitle2">
                      {paper.is_favorite ? 'お気に入り' : 'お気に入りではない'}
                    </Typography>
                  </Box>
                </Box>

                {/* Citation Count */}
                {paper.citation_count > 0 && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      被引用数
                    </Typography>
                    <Typography variant="body2">
                      {paper.citation_count.toLocaleString()}
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>

            {/* Metadata */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  メタデータ
                </Typography>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  {paper.doi && (
                    <Box>
                      <Typography variant="subtitle2">DOI:</Typography>
                      <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
                        {paper.doi}
                      </Typography>
                    </Box>
                  )}

                  {paper.arxiv_id && (
                    <Box>
                      <Typography variant="subtitle2">arXiv ID:</Typography>
                      <Typography variant="body2">
                        {paper.arxiv_id}
                      </Typography>
                    </Box>
                  )}

                  {paper.pmid && (
                    <Box>
                      <Typography variant="subtitle2">PubMed ID:</Typography>
                      <Typography variant="body2">
                        {paper.pmid}
                      </Typography>
                    </Box>
                  )}

                  {paper.isbn && (
                    <Box>
                      <Typography variant="subtitle2">ISBN:</Typography>
                      <Typography variant="body2">
                        {paper.isbn}
                      </Typography>
                    </Box>
                  )}

                  <Box>
                    <Typography variant="subtitle2">言語:</Typography>
                    <Typography variant="body2">
                      {paper.language === 'en' ? '英語' : paper.language}
                    </Typography>
                  </Box>

                  <Box>
                    <Typography variant="subtitle2">作成日:</Typography>
                    <Typography variant="body2">
                      {formatDate(paper.created_at)}
                    </Typography>
                  </Box>

                  <Box>
                    <Typography variant="subtitle2">更新日:</Typography>
                    <Typography variant="body2">
                      {formatDate(paper.updated_at)}
                    </Typography>
                  </Box>

                  {paper.read_at && (
                    <Box>
                      <Typography variant="subtitle2">読了日:</Typography>
                      <Typography variant="body2">
                        {formatDate(paper.read_at)}
                      </Typography>
                    </Box>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};
