<script setup>
import { computed } from 'vue'

import Button from '@/components/atoms/Button.vue'

const props = defineProps({
  open: {
    type: Boolean,
    default: false,
  },
  approverName: {
    type: String,
    default: '',
  },
  approvalMessage: {
    type: String,
    default: '',
  },
  completedDate: {
    type: String,
    default: '',
  },
  submitDisabled: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['close', 'update:approverName', 'update:approvalMessage', 'update:completedDate', 'submit'])

const dialogTitle = computed(() => '승인 처리')
</script>

<template>
  <div
    v-if="open"
    class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 px-4"
    @click.self="emit('close')"
  >
    <div class="w-full max-w-md rounded-xl bg-white p-5 shadow-xl">
      <div class="mb-4 flex items-center justify-between">
        <h3 class="text-lg font-semibold text-slate-900">{{ dialogTitle }}</h3>
        <button type="button" class="text-sm text-slate-500" @click="emit('close')">닫기</button>
      </div>

      <div class="space-y-4">
        <label class="block">
          <span class="mb-1 block text-sm font-medium text-slate-700">승인자 이름</span>
          <input
            :value="approverName"
            type="text"
            class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-500"
            placeholder="예: 홍길동"
            @input="emit('update:approverName', $event.target.value)"
          />
        </label>

        <label class="block">
          <span class="mb-1 block text-sm font-medium text-slate-700">승인 메세지</span>
          <textarea
            :value="approvalMessage"
            rows="4"
            class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-500"
            placeholder="승인 코멘트를 입력하세요"
            @input="emit('update:approvalMessage', $event.target.value)"
          />
        </label>

        <label class="block">
          <span class="mb-1 block text-sm font-medium text-slate-700">완료일자</span>
          <input
            :value="completedDate"
            type="date"
            class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-500"
            @input="emit('update:completedDate', $event.target.value)"
          />
        </label>
      </div>

      <div class="mt-5 flex justify-end gap-2">
        <Button variant="secondary" size="sm" @click="emit('close')">취소</Button>
        <Button size="sm" :disabled="submitDisabled" @click="emit('submit')">승인 완료</Button>
      </div>
    </div>
  </div>
</template>
