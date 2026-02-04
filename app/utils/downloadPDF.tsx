import { memorialsAPI, willsAPI } from '../services/api'

export const downloadMemorialPDF = async (id: number, title: string) => {
  try {
    const response = await memorialsAPI.getPDF(id)
    
    // Create blob from response
    const blob = new Blob([response.data], { type: 'application/pdf' })
    
    // Create download link
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `memorial_${title.replace(/\s+/g, '_')}.pdf`
    
    // Trigger download
    document.body.appendChild(link)
    link.click()
    
    // Cleanup
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    return true
  } catch (error) {
    console.error('Error downloading PDF:', error)
    return false
  }
}

export const downloadWillPDF = async (id: number, title: string) => {
  try {
    const response = await willsAPI.getPDF(id)
    
    const blob = new Blob([response.data], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `will_${title.replace(/\s+/g, '_')}.pdf`
    
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    return true
  } catch (error) {
    console.error('Error downloading PDF:', error)
    return false
  }
}