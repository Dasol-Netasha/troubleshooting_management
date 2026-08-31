<script setup>
import { computed, ref } from 'vue'

import Button from '@/components/atoms/Button.vue'
import ApprovalModalTemplate from '@/views/templates/detail-page/ApprovalModalTemplate.vue'
import { useIssueDetailPage } from '@/composables/shared/useIssueDetailPage'
import { useIssueDetailStore } from '@/stores/issueDetailStore'

const { issueId, loading, errorMessage, detailFields } = useIssueDetailPage()
const issueDetailStore = useIssueDetailStore()

const isApprovalModalOpen = ref(false)
const approverName = ref('')
const approvalMessage = ref('')

const approvalStatus = computed(() => {
  const fields = detailFields.value || []
  const approvalValue = fields.find((field) => field.key === 'approval_yn')?.value
  const approvedBy = fields.find((field) => field.key === 'approved_by')?.value
  const approvedMessage = fields.find((field) => field.key === 'approved_message')?.value

  const normalizedApproval = (() => {
    if (approvalValue === true) {
      return true
    }

    const text = String(approvalValue ?? '').trim().toLowerCase()
    return text === 'yes' || text === 'true' || text === '승인완료' || text === 'approved'
  })()

  return {
    approved: normalizedApproval,
    approvedBy: approvedBy && approvedBy !== '-' ? String(approvedBy) : '-',
    approvedMessage: approvedMessage && approvedMessage !== '-' ? String(approvedMessage) : '-',
  }
})

const openApprovalModal = () => {
  approverName.value = ''
  approvalMessage.value = '승인완료'
  isApprovalModalOpen.value = true
}

const closeApprovalModal = () => {
  isApprovalModalOpen.value = false
  approverName.value = ''
  approvalMessage.value = ''
}

const submitApproval = async () => {
  const trimmedName = approverName.value.trim()
  const trimmedMessage = approvalMessage.value.trim()
  if (!trimmedName || !trimmedMessage) {
    return
  }

  await issueDetailStore.approveIssue(issueId.value, {
    approved_by: trimmedName,
    approved_message: trimmedMessage,
  })

  closeApprovalModal()
}

const normalizedFields = computed(() => {
  return (detailFields.value || [])
    .filter((item) => item?.key && item.key !== 'issue_id')
    .map((item) => ({
      key: item.key,
      label: item.label || item.key,
      value: item.value ?? '-',
      detail_order: Number.isFinite(Number(item.detail_order)) ? Number(item.detail_order) : 9999,
    }))
    .sort((a, b) => {
      if (a.detail_order !== b.detail_order) {
        return a.detail_order - b.detail_order
      }
      return String(a.key).localeCompare(String(b.key))
    })
})

const emptyField = (order) => ({
  key: `empty-${order}`,
  label: `상세정보 ${order}`,
  value: '-',
})

const fieldAt = (order) => normalizedFields.value[order - 1] || emptyField(order)

const rowFields = (orders) => orders.map((order) => fieldAt(order))

// 왼쪽/오른쪽 모두 동일한 형태: 줄(row) 배열, 줄마다 필드 개수(orders)와 높이(rowSpan)를 독립적으로 지정
const detailLayoutSections = [
  {
    leftRows: [{ orders: [1], rowSpan: 1 }],
    rightRows: [{ orders: [2, 3, 4], rowSpan: 1 }],
  },
  {
    leftRows: [{ orders: [5], rowSpan: 2 }],
    rightRows: [
      { orders: [6, 7, 8], rowSpan: 1 },
      { orders: [9, 10, 11], rowSpan: 1 },
    ],
  },
  {
    leftRows: [{ orders: [12], rowSpan: 2 }],
    rightRows: [{ orders: [13], rowSpan: 2 }],
  },
  {
    leftRows: [{ orders: [14], rowSpan: 2 }],
    rightRows: [
      { orders: [15], rowSpan: 1 },
      { orders: [16, 17], rowSpan: 1 },
    ],
  },
]

const rightGridClass = (rowLength) => {
  if (rowLength >= 3) {
    return 'grid grid-cols-1 gap-3 sm:grid-cols-3'
  }
  if (rowLength === 2) {
    return 'grid grid-cols-1 gap-3 sm:grid-cols-2'
  }
  return 'grid grid-cols-1 gap-3'
}

const normalizedRowSpan = (rowSpan) => (Number(rowSpan) === 2 ? 2 : 1)

const normalizeRow = (rowConfig) => {
  if (Array.isArray(rowConfig)) {
    return { orders: rowConfig, rowSpan: 1 }
  }

  return {
    orders: Array.isArray(rowConfig?.orders) ? rowConfig.orders : [],
    rowSpan: normalizedRowSpan(rowConfig?.rowSpan),
  }
}

// side에 상관없이 동일 로직으로 처리 (leftRows / rightRows 둘 다 이 함수를 씀)
const sectionRows = (rows) => (rows || []).map((rowConfig) => normalizeRow(rowConfig))

const sectionUsesTwoRows = (section) => {
  const leftRows = sectionRows(section?.leftRows)
  const rightRows = sectionRows(section?.rightRows)
  const allRows = [...leftRows, ...rightRows]

  if (allRows.length === 0) {
    return false
  }

  if (leftRows.length > 1 || rightRows.length > 1) {
    return true
  }

  return allRows.some((row) => row.rowSpan === 2)
}

// Tailwind는 클래스명을 소스에서 정적으로 스캔하므로, 템플릿 리터럴로 동적 조합한
// 클래스(md:min-h-[${n}px])는 빌드 시 인식되지 못한다. 반드시 리터럴 문자열로 둔다.
const spanCardClass = (rowSpan) => {
  if (normalizedRowSpan(rowSpan) !== 2) {
    return 'md:min-h-[104px]'
  }

  return 'md:row-span-2 md:min-h-[220px] md:max-h-[220px] md:overflow-y-auto'
}
</script>

<template>
  <section class="space-y-3 rounded-xl border border-slate-200 bg-white p-4">
    <p v-if="errorMessage" class="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
      {{ errorMessage }}
    </p>

    <div v-else class="space-y-3">
      <p v-if="loading" class="px-4 py-3 text-sm text-slate-500">로딩 중...</p>

      <div v-else class="space-y-3">
        <div class="flex items-center justify-between gap-3 rounded-lg border border-slate-200 bg-slate-50 p-3">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Approval</p>
            <p class="mt-1 text-sm text-slate-700">
              {{ approvalStatus.approved ? '승인 완료' : '미승인 상태' }}
            </p>
          </div>

          <div v-if="approvalStatus.approved" class="flex flex-col items-end gap-1 text-right">
            <span class="text-sm font-medium text-slate-700">승인자: {{ approvalStatus.approvedBy }}</span>
            <span class="text-sm text-slate-600">메세지: {{ approvalStatus.approvedMessage }}</span>
          </div>

          <Button v-else variant="primary" size="sm" @click="openApprovalModal">
            승인하기
          </Button>
        </div>

        <ApprovalModalTemplate
          :open="isApprovalModalOpen"
          :approver-name="approverName"
          :approval-message="approvalMessage"
          :submit-disabled="!approverName.trim() || !approvalMessage.trim()"
          @close="closeApprovalModal"
          @update:approver-name="approverName = $event"
          @update:approval-message="approvalMessage = $event"
          @submit="submitApproval"
        />

        <div
          v-for="(section, sectionIndex) in detailLayoutSections"
          :key="`detail-layout-${sectionIndex}`"
          class="grid grid-cols-1 gap-3 md:grid-cols-2"
          :class="{ 'md:grid-rows-2': sectionUsesTwoRows(section) }"
        >
          <div
            v-for="(row, rowIndex) in sectionRows(section.leftRows)"
            :key="`detail-layout-${sectionIndex}-left-${rowIndex}`"
            class="rounded-lg border border-slate-100 bg-slate-50/70 px-3 py-2"
            :class="spanCardClass(row.rowSpan)"
          >
            <div :class="rightGridClass(row.orders.length)">
              <div v-for="field in rowFields(row.orders)" :key="field.key">
                <p class="text-md font-medium text-slate-500 pb-2">{{ field.label }}</p>
                <p class="text-xl text-slate-800 whitespace-pre-wrap">{{ field.value }}</p>
              </div>
            </div>
          </div>

          <div
            v-for="(row, rowIndex) in sectionRows(section.rightRows)"
            :key="`detail-layout-${sectionIndex}-right-${rowIndex}`"
            class="rounded-lg border border-slate-100 bg-slate-50/70 px-3 py-2"
            :class="spanCardClass(row.rowSpan)"
          >
            <div :class="rightGridClass(row.orders.length)">
              <div v-for="field in rowFields(row.orders)" :key="field.key">
                <p class="text-md font-medium text-slate-500 pb-2">{{ field.label }}</p>
                <p class="text-xl text-slate-800 whitespace-pre-wrap">{{ field.value }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>