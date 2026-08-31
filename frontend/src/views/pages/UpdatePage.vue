<script setup>
import { useRouter } from 'vue-router'

import BackNavIconBtn from '@/components/molecules/buttons/BackNavIconBtn.vue'
import Button from '@/components/atoms/Button.vue'
import { useIssueForm } from '@/composables/shared/useIssueForm'
import InputTemplate from '@/views/templates/update-page/InputTemplate.vue'
import AddImagesTmplate from '@/views/templates/update-page/AddImagesTmplate.vue'

const router = useRouter()

const {
  loading,
  saving,
  errorMessage,
  fields,
  values,
  attachedImages,
  targetIssueId,
  isEditMode,
  pageTitle,
  pageDescription,
  setFieldValue,
  setAttachedImages,
  save,
} = useIssueForm()

const goToList = () => {
  router.push('/list')
}

const onSave = async () => {
  await save()
}

const onUpdateField = (fieldKey, value) => {
  setFieldValue(fieldKey, value)
}

const onUpdateImages = (nextImages) => {
  setAttachedImages(nextImages)
}
</script>

<template>
  <section class="space-y-4">
    <div class="flex items-center gap-2">
      <BackNavIconBtn @click="goToList" />
      <h1 class="text-2xl font-semibold text-slate-900">{{ pageTitle }}</h1>
    </div>

    <section class="space-y-3 rounded-xl border border-slate-200 bg-white p-4">

      <p v-if="loading" class="text-sm text-slate-500">데이터를 불러오는 중입니다.</p>
      <p v-else-if="errorMessage" class="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
        {{ errorMessage }}
      </p>

      <div v-else class="space-y-3">

        <InputTemplate :fields="fields" :values="values" @update-field="onUpdateField" />

        <AddImagesTmplate :model-value="attachedImages" @update:model-value="onUpdateImages" />
        
        <div class="flex items-center gap-2 pt-2">
          <Button size="sm" variant="secondary" :disabled="saving" @click="goToList">취소</Button>
          <Button size="sm" :disabled="saving" @click="onSave">{{ saving ? '저장 중...' : '저장' }}</Button>
        </div>
      </div>
    </section>

  </section>
</template>