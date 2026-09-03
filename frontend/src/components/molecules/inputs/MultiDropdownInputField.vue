<script setup>
import { computed, ref } from 'vue'

import Button from '@/components/atoms/Button.vue'
import Select from '@/components/atoms/Select.vue'
import BilingualLabel from '@/components/molecules/labels/BilingualLabel.vue'

const props = defineProps({
  label: { type: String, required: true },
  modelValue: { type: Array, default: () => [] },
  options: { type: Array, default: () => [] },
  required: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue'])
const selectedValue = ref('')
const selectedValues = computed(() => (Array.isArray(props.modelValue) ? props.modelValue.map(String) : []))
const selectedOptions = computed(() => props.options.filter((option) => selectedValues.value.includes(String(option?.value))))

const addSelection = () => {
  if (!selectedValue.value || selectedValues.value.includes(String(selectedValue.value))) {
    return
  }
  emit('update:modelValue', [...selectedValues.value, String(selectedValue.value)])
  selectedValue.value = ''
}

const removeSelection = (value) => {
  emit('update:modelValue', selectedValues.value.filter((selected) => selected !== String(value)))
}
</script>

<template>
  <div class="flex flex-col gap-1">
    <label class="text-xs font-medium text-slate-600">
      <BilingualLabel :label="label" />
      <span v-if="required" class="ml-0.5 text-rose-500">*</span>
    </label>
    <div class="flex gap-2">
      <Select v-model="selectedValue" class="min-w-0 flex-1" :options="options" size="sm" placeholder="선택" />
      <Button size="sm" type="button" :disabled="!selectedValue" @click="addSelection">추가</Button>
    </div>
    <div v-if="selectedOptions.length" class="flex flex-wrap gap-1 pt-1">
      <span
        v-for="option in selectedOptions"
        :key="option.value"
        class="inline-flex items-center gap-1 rounded-md bg-slate-100 px-2 py-1 text-xs text-slate-700"
      >
        {{ option.label }}
        <button type="button" class="font-semibold text-slate-500 hover:text-rose-600" @click="removeSelection(option.value)">x</button>
      </span>
    </div>
  </div>
</template>