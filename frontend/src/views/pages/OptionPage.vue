<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import BackNavIconBtn from '@/components/molecules/buttons/BackNavIconBtn.vue'
import { optionService } from '@/services/optionService'
import DropdownOptionCard from '@/views/templates/option-page/DropdownOptionCard.vue'

const router = useRouter()

const loading = ref(false)
const errorMessage = ref('')
const sources = ref([])

const loadSources = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const data = await optionService.getSources()
    sources.value = Array.isArray(data?.sources) ? data.sources : []
  } catch {
    sources.value = []
    errorMessage.value = '옵션 분류를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadSources()
})

const goToList = () => {
  router.push('/list')
}
</script>

<template>
  <section class="space-y-4">
    <header class="space-y-2">
      <div class="flex items-center gap-2">
        <BackNavIconBtn @click="goToList" />
        <h1 class="text-2xl font-semibold text-slate-900">옵션 관리</h1>
      </div>
      <p class="text-sm text-slate-500">드롭다운 항목을 등록, 수정, 삭제할 수 있습니다.</p>
    </header>

    <p v-if="errorMessage" class="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
      {{ errorMessage }}
    </p>

    <p v-else-if="loading" class="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-500">
      옵션 분류를 불러오는 중입니다.
    </p>

    <p v-else-if="sources.length === 0" class="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-500">
      관리 가능한 드롭다운 분류가 없습니다.
    </p>

    <section v-else class="grid grid-cols-1 gap-4 xl:grid-cols-2">
      <DropdownOptionCard
        v-for="source in sources"
        :key="source.key"
        :source-key="source.key"
        :source-label="source.label"
      />
    </section>

  </section>
</template>
