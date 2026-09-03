import { ref } from 'vue'
import { defineStore } from 'pinia'

import { issueService } from '@/services/issueService'

export const useIssueListStore = defineStore('issueList', () => {
  const fields = ref([])
  const rows = ref([])
  const optionsMap = ref({})
  const totalCount = ref(0)
  const loading = ref(false)
  const errorMessage = ref('')

  const fetchListPageData = async (filters = {}) => {
    loading.value = true
    errorMessage.value = ''

    try {
      const data = await issueService.getListPageData({
        filters: JSON.stringify(filters || {}),
      })

      fields.value = Array.isArray(data?.fields) ? data.fields : []
      rows.value = Array.isArray(data?.rows) ? data.rows : []
      optionsMap.value = data?.options_map && typeof data.options_map === 'object' ? data.options_map : {}
      const responseTotal = Number(data?.total_count)
      totalCount.value = Number.isFinite(responseTotal) ? responseTotal : rows.value.length
      return data
    } catch (error) {
      errorMessage.value = '이슈 목록 데이터를 불러오지 못했습니다.'
      throw error
    } finally {
      loading.value = false
    }
  }

  const removeIssueById = (issueId) => {
    const numericId = Number(issueId)
    if (!Number.isInteger(numericId) || numericId <= 0) {
      return
    }

    rows.value = rows.value.filter((row) => Number(row?.issue_id) !== numericId)
    totalCount.value = rows.value.length
  }

  return {
    fields,
    rows,
    optionsMap,
    totalCount,
    loading,
    errorMessage,
    fetchListPageData,
    removeIssueById,
  }
})