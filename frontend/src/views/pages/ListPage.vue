<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

import { useIssueListPage } from '@/composables/shared/useIssueListPage'
import FilterTemplate from '@/views/templates/list-page/FilterTemplate.vue'
import ListTableTemplate from '@/views/templates/list-page/ListTableTemplate.vue'

const {
  loading,
  errorMessage,
  totalCount,
  optionsMap,
  filterValues,
  listFields,
  tableColumns,
  tableRows,
  load,
  resetFilters,
} = useIssueListPage()

const router = useRouter()

const onSearch = async () => {
  await load()
}

const onReset = async () => {
  await resetFilters()
}

onMounted(async () => {
  await load()
})

const goToDetail = () => {
  router.push('/detail')
}

const goToUpdate = () => {
  router.push('/update')
}
</script>

<template>
  <section class="space-y-4">
    <div class="flex items-center justify-end gap-2">
      <button
        type="button"
        class="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-700"
        @click="goToDetail"
      >
        DetailPage 이동
      </button>
      <button
        type="button"
        class="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-900 transition hover:bg-slate-100"
        @click="goToUpdate"
      >
        UpdatePage 이동
      </button>
    </div>

    <FilterTemplate
      v-model="filterValues"
      :fields="listFields"
      :options-map="optionsMap"
      :loading="loading"
      @search="onSearch"
      @reset="onReset"
    />

    <p v-if="errorMessage" class="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
      {{ errorMessage }}
    </p>

    <ListTableTemplate :columns="tableColumns" :rows="tableRows" :loading="loading" :total-count="totalCount" />
  </section>
</template>