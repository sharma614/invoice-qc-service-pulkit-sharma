import { useState } from 'react'
import * as api from '../api/client'

/**
 * Hook for managing invoice-related operations (upload and manual validation).
 * Provides loading, error, and result states.
 */
export function useInvoiceOps() {
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)

  const clear = () => {
    setResults(null)
    setError(null)
    setLoading(false)
  }

  /**
   * Validates raw JSON invoices.
   * @param {import('../api/client').Invoice[]} invoices
   */
  const validateManual = async (invoices) => {
    setLoading(true)
    setError(null)
    setResults(null)
    try {
      const data = await api.validateJson(invoices)
      setResults(data)
      return data
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Validation service error.'
      setError(msg)
      throw err
    } finally {
      setLoading(false)
    }
  }

  /**
   * Extracts and validates PDF files.
   * @param {File[]} files
   */
  const processPdfs = async (files) => {
    setLoading(true)
    setError(null)
    setResults(null)
    try {
      const data = await api.extractAndValidatePdfs(files)
      setResults(data)
      return data
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Extraction failed.'
      setError(msg)
      throw err
    } finally {
      setLoading(false)
    }
  }

  return {
    loading,
    results,
    error,
    clear,
    validateManual,
    processPdfs
  }
}
