import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  MenuItem,
  FormControlLabel,
  Checkbox,
  Grid,
  Alert,
  Rating,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Save as SaveIcon,
} from '@mui/icons-material';
import { paperAPI } from '../lib/api';

interface PaperFormData {
  title: string;
  abstract: string;
  authors: string;
  journal: string;
  conference: string;
  publisher: string;
  publication_year: number | null;
  publication_date: string;
  volume: string;
  issue: string;
  pages: string;
  doi: string;
  arxiv_id: string;
  pmid: string;
  isbn: string;
  url: string;
  pdf_url: string;
  language: string;
  paper_type: string;
  personal_notes: string;
  rating: number | null;
  reading_status: string;
  priority: number;
  is_favorite: boolean;
  citation_count: number;
}

const initialFormData: PaperFormData = {
  title: '',
  abstract: '',
  authors: '',
  journal: '',
  conference: '',
  publisher: '',
  publication_year: null,
  publication_date: '',
  volume: '',
  issue: '',
  pages: '',
  doi: '',
  arxiv_id: '',
  pmid: '',
  isbn: '',
  url: '',
  pdf_url: '',
  language: 'en',
  paper_type: 'journal',
  personal_notes: '',
  rating: null,
  reading_status: 'to_read',
  priority: 3,
  is_favorite: false,
  citation_count: 0,
};

export const PaperCreatePage: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<PaperFormData>(initialFormData);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (field: keyof PaperFormData) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = event.target.value;
    setFormData(prev => ({
      ...prev,
      [field]: value === '' && (field === 'publication_year' || field === 'rating') ? null : value
    }));
  };

  const handleNumberChange = (field: 'publication_year' | 'priority' | 'citation_count') => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = event.target.value;
    setFormData(prev => ({
      ...prev,
      [field]: value === '' ? (field === 'publication_year' ? null : 0) : parseInt(value)
    }));
  };

  const handleRatingChange = (value: number | null) => {
    setFormData(prev => ({ ...prev, rating: value }));
  };

  const handleCheckboxChange = (field: 'is_favorite') => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData(prev => ({ ...prev, [field]: event.target.checked }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setError(null);

    try {
      // 空文字列をundefinedに変換してnullとして送信されるのを防ぐ
      const submitData = {
        title: formData.title,
        authors: formData.authors,
        abstract: formData.abstract || undefined,
        journal: formData.journal || undefined,
        conference: formData.conference || undefined,
        publisher: formData.publisher || undefined,
        publication_year: formData.publication_year || undefined,
        publication_date: formData.publication_date || undefined,
        volume: formData.volume || undefined,
        issue: formData.issue || undefined,
        pages: formData.pages || undefined,
        doi: formData.doi || undefined,
        arxiv_id: formData.arxiv_id || undefined,
        pmid: formData.pmid || undefined,
        isbn: formData.isbn || undefined,
        url: formData.url || undefined,
        pdf_url: formData.pdf_url || undefined,
        language: formData.language,
        paper_type: formData.paper_type,
        personal_notes: formData.personal_notes || undefined,
        rating: formData.rating || undefined,
        reading_status: formData.reading_status,
        priority: formData.priority,
        is_favorite: formData.is_favorite,
        citation_count: formData.citation_count,
        category_id: null,
        tag_ids: [],
      };

      const response = await paperAPI.create(submitData);
      navigate(`/papers/${response.data.id}`);
    } catch (error) {
      console.error('Failed to create paper:', error);
      setError('論文の作成に失敗しました');
    } finally {
      setSaving(false);
    }
  };

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
          <Typography variant="h4" component="h1">
            新しい論文を追加
          </Typography>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    基本情報
                  </Typography>

                  <Grid container spacing={2}>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="タイトル"
                        required
                        value={formData.title}
                        onChange={handleInputChange('title')}
                        multiline
                        rows={2}
                        placeholder="論文のタイトルを入力してください"
                      />
                    </Grid>

                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="著者"
                        required
                        value={formData.authors}
                        onChange={handleInputChange('authors')}
                        helperText="複数の著者はカンマで区切ってください"
                        placeholder="著者名をカンマ区切りで入力してください"
                      />
                    </Grid>

                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="アブストラクト"
                        value={formData.abstract}
                        onChange={handleInputChange('abstract')}
                        multiline
                        rows={4}
                        placeholder="論文の要約を入力してください"
                      />
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    出版情報
                  </Typography>

                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="論文種別"
                        select
                        value={formData.paper_type}
                        onChange={handleInputChange('paper_type')}
                      >
                        <MenuItem value="journal">ジャーナル</MenuItem>
                        <MenuItem value="conference">学会</MenuItem>
                        <MenuItem value="preprint">プレプリント</MenuItem>
                        <MenuItem value="thesis">論文</MenuItem>
                        <MenuItem value="book">書籍</MenuItem>
                      </TextField>
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="言語"
                        select
                        value={formData.language}
                        onChange={handleInputChange('language')}
                      >
                        <MenuItem value="en">英語</MenuItem>
                        <MenuItem value="ja">日本語</MenuItem>
                        <MenuItem value="zh">中国語</MenuItem>
                        <MenuItem value="fr">フランス語</MenuItem>
                        <MenuItem value="de">ドイツ語</MenuItem>
                        <MenuItem value="es">スペイン語</MenuItem>
                      </TextField>
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="ジャーナル名"
                        value={formData.journal}
                        onChange={handleInputChange('journal')}
                        placeholder="ジャーナル名を入力"
                      />
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="学会名"
                        value={formData.conference}
                        onChange={handleInputChange('conference')}
                        placeholder="学会名を入力"
                      />
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="出版社"
                        value={formData.publisher}
                        onChange={handleInputChange('publisher')}
                        placeholder="出版社名を入力"
                      />
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="発行年"
                        type="number"
                        value={formData.publication_year || ''}
                        onChange={handleNumberChange('publication_year')}
                        placeholder="例: 2023"
                        inputProps={{ min: 1900, max: new Date().getFullYear() + 5 }}
                      />
                    </Grid>

                    <Grid item xs={12} sm={4}>
                      <TextField
                        fullWidth
                        label="巻"
                        value={formData.volume}
                        onChange={handleInputChange('volume')}
                        placeholder="例: 15"
                      />
                    </Grid>

                    <Grid item xs={12} sm={4}>
                      <TextField
                        fullWidth
                        label="号"
                        value={formData.issue}
                        onChange={handleInputChange('issue')}
                        placeholder="例: 3"
                      />
                    </Grid>

                    <Grid item xs={12} sm={4}>
                      <TextField
                        fullWidth
                        label="ページ"
                        value={formData.pages}
                        onChange={handleInputChange('pages')}
                        placeholder="例: 1-10"
                      />
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    識別子・URL
                  </Typography>

                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="DOI"
                        value={formData.doi}
                        onChange={handleInputChange('doi')}
                        placeholder="例: 10.1000/182"
                      />
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="arXiv ID"
                        value={formData.arxiv_id}
                        onChange={handleInputChange('arxiv_id')}
                        placeholder="例: 1234.5678"
                      />
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="PubMed ID"
                        value={formData.pmid}
                        onChange={handleInputChange('pmid')}
                        placeholder="例: 12345678"
                      />
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="ISBN"
                        value={formData.isbn}
                        onChange={handleInputChange('isbn')}
                        placeholder="例: 978-0123456789"
                      />
                    </Grid>

                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="論文URL"
                        value={formData.url}
                        onChange={handleInputChange('url')}
                        type="url"
                        placeholder="https://example.com/paper"
                      />
                    </Grid>

                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="PDF URL"
                        value={formData.pdf_url}
                        onChange={handleInputChange('pdf_url')}
                        type="url"
                        placeholder="https://example.com/paper.pdf"
                      />
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    個人的評価・メモ
                  </Typography>

                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="読書ステータス"
                        select
                        value={formData.reading_status}
                        onChange={handleInputChange('reading_status')}
                      >
                        <MenuItem value="to_read">未読</MenuItem>
                        <MenuItem value="reading">読書中</MenuItem>
                        <MenuItem value="completed">読了</MenuItem>
                        <MenuItem value="skipped">スキップ</MenuItem>
                      </TextField>
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="優先度"
                        select
                        value={formData.priority}
                        onChange={handleNumberChange('priority')}
                      >
                        <MenuItem value={1}>1 (低)</MenuItem>
                        <MenuItem value={2}>2</MenuItem>
                        <MenuItem value={3}>3 (中)</MenuItem>
                        <MenuItem value={4}>4</MenuItem>
                        <MenuItem value={5}>5 (高)</MenuItem>
                      </TextField>
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <Box>
                        <Typography component="legend" gutterBottom>
                          評価
                        </Typography>
                        <Rating
                          value={formData.rating}
                          onChange={(_, value) => handleRatingChange(value)}
                          size="large"
                        />
                      </Box>
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="被引用数"
                        type="number"
                        value={formData.citation_count}
                        onChange={handleNumberChange('citation_count')}
                        inputProps={{ min: 0 }}
                        placeholder="0"
                      />
                    </Grid>

                    <Grid item xs={12}>
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={formData.is_favorite}
                            onChange={handleCheckboxChange('is_favorite')}
                          />
                        }
                        label="お気に入りに追加"
                      />
                    </Grid>

                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="個人的なメモ"
                        value={formData.personal_notes}
                        onChange={handleInputChange('personal_notes')}
                        multiline
                        rows={4}
                        placeholder="この論文についての個人的な感想やメモを記録できます"
                      />
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button
                  variant="outlined"
                  onClick={() => navigate('/papers')}
                  disabled={saving}
                >
                  キャンセル
                </Button>
                <Button
                  type="submit"
                  variant="contained"
                  startIcon={<SaveIcon />}
                  disabled={saving || !formData.title.trim() || !formData.authors.trim()}
                >
                  {saving ? '作成中...' : '論文を追加'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Box>
    </Container>
  );
};
