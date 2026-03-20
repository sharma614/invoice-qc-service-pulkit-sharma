import axios from 'axios'

const client = axios.create({
  timeout: 10000,
})

export const validateJson = async (invoices) => {
  const response = await client.post('/validate-json', invoices)
  return response.data
}

export const extractAndValidatePdfs = async (files) => {
  const formData = new FormData()
  files.forEach(file => formData.append('files', file))
  const response = await client.post('/extract-and-validate-pdfs', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return response.data
}

export const checkHealth = async () => {
  const response = await client.get('/health')
  return response.data
}
