import { useEffect, useState } from 'react'
import { Box, Card, CardContent, Typography, Grid, CircularProgress, Alert } from '@mui/material'
import { apiClient } from '@/services/api'

export default function HomePage() {
  const [health, setHealth] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const response = await apiClient.get('/health')
        setHealth(response.data)
      } catch (err) {
        setError('无法连接到后端服务')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchHealth()
  }, [])

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 300 }}>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box>
      <Typography variant="h4" component="h1" sx={{ mb: 3 }}>
        欢迎使用办公助手Agent
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {health && (
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  系统状态
                </Typography>
                <Typography variant="h5">
                  {health.status === 'ok' ? '✓ 运行中' : '✗ 离线'}
                </Typography>
                <Typography variant="body2" sx={{ mt: 1 }}>
                  版本: {health.version}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          核心功能模块
        </Typography>
        <Grid container spacing={2}>
          {[
            { title: '会议纪要处理', desc: '自动处理会议音频/文字，生成结构化纪要' },
            { title: '文献摘要提取', desc: '快速提取学术论文和文献的核心要点' },
            { title: '学术文献润色', desc: '提升学术写作的规范性和表达质量' },
            { title: '多语言处理', desc: '支持跨语言的翻译和润色服务' },
            { title: 'PPT智能生成', desc: '从内容自动生成专业演示文稿' },
            { title: '实习周报生成', desc: '智能化生成周报，记录实习进度' }
          ].map((feature, idx) => (
            <Grid item xs={12} sm={6} md={4} key={idx}>
              <Card>
                <CardContent>
                  <Typography variant="h6">{feature.title}</Typography>
                  <Typography variant="body2" color="textSecondary">
                    {feature.desc}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Box>
  )
}
