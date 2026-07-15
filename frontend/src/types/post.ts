export interface Post {
  id: number
  title: string
  content: string
  author: string
}

export interface PostCreatePayload {
  title: string
  content: string
  author?: string
  password: string
}
