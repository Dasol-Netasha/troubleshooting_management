import { computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'

import { useIssueDetailStore } from '@/stores/issueDetailStore'

export const useIssueDetailPage = () => {
  const route = useRoute()
  const issueDetailStore = useIssueDetailStore()
  const { loading, errorMessage, fields, images } = storeToRefs(issueDetailStore)

  const issueId = computed(() => Number(route.params.issueId || 0))
  const validIssueId = computed(() => Number.isInteger(issueId.value) && issueId.value > 0)

  const load = async () => {
    if (!validIssueId.value) {
      issueDetailStore.setErrorMessage('유효하지 않은 이슈 ID입니다.')
      return
    }

    await issueDetailStore.fetchIssueDetail(issueId.value)
  }

  watch(
    issueId,
    async () => {
      await load()
    },
    { immediate: true },
  )

  return {
    issueId,
    validIssueId,
    loading,
    errorMessage,
    detailFields: fields,
    detailImages: images,
    load,
  }
}