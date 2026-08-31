<script setup>
import Button from '@/components/atoms/Button.vue'
import Input from '@/components/atoms/Input.vue'
import { useAddMenu } from '@/composables/option-page/useAddMenu'

const {
  newLabel,
  saving,
  errorMessage,
  canSubmit,
  submit,
} = useAddMenu()
</script>

<template>
  <div class="space-y-1">
    <label class="text-xs font-semibold uppercase tracking-[0.08em] text-slate-500">신규 항목</label>
    <p v-if="errorMessage" class="rounded-md border border-rose-200 bg-rose-50 px-2 py-1 text-xs text-rose-700">
      {{ errorMessage }}
    </p>
    <div class="flex gap-2">
      <Input
        :model-value="newLabel"
        placeholder="추가할 항목명"
        @update:model-value="newLabel = $event"
        @enter="submit"
      />
      <Button
        size="sm"
        variant="primary"
        class="w-20 shrink-0"
        :disabled="saving || !canSubmit"
        @click="submit"
      >
        추가
      </Button>
    </div>
  </div>
</template>
