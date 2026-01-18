import { Box, Typography } from '@mui/material'

export default function NotFound() {
  return (
    <Box sx={{ textAlign: 'center', py: 8 }}>
      <Typography variant="h3" gutterBottom>
        404 - 页面不存在
      </Typography>
      <Typography variant="body1" color="textSecondary">
        请检查URL是否正确
      </Typography>
    </Box>
  )
}
