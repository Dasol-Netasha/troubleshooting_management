<script setup>
import { toRef } from 'vue'

import { provideOptionCardContext } from '@/composables/option-page/useOptionCardContext'
import AddMenu from '@/views/organisms/option-page/AddMenu.vue'
import MenuTable from '@/views/organisms/option-page/MenuTable.vue'

const props = defineProps({
  sourceKey: {
    type: String,
    required: true,
  },
  sourceLabel: {
    type: String,
    required: true,
  },
})

provideOptionCardContext({
  sourceKey: toRef(props, 'sourceKey'),
  sourceLabel: toRef(props, 'sourceLabel'),
})
</script>

<template>
  <section class="space-y-4 rounded-xl border border-slate-200 bg-white p-4">
    <header class="space-y-1">
      <h2 class="text-lg font-semibold text-slate-900">{{ sourceLabel }}</h2>
      <p class="text-sm text-slate-500">{{ sourceKey }} 테이블의 드롭다운 항목을 관리합니다.</p>
    </header>

    <AddMenu />

    <MenuTable />
  </section>
</template>
