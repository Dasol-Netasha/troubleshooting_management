import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { issueService } from '@/services/issueService'

const ORDER_FALLBACK = 9999

const normalizeSortOrder = (value) => {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : ORDER_FALLBACK
}

const normalizeFields = (fields) => {
  return [...(fields || [])]
    .filter((field) => field?.key)
    .sort((a, b) => {
      const left = normalizeSortOrder(a?.detail_order)
      const right = normalizeSortOrder(b?.detail_order)
      if (left !== right) {
        return left - right
      }
      return String(a?.key).localeCompare(String(b?.key))
    })
}

const toModelValue = (field, value) => {
  const inputType = String(field?.input_type || 'text')

  if (value === null || value === undefined) {
    if (inputType === 'multi_dropdown') {
      return []
    }
    if (inputType === 'boolean') {
      return false
    }
    return ''
  }

  if (inputType === 'boolean') {
    return Boolean(value)
  }

  if (inputType === 'multi_dropdown') {
    return Array.isArray(value) ? value : []
  }

  return value
}

const toSubmitValue = (field, value) => {
  const inputType = String(field?.input_type || 'text')

  if (value === '' || value === null || value === undefined) {
    if (inputType === 'multi_dropdown') {
      return []
    }
    if (inputType === 'boolean') {
      return false
    }
    return null
  }

  if (inputType === 'number' || inputType === 'dropdown' || inputType === 'search') {
    const parsed = Number(value)
    return Number.isNaN(parsed) ? value : parsed
  }

  if (inputType === 'multi_dropdown') {
    return Array.isArray(value) ? value.map(Number).filter(Number.isInteger) : []
  }

  if (inputType === 'boolean') {
    return Boolean(value)
  }

  return value
}

export const useIssueForm = () => {
  const route = useRoute()
  const router = useRouter()

  const loading = ref(false)
  const saving = ref(false)
  const errorMessage = ref('')
  const fields = ref([])
  const values = ref({})
  const attachedImages = ref([])
  const existingImageIds = ref([])

  const targetIssueId = computed(() => {
    const raw = route.query?.issueId
    const parsed = Number(raw)
    return Number.isInteger(parsed) && parsed > 0 ? parsed : null
  })

  const isEditMode = computed(() => targetIssueId.value !== null)

  const pageTitle = computed(() => {
    if (isEditMode.value) {
      return `이슈 변경 #${targetIssueId.value}`
    }
    return '신규 이슈 등록'
  })

  const pageDescription = computed(() => {
    if (isEditMode.value) {
      return 'DetailPage와 동일한 항목을 수정합니다.'
    }
    return 'DetailPage와 동일한 항목으로 신규 이슈를 등록합니다.'
  })

  const setFieldValue = (fieldKey, value) => {
    values.value = {
      ...values.value,
      [fieldKey]: value,
    }
  }

  const initializeValues = (nextFields, sourceValues = {}) => {
    const nextValues = {}
    for (const field of nextFields) {
      const key = String(field.key)
      nextValues[key] = toModelValue(field, sourceValues[key])
    }
    values.value = nextValues
  }

  const load = async () => {
    loading.value = true
    errorMessage.value = ''

    try {
      if (isEditMode.value) {
        const data = await issueService.getFormData(targetIssueId.value)
        const nextFields = normalizeFields(data?.fields)
        fields.value = nextFields

        const sourceValues = {}
        for (const field of nextFields) {
          sourceValues[field.key] = field.value
        }
        initializeValues(nextFields, sourceValues)
        attachedImages.value = Array.isArray(data?.images) ? data.images : []
        existingImageIds.value = attachedImages.value.map((image) => Number(image?.image_id)).filter(Number.isInteger)
        return
      }

      const data = await issueService.getFormConfig()
      const nextFields = normalizeFields(data?.fields).filter((field) => field.key !== 'completed_date')
      fields.value = nextFields
      initializeValues(nextFields)
      attachedImages.value = []
      existingImageIds.value = []
    } catch (error) {
      fields.value = []
      values.value = {}
      errorMessage.value = '작성 폼 데이터를 불러오지 못했습니다.'
    } finally {
      loading.value = false
    }
  }

  const save = async () => {
    saving.value = true
    errorMessage.value = ''

    try {
      const payload = {}
      for (const field of fields.value) {
        const key = String(field.key)
        payload[key] = toSubmitValue(field, values.value[key])
      }

      let result
      if (isEditMode.value) {
        const retainedImageIds = new Set(
          attachedImages.value.map((image) => Number(image?.image_id)).filter(Number.isInteger)
        )
        const deletedImageIds = existingImageIds.value.filter((imageId) => !retainedImageIds.has(imageId))
        const newImages = attachedImages.value.filter((image) => !Number.isInteger(Number(image?.image_id)))
        result = await issueService.updateIssue(targetIssueId.value, payload, newImages, deletedImageIds)
      } else {
        result = await issueService.createIssue(payload, attachedImages.value)
      }

      const createdOrUpdatedId = Number(result?.issue_id || targetIssueId.value)
      if (Number.isInteger(createdOrUpdatedId) && createdOrUpdatedId > 0) {
        router.push(`/detail/${createdOrUpdatedId}`)
        return
      }

      router.push('/list')
    } catch (error) {
      const detail = error?.response?.data?.detail
      errorMessage.value = detail ? `저장에 실패했습니다: ${detail}` : '저장에 실패했습니다.'
      throw error
    } finally {
      saving.value = false
    }
  }

  const setAttachedImages = (images) => {
    attachedImages.value = Array.isArray(images) ? images : []
  }

  watch(
    () => route.query.issueId,
    () => {
      load()
    },
    { immediate: true }
  )

  return {
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
    load,
    save,
  }
}
