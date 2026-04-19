import axios from 'axios'

/**
 * @typedef {Object} LineItem
 * @property {string} description
 * @property {number} [quantity]
 * @property {number} [unit_price]
 * @property {number} [line_total]
 */

/**
 * @typedef {Object} Invoice
 * @property {string} [invoice_number]
 * @property {string} [external_reference]
 * @property {string} [seller_name]
 * @property {string} [buyer_name]
 * @property {string} [invoice_date]
 * @property {string} [due_date]
 * @property {string} [currency]
 * @property {number} [net_total]
 * @property {number} [tax_amount]
 * @property {number} [gross_total]
 * @property {LineItem[]} [line_items]
 */

/**
 * @typedef {Object} QCResult
 * @property {string} invoice_id
 * @property {boolean} is_valid
 * @property {string[]} errors
 */

/**
 * @typedef {Object} QCSummary
 * @property {number} total_invoices
 * @property {number} valid_invoices
 * @property {number} invalid_invoices
 * @property {Object.<string, number>} error_counts
 */

/**
 * @typedef {Object} QCResponse
 * @property {QCResult[]} results
 * @property {QCSummary} summary
 */

const client = axios.create({
  timeout: 30000, // Increased timeout for PDF extraction
})

/**
 * Validates a list of invoices via JSON.
 * @param {Invoice[]} invoices 
 * @returns {Promise<QCResponse>}
 */
export const validateJson = async (invoices) => {
  const response = await client.post('/validate-json', invoices)
  return response.data
}

/**
 * Uploads PDFs for extraction and validation.
 * @param {File[]} files 
 * @returns {Promise<QCResponse>}
 */
export const extractAndValidatePdfs = async (files) => {
  const formData = new FormData()
  files.forEach(file => formData.append('files', file))
  const response = await client.post('/extract-and-validate-pdfs', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return response.data
}

/**
 * Checks backend health status.
 * @returns {Promise<{status: string}>}
 */
export const checkHealth = async () => {
  const response = await client.get('/health')
  return response.data
}
