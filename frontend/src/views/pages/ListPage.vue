<script setup>
import { onMounted } from 'vue'

import { useIssueListPage } from '@/composables/shared/useIssueListPage'
import FilterTemplate from '@/views/templates/list-page/FilterTemplate.vue'
import ListTableTemplate from '@/views/templates/list-page/ListTableTemplate.vue'

const { load } = useIssueListPage()

onMounted(async () => {
  try {
    await load()
  } catch {
    // Error state is handled by the shared store/composable.
  }
})
</script>

<template>
  <section class="space-y-4">
    <FilterTemplate />
    <ListTableTemplate />
  </section>
</template>