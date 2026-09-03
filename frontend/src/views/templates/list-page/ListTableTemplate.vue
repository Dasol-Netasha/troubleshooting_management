<script setup>
import { computed } from 'vue'
import DataTable from '@/components/organisms/table/DataTable.vue'
import PaginationBar from '@/components/organisms/pagination/PaginationBar.vue'
import { useRouter } from 'vue-router'
import { useIssueListPage } from '@/composables/shared/useIssueListPage'
import AddBtn from '@/views/organisms/list-page/AddBtn.vue'
import EditBtn from '@/views/organisms/list-page/EditBtn.vue'
import DeleteBtn from '@/views/organisms/list-page/DeleteBtn.vue'

const {
  loading,
  errorMessage,
  totalCount,
  tableColumns,
  pagedTableRows,
  currentPage,
  pageSize,
  totalPages,
  pageSizeOptions,
  setCurrentPage,
  setPageSize,
} = useIssueListPage()
const router = useRouter()

const tableColumnsWithActions = computed(() => {
  return [
    ...tableColumns.value,
    {
      key: '__actions',
      label: '작업',
      sortable: false,
      align: 'center',
    },
  ]
})

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
      <div class="flex items-center gap-2">
        <p class="text-xs text-slate-500">총 {{ totalCount }}건</p>
        <AddBtn />
      </div>
    </header>

    <p v-if="errorMessage" class="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
      {{ errorMessage }}
    </p>

    <DataTable
      :columns="tableColumnsWithActions"
      :rows="pagedTableRows"
      row-key="issue_id"
      :loading="loading"
      empty-text="표시할 이슈가 없습니다."
      sortable
      clickable-rows
      @row-click="onRowClick"
    >
      <template #cell-approval_yn="{ value }">
        <span
          class="inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold"
          :style="value === '승인완료'
            ? 'background: var(--theme-primary-bg); color: var(--theme-primary-text);'
            : 'background: var(--theme-danger-bg); color: var(--theme-danger-text);'"
        >
          {{ value || '미승인' }}
        </span>
      </template>

      <template #cell-__actions="{ row }">
        <div class="flex items-center justify-center gap-2">
          <EditBtn :issue-id="row.issue_id" />
          <DeleteBtn :issue-id="row.issue_id" />
        </div>
      </template>
    </DataTable>

    <PaginationBar
      v-if="totalCount > 0"
      :page="currentPage"
      :page-size="pageSize"
      :total="totalCount"
      :total-pages="totalPages"
      :page-size-options="pageSizeOptions"
      :loading="loading"
      @update:page="setCurrentPage"
      @update:page-size="setPageSize"
    />
  </section>
</template>