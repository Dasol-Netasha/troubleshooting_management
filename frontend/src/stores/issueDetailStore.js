import { ref } from 'vue'
import { defineStore } from 'pinia'

import { issueService } from '@/services/issueService'

export const useIssueDetailStore = defineStore('issueDetail', () => {
  const issueId = ref(null)
  const fields = ref([])
  const images = ref([])
  const loading = ref(false)
  const errorMessage = ref('')

  const fetchIssueDetail = async (targetIssueId) => {
    loading.value = true
    errorMessage.value = ''

    try {
      const data = await issueService.getDetail(targetIssueId)
      issueId.value = Number(data?.issue_id || targetIssueId)
      fields.value = Array.isArray(data?.fields) ? data.fields : []
      images.value = Array.isArray(data?.images) ? data.images : []
      return data
    } catch (error) {
      errorMessage.value = '이슈 상세 데이터를 불러오지 못했습니다.'
      throw error
    } finally {
      loading.value = false
    }
  }

  const approveIssue = async (targetIssueId, payload = {}) => {
    const data = await issueService.approveIssue(targetIssueId, payload)
    await fetchIssueDetail(targetIssueId)
    return data
  }

  const setErrorMessage = (message) => {
    errorMessage.value = String(message || '')
  }

  return {
    issueId,
    fields,
    images,
    loading,
    errorMessage,
    fetchIssueDetail,
    approveIssue,
    setErrorMessage,
  }
})