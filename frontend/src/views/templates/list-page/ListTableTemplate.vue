<script setup>
import DataTable from '@/components/organisms/table/DataTable.vue'
import { useRouter } from 'vue-router'
import { useIssueListPage } from '@/composables/shared/useIssueListPage'

const { loading, errorMessage, totalCount, tableColumns, tableRows } = useIssueListPage()
const router = useRouter()

const onRowClick = (row) => {
  const issueId = Number(row?.issue_id)
  if (!Number.isInteger(issueId) || issueId <= 0) {
    return
  }
  router.push(`/detail/${issueId}`)
}
</script>

<template>
  <section class="space-y-3 rounded-xl border border-slate-200 bg-white p-4">
    <header class="flex items-center justify-between gap-2">
      <h2 class="text-sm font-semibold text-slate-800">이슈 목록</h2>
      <p class="text-xs text-slate-500">총 {{ totalCount }}건</p>
    </header>

    <p v-if="errorMessage" class="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
      {{ errorMessage }}
    </p>

    <DataTable
      :columns="tableColumns"
      :rows="tableRows"
      row-key="issue_id"
      :loading="loading"
      empty-text="표시할 이슈가 없습니다."
      sortable
      clickable-rows
      @row-click="onRowClick"
    />
  </section>
</template>