export interface ApiRequest<TBody> {
  body: TBody;
  headers: Record<string, string>;
  log: {
    info: (data: Record<string, unknown>, msg: string) => void;
    warn: (data: Record<string, unknown>, msg: string) => void;
    error: (data: Record<string, unknown>, msg: string) => void;
  };
}

export interface ApiResponse<TOut> {
  status: number;
  body: TOut;
}
