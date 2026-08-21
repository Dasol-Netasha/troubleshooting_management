<script setup>
import DataTable from '@/components/organisms/table/DataTable.vue'

defineProps({
  columns: {
    type: Array,
    default: () => [],
  },
  rows: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
  totalCount: {
    type: Number,
    default: 0,
  },
})
</script>

<template>
  <section class="space-y-3 rounded-xl border border-slate-200 bg-white p-4">
    <header class="flex items-center justify-between gap-2">
      <h2 class="text-sm font-semibold text-slate-800">이슈 목록</h2>
      <p class="text-xs text-slate-500">총 {{ totalCount }}건</p>
    </header>

    <DataTable
      :columns="columns"
      :rows="rows"
      row-key="issue_id"
      :loading="loading"
      empty-text="표시할 이슈가 없습니다."
      sortable
    />
  </section>
</template>