<script setup>
import { computed, ref } from 'vue'

import Button from '@/components/atoms/Button.vue'
import FileInput from '@/components/atoms/FileInput.vue'

const selectedFiles = ref([])

const imageAccept = 'image/png,image/jpeg,image/webp,image/gif'

const totalSizeText = computed(() => {
  const total = selectedFiles.value.reduce((sum, file) => sum + (file?.size || 0), 0)
  if (!total) {
    return '0 KB'
  }

  const kb = total / 1024
  if (kb < 1024) {
    return `${kb.toFixed(1)} KB`
  }

  return `${(kb / 1024).toFixed(2)} MB`
})

const onPickFile = (file) => {
  if (!file) {
    return
  }

  const isImage = String(file.type || '').startsWith('image/')
  if (!isImage) {
    window.alert('이미지 파일만 첨부할 수 있습니다.')
    return
  }

  selectedFiles.value = [...selectedFiles.value, file]
}

const removeFileAt = (index) => {
  selectedFiles.value = selectedFiles.value.filter((_, idx) => idx !== index)
}

const clearFiles = () => {
  selectedFiles.value = []
}
</script>

<template>
  <section class="space-y-3 rounded-xl border border-slate-200 bg-white p-4">
    <header class="flex items-center justify-between gap-2">
      <h2 class="text-sm font-semibold text-slate-800">이미지 첨부</h2>
      <p class="text-xs text-slate-500">{{ selectedFiles.length }}개 / {{ totalSizeText }}</p>
    </header>

    <p class="text-xs text-slate-500">등록/수정 저장 API에 이미지 업로드가 연결되면 함께 전송됩니다.</p>

    <div class="flex flex-col gap-2 md:flex-row md:items-center">
      <FileInput :accept="imageAccept" size="sm" @change="onPickFile" />
      <Button size="sm" variant="secondary" :disabled="selectedFiles.length === 0" @click="clearFiles">
        전체 제거
      </Button>
    </div>

    <ul v-if="selectedFiles.length > 0" class="space-y-2">
      <li
        v-for="(file, index) in selectedFiles"
        :key="`${file.name}-${file.lastModified}-${index}`"
        class="flex items-center justify-between gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2"
      >
        <div class="min-w-0">
          <p class="truncate text-sm text-slate-700">{{ file.name }}</p>
          <p class="text-xs text-slate-500">{{ (file.size / 1024).toFixed(1) }} KB</p>
        </div>
        <Button size="sm" variant="danger" outlined @click="removeFileAt(index)">삭제</Button>
      </li>
    </ul>

    <p v-else class="text-sm text-slate-500">첨부된 이미지가 없습니다.</p>
  </section>
</template>
