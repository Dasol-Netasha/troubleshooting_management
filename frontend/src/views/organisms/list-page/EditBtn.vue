<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import EditIconBtn from '@/components/molecules/buttons/EditIconBtn.vue'

const props = defineProps({
  issueId: {
    type: [Number, String],
    default: null,
  },
})

const router = useRouter()

const normalizedIssueId = computed(() => {
  const parsed = Number(props.issueId)
  return Number.isInteger(parsed) && parsed > 0 ? parsed : null
})

const onClick = (event) => {
  event?.stopPropagation?.()

  if (!normalizedIssueId.value) {
    return
  }

  router.push({
    path: '/update',
    query: { issueId: String(normalizedIssueId.value) },
  })
}
</script>

<template>
  <EditIconBtn
    aria-label="수정"
    size="sm"
    outlined
    :disabled="!normalizedIssueId"
    @click="onClick"
  />
</template>
