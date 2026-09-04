<script setup>
import { computed, ref, watch } from 'vue'

import { issueService } from '@/services/issueService'

const props = defineProps({
  issueId: {
    type: [Number, String],
    required: true,
  },
})

const comments = ref([])
const author = ref('')
const content = ref('')
const replyAuthor = ref({})
const replyContent = ref({})
const activeReplyId = ref(null)
const loading = ref(false)
const saving = ref(false)
const errorMessage = ref('')

const normalizedIssueId = computed(() => {
  const value = Number(props.issueId)
  return Number.isInteger(value) && value > 0 ? value : null
})

const canSubmitComment = computed(() => Boolean(author.value.trim() && content.value.trim() && !saving.value))

const formatDate = (value) => {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? '' : date.toLocaleString('ko-KR')
}

const loadComments = async () => {
  if (!normalizedIssueId.value) {
    return
  }

  loading.value = true
  errorMessage.value = ''
  try {
    const data = await issueService.getComments(normalizedIssueId.value)
    comments.value = Array.isArray(data?.comments) ? data.comments : []
  } catch {
    errorMessage.value = '댓글을 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

const submitComment = async () => {
  if (!canSubmitComment.value || !normalizedIssueId.value) {
    return
  }

  saving.value = true
  errorMessage.value = ''
  try {
    const comment = await issueService.createComment(normalizedIssueId.value, {
      author: author.value.trim(),
      content: content.value.trim(),
    })
    comments.value = [...comments.value, { ...comment, reply: null }]
    content.value = ''
  } catch {
    errorMessage.value = '댓글을 등록하지 못했습니다.'
  } finally {
    saving.value = false
  }
}

const openReply = (commentId) => {
  activeReplyId.value = commentId
  replyAuthor.value[commentId] = ''
  replyContent.value[commentId] = ''
}

const submitReply = async (commentId) => {
  const replyAuthorName = String(replyAuthor.value[commentId] || '').trim()
  const value = String(replyContent.value[commentId] || '').trim()
  if (!replyAuthorName || !value || saving.value || !normalizedIssueId.value) {
    return
  }

  saving.value = true
  errorMessage.value = ''
  try {
    const updatedComment = await issueService.createCommentReply(normalizedIssueId.value, commentId, {
      author: replyAuthorName,
      content: value,
    })
    comments.value = comments.value.map((comment) => comment.comment_id === commentId ? updatedComment : comment)
    activeReplyId.value = null
    delete replyAuthor.value[commentId]
    delete replyContent.value[commentId]
  } catch {
    errorMessage.value = '답글을 등록하지 못했습니다.'
  } finally {
    saving.value = false
  }
}

watch(normalizedIssueId, loadComments, { immediate: true })
</script>

<template>
  <section class="space-y-4 rounded-xl border border-slate-200 bg-white p-4">
    <header class="flex items-center justify-between">
      <h2 class="text-base font-semibold text-slate-900">댓글</h2>
      <span class="text-sm text-slate-500">{{ comments.length }}개</span>
    </header>

    <p v-if="errorMessage" class="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{{ errorMessage }}</p>

    <div class="rounded-lg border border-slate-200 p-3">
      <input v-model="author" type="text" maxlength="100" class="mb-3 w-full border-0 border-b border-slate-200 bg-transparent px-0 pb-2 text-sm text-slate-800 outline-none placeholder:text-slate-400" placeholder="작성자" :disabled="saving" />
      <textarea
        v-model="content"
        rows="3"
        class="w-full resize-y border-0 bg-transparent text-sm text-slate-800 outline-none placeholder:text-slate-400"
        placeholder="댓글을 입력하세요"
        :disabled="saving"
      />
      <div class="mt-2 flex items-center justify-between gap-3 border-t border-slate-100 pt-2">
        <p class="text-xs text-slate-500">작성자와 내용을 입력해 주세요.</p>
        <button type="button" class="rounded-md bg-slate-900 px-3 py-1.5 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-slate-300" :disabled="!canSubmitComment" @click="submitComment">
          등록
        </button>
      </div>
    </div>

    <p v-if="loading" class="py-4 text-center text-sm text-slate-500">댓글을 불러오는 중...</p>
    <p v-else-if="comments.length === 0" class="py-4 text-center text-sm text-slate-500">첫 댓글을 남겨주세요.</p>

    <div v-else class="divide-y divide-slate-100">
      <article v-for="comment in comments" :key="comment.comment_id" class="py-4 first:pt-0 last:pb-0">
        <div class="flex items-baseline justify-between gap-3">
          <strong class="text-sm text-slate-800">{{ comment.author }}</strong>
          <time class="shrink-0 text-xs text-slate-400">{{ formatDate(comment.created_at) }}</time>
        </div>
        <p class="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-700">{{ comment.content }}</p>

        <div v-if="comment.reply" class="mt-3 border-l-2 border-slate-200 pl-3">
          <div class="flex items-baseline justify-between gap-3">
            <strong class="text-sm text-slate-800">{{ comment.reply.author }}</strong>
            <time class="shrink-0 text-xs text-slate-400">{{ formatDate(comment.reply.created_at) }}</time>
          </div>
          <p class="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-700">{{ comment.reply.content }}</p>
        </div>

        <template v-else>
          <button v-if="activeReplyId !== comment.comment_id" type="button" class="mt-3 text-sm font-medium text-slate-600 hover:text-slate-900 disabled:cursor-not-allowed disabled:text-slate-300" :disabled="saving" @click="openReply(comment.comment_id)">
            답글
          </button>
          <div v-else class="mt-3 rounded-lg border border-slate-200 p-3">
            <input v-model="replyAuthor[comment.comment_id]" type="text" maxlength="100" class="mb-3 w-full border-0 border-b border-slate-200 bg-transparent px-0 pb-2 text-sm text-slate-800 outline-none placeholder:text-slate-400" placeholder="작성자" :disabled="saving" />
            <textarea v-model="replyContent[comment.comment_id]" rows="2" class="w-full resize-y border-0 bg-transparent text-sm text-slate-800 outline-none placeholder:text-slate-400" placeholder="답글을 입력하세요" :disabled="saving" />
            <div class="mt-2 flex justify-end gap-2 border-t border-slate-100 pt-2">
              <button type="button" class="px-2 py-1 text-sm text-slate-600" :disabled="saving" @click="activeReplyId = null">취소</button>
              <button type="button" class="rounded-md bg-slate-900 px-3 py-1 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-slate-300" :disabled="!replyAuthor[comment.comment_id]?.trim() || !replyContent[comment.comment_id]?.trim() || saving" @click="submitReply(comment.comment_id)">등록</button>
            </div>
          </div>
        </template>
      </article>
    </div>
  </section>
</template>