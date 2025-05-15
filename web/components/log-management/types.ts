export interface LogEntry {
  id: number
  operator_module: string
  operator_type: string
  person_name: string
  describes: string
  create_time: string
  state: string
}

export interface GetLogsParams {
  module?: string
  name?: string
  type?: string[] // 注意：这在URL中是数组
  people?: string
  begin_time?: string
  end_time?: string
  page?: string
  num?: string
}

export type GetLogsResponse = LogEntry[]

export interface DeleteLogResponse {
  code: number
  message: string
}

// ✅ 如果你真的需要 CreateLogResponse：
export interface CreateLogResponse extends LogEntry {
  created: boolean
}
