import { computed, ref } from 'vue'

import { useIssueListStore } from '@/stores/issueListStore'

const TEXT_INPUT_TYPES = new Set(['text', 'textarea'])
const sharedFilterValues = ref({})
const PAGE_SIZE_OPTIONS = [10, 20, 30, 50]

const sortByListOrder = (fields) => {
  return [...fields].sort((a, b) => {
    const left = Number(a?.list_order ?? 9999)
    const right = Number(b?.list_order ?? 9999)
    return left - right
  })
}

export const useIssueListPage = () => {
  const issueListStore = useIssueListStore()
  const filterValues = sharedFilterValues
  const currentPage = ref(1)
  const pageSize = ref(10)
  const loading = computed(() => issueListStore.loading)
  const errorMessage = computed(() => issueListStore.errorMessage)
  const totalCount = computed(() => issueListStore.totalCount)

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
        const rawValue = row?.[field.field_key]

        if (field?.input_type === 'boolean') {
          const normalizedBoolean = rawValue === true || rawValue === 'true' || rawValue === 'True' || rawValue === 'YES' || rawValue === 'Yes' || rawValue === 1
          displayRow[field.field_key] = normalizedBoolean ? '승인완료' : '미승인'
          continue
        }

        if (field?.input_type === 'multi_dropdown') {
          const optionMap = optionLabelMaps.value[field?.option_source]
          const values = Array.isArray(rawValue) ? rawValue : []
          displayRow[field.field_key] = values.map((value) => optionMap?.get(String(value)) ?? value).join(', ')
          continue
        }

        const source = field?.option_source
        if (!source) {
          continue
        }

        const optionMap = optionLabelMaps.value[source]
        if (!optionMap) {
          continue
        }

        const resolved = optionMap.get(String(rawValue))
        displayRow[field.field_key] = resolved ?? rawValue
      }

      return displayRow
    })
  })

  const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / pageSize.value)))

  const pagedTableRows = computed(() => {
    const start = (currentPage.value - 1) * pageSize.value
    return tableRows.value.slice(start, start + pageSize.value)
  })

  const setCurrentPage = (page) => {
    const nextPage = Number(page)
    currentPage.value = Math.min(Math.max(1, Number.isInteger(nextPage) ? nextPage : 1), totalPages.value)
  }

  const setPageSize = (size) => {
    const nextSize = Number(size)
    pageSize.value = PAGE_SIZE_OPTIONS.includes(nextSize) ? nextSize : 10
    currentPage.value = 1
  }

  const setFilterValue = (fieldKey, value) => {
    filterValues.value = {
      ...filterValues.value,
      [fieldKey]: value,
    }
  }

  const load = async () => {
    await issueListStore.fetchListPageData(normalizedFilters.value)
    currentPage.value = 1

    if (Object.keys(filterValues.value).length === 0) {
      initializeFilters()
    }
  }

  const resetFilters = async () => {
    initializeFilters()
    await issueListStore.fetchListPageData({})
    currentPage.value = 1
  }

  return {
    loading,
    errorMessage,
    totalCount,
    optionsMap: issueListStore.optionsMap,
    filterValues,
    listFields,
    tableColumns,
    tableRows,
    pagedTableRows,
    currentPage,
    pageSize,
    totalPages,
    pageSizeOptions: PAGE_SIZE_OPTIONS,
    setCurrentPage,
    setPageSize,
    setFilterValue,
    load,
    resetFilters,
  }
}