import { ref } from 'vue'

// 게시글 상세 화면에서 확인한 비밀번호를 수정 화면으로 잠시 전달하기 위한 모듈 스코프 상태.
// URL에 노출하지 않기 위해 컴포넌트 간 공유 ref로 처리한다.
const pendingPassword = ref('')

export function usePostAuth() {
  return { pendingPassword }
}
