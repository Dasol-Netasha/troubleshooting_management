import { computed, ref } from 'vue'

import { useIssueListStore } from '@/stores/issueListStore'

const TEXT_INPUT_TYPES = new Set(['text', 'textarea'])

const sortByListOrder = (fields) => {
  return [...fields].sort((a, b) => {
    const left = Number(a?.list_order ?? 9999)
    const right = Number(b?.list_order ?? 9999)
    return left - right
  })
}

export const useIssueListPage = () => {
  const issueListStore = useIssueListStore()
  const filterValues = ref({})

  const listFields = computed(() => {
    const visible = issueListStore.fields.filter((field) => field?.show_in_list === true)
    return sortByListOrder(visible)
  })

  const initializeFilters = () => {
    const next = {}
    for (const field of listFields.value) {
      next[field.field_key] = ''
    }
    filterValues.value = next
  }

  const coerceFilterValue = (field, value) => {
    const inputType = String(field?.input_type || '')

    if (value === '' || value === null || value === undefined) {
      return ''
    }

    if (inputType === 'number' || inputType === 'dropdown') {
      const parsed = Number(value)
      return Number.isNaN(parsed) ? String(value) : parsed
    }

    if (inputType === 'boolean') {
      return Boolean(value)
    }

    if (TEXT_INPUT_TYPES.has(inputType)) {
      return String(value)
    }

    return value
  }

  const normalizedFilters = computed(() => {
    const normalized = {}

    for (const field of listFields.value) {
      const key = field.field_key
      normalized[key] = coerceFilterValue(field, filterValues.value[key])
    }

    return normalized
  })

  const tableColumns = computed(() => {
    return listFields.value.map((field) => ({
      key: field.field_key,
      label: field.label,
      sortable: true,
    }))
  })

  const optionLabelMaps = computed(() => {
    const result = {}
    for (const [source, options] of Object.entries(issueListStore.optionsMap || {})) {
      const map = new Map()
      for (const option of options || []) {
        map.set(String(option?.value), option?.label)
      }
      result[source] = map
    }
    return result
  })

  const tableRows = computed(() => {
    return issueListStore.rows.map((row) => {
      const displayRow = { ...row }

      for (const field of listFields.value) {
        const source = field?.option_source
        if (!source) {
          continue
        }

        const optionMap = optionLabelMaps.value[source]
        if (!optionMap) {
          continue
        }

        const rawValue = row?.[field.field_key]
        const resolved = optionMap.get(String(rawValue))
        displayRow[field.field_key] = resolved ?? rawValue
      }

      return displayRow
    })
  })

  const setFilterValue = (fieldKey, value) => {
    filterValues.value = {
      ...filterValues.value,
      [fieldKey]: value,
    }
  }

  const load = async () => {
    await issueListStore.fetchListPageData(normalizedFilters.value)

    if (Object.keys(filterValues.value).length === 0) {
      initializeFilters()
    }
  }

  const resetFilters = async () => {
    initializeFilters()
    await issueListStore.fetchListPageData({})
  }

  return {
    loading: issueListStore.loading,
    errorMessage: issueListStore.errorMessage,
    totalCount: issueListStore.totalCount,
    optionsMap: issueListStore.optionsMap,
    filterValues,
    listFields,
    tableColumns,
    tableRows,
    setFilterValue,
    load,
    resetFilters,
  }
}