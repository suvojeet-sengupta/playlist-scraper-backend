/**
 * Standardised API response envelope.
 *
 * Every response from the gateway is wrapped in this structure so that
 * clients can always expect a consistent shape.
 */
export class ApiResponseDto<T = unknown> {
  success!: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: unknown;
  };
  metadata!: {
    timestamp: string;
    version: string;
    requestId?: string;
  };

  /** Factory for successful responses. */
  static success<T>(data: T, requestId?: string): ApiResponseDto<T> {
    const dto = new ApiResponseDto<T>();
    dto.success = true;
    dto.data = data;
    dto.metadata = {
      timestamp: new Date().toISOString(),
      version: '1.0.0',
      requestId,
    };
    return dto;
  }

  /** Factory for error responses. */
  static error(
    code: string,
    message: string,
    details?: unknown,
    requestId?: string,
  ): ApiResponseDto<never> {
    const dto = new ApiResponseDto<never>();
    dto.success = false;
    dto.error = { code, message, details };
    dto.metadata = {
      timestamp: new Date().toISOString(),
      version: '1.0.0',
      requestId,
    };
    return dto;
  }
}
