<script setup>
import { computed } from 'vue'
import DeleteIconBtn from '@/components/molecules/buttons/DeleteIconBtn.vue'
import { useIssueListStore } from '@/stores/issueListStore'
import { issueService } from '@/services/issueService'

const props = defineProps({
  issueId: {
    type: [Number, String],
    default: null,
  },
})

const issueListStore = useIssueListStore()

const normalizedIssueId = computed(() => {
  const parsed = Number(props.issueId)
  return Number.isInteger(parsed) && parsed > 0 ? parsed : null
})

const onClick = async (event) => {
  event?.stopPropagation?.()

  if (!normalizedIssueId.value) {
    return
  }

  const confirmed = window.confirm(`이슈 #${normalizedIssueId.value}를 삭제하시겠습니까?`)
  if (!confirmed) {
    return
  }

  try {
    await issueService.deleteIssue(normalizedIssueId.value)
    issueListStore.removeIssueById(normalizedIssueId.value)
  } catch (error) {
    window.alert('삭제에 실패했습니다.')
  }
}
</script>

<template>
  <DeleteIconBtn
    aria-label="삭제"
    size="sm"
    outlined
    :disabled="!normalizedIssueId"
    @click="onClick"
  />
</template>
