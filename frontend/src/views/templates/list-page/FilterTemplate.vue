<script setup>
import { computed, onMounted, ref } from 'vue'

import Button from '@/components/atoms/Button.vue'
import BooleanInputField from '@/components/molecules/inputs/BooleanInputField.vue'
import DateInputField from '@/components/molecules/inputs/DateInputField.vue'
import DropdownInputField from '@/components/molecules/inputs/DropdownInputField.vue'
import NumberInputField from '@/components/molecules/inputs/NumberInputField.vue'
import TextInputField from '@/components/molecules/inputs/TextInputField.vue'
import { useIssueListPage } from '@/composables/shared/useIssueListPage'
import SearchModalTemplate from '@/views/templates/update-page/SearchModalTemplate.vue'

const { loading, optionsMap, filterValues, listFields, setFilterValue, load, resetFilters } = useIssueListPage()
const searchField = ref(null)

const sortedFields = computed(() => {
  return [...listFields.value].sort((a, b) => Number(a?.list_order ?? 9999) - Number(b?.list_order ?? 9999))
})

const normalizeInputType = (inputType) => String(inputType || 'text').trim().toLowerCase()

const resolveInputComponent = (inputType) => {
  if (inputType === 'dropdown') {
    return DropdownInputField
  }
  if (inputType === 'number') {
    return NumberInputField
  }
  if (inputType === 'date') {
    return DateInputField
  }
  if (inputType === 'boolean') {
    return BooleanInputField
  }
  return TextInputField
}

const updateFieldValue = (fieldKey, value) => {
  setFilterValue(fieldKey, value)
}

const getOptions = (field) => {
  if (Array.isArray(field?.options) && field.options.length > 0) {
    return field.options
  }

  const source = field?.option_source
  if (!source) {
    return []
  }
  return optionsMap.value[source] || []
}

const getDisplayValue = (field) => {
  const value = filterValues.value?.[field.field_key]
  if (normalizeInputType(field.input_type) !== 'search') {
    return value
  }

  return getOptions(field).find((option) => String(option?.value) === String(value))?.label ?? value
}

const openSearch = (field) => {
  searchField.value = {
    ...field,
    options: getOptions(field),
  }
}

const closeSearch = () => {
  searchField.value = null
}

const selectSearchValue = (value) => {
  if (searchField.value?.field_key) {
    setFilterValue(searchField.value.field_key, value)
  }
}

onMounted(async () => {
  if (listFields.value.length === 0) {
    await load()
  }
})
</script>

<template>
  <section class="space-y-3 rounded-xl border border-slate-200 bg-white p-4">
    <header class="flex items-center justify-between gap-3">
      <h2 class="text-sm font-semibold text-slate-800">검색 필터</h2>
      <div class="flex items-center gap-2">
        <Button size="sm" variant="secondary" :disabled="loading" @click="resetFilters">
          초기화
        </Button>
        <Button size="sm" :disabled="loading" @click="load">
          조회
        </Button>
      </div>
    </header>

    <div class="grid grid-cols-1 gap-3 md:grid-cols-3 lg:grid-cols-5">
      <component
        :is="resolveInputComponent(field.input_type)"
        v-for="field in sortedFields"
        :key="field.field_key"
        :label="field.label"
        :model-value="getDisplayValue(field)"
        :options="normalizeInputType(field.input_type) === 'dropdown' ? getOptions(field) : undefined"
        :placeholder="normalizeInputType(field.input_type) === 'dropdown' ? '전체' : normalizeInputType(field.input_type) === 'search' ? '클릭하여 검색' : undefined"
        :readonly="normalizeInputType(field.input_type) === 'search'"
        @update:model-value="updateFieldValue(field.field_key, $event)"
        @open="normalizeInputType(field.input_type) === 'search' && openSearch(field)"
      />
    </div>

    <SearchModalTemplate
      :open="searchField !== null"
      :field="searchField"
      @close="closeSearch"
      @select="selectSearchValue"
    />
  </section>
</template>